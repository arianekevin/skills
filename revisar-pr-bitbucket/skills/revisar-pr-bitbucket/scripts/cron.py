#!/usr/bin/env python3
"""Rodada automática da revisão de PRs, para rodar no cron sem ninguém acompanhando.

Uso (crontab, em horário comercial; `flock` impede duas rodadas ao mesmo tempo):
  */30 8-19 * * 1-5 . ~/revisor/env && flock -n /tmp/revisor.lock python3 <skill>/scripts/cron.py >> ~/revisor/cron.log 2>&1
  */2  8-19 * * 1-5 . ~/revisor/env && flock -n /tmp/revisor.lock python3 <skill>/scripts/cron.py --urgente >> ~/revisor/cron.log 2>&1

`--urgente` é a via rápida: olha só os PRs que têm a conta do agente ($REVISOR_REVISOR) entre os
revisores. O dev pede urgência adicionando essa conta como revisor do PR. Sem PR a revisar, sai
sem fetch, sem chamar o Claude e sem escrever no log.

O que faz:
  1. `git fetch` no clone e `bitbucket.py list --dest <destino>`. Sem PR marcado REVISAR, sai sem
     chamar o Claude.
  2. Chama `claude -p` com a skill sobre os PRs a revisar (no máximo $REVISOR_MAX por rodada).
  3. Lista de novo. PR que entrou na rodada e continua REVISAR no mesmo commit ficou sem veredito
     (inconclusivo, erro ao aplicar, rodada cortada): conta uma tentativa.
  4. Na tentativa $REVISOR_TENTATIVAS o PR sai das rodadas e um aviso é emitido. Qualquer novidade
     no PR depois da última tentativa zera a contagem: commit, comentário, mudança de estado
     (saiu do draft, marca removida, título ou descrição editados).

Ambiente (além das credenciais que a skill pede):
  REVISOR_CLONE       clone do repo dos PRs (obrigatório)
  REVISOR_DEST        branch de destino (padrão: alpha)
  REVISOR_DIR         onde ficam estado, avisos e logs das rodadas (padrão: ~/revisor)
  REVISOR_MAX         PRs por rodada (padrão: 10)
  REVISOR_TENTATIVAS  tentativas sem veredito no mesmo commit antes de desistir (padrão: 3)
  REVISOR_TIMEOUT     minutos até cortar a rodada (padrão: 50)
  REVISOR_CLAUDE      comando do Claude Code (padrão: claude)
  REVISOR_REVISOR     nome da conta do agente no Bitbucket, como aparece em "Reviewers"
                      (obrigatório com --urgente)
  REVISOR_AVISAR      comando que recebe o aviso como último argumento (ex.: um script que manda
                      para o chat). Sem ele, o aviso fica só em $REVISOR_DIR/avisos.log.
  CORRETOR_CLAUDE     se definido, a rodada é de triagem: PR aprovado é aprovado, e PR com achado
                      não recebe comentário — os achados vão para a fila do corretor
                      ($REVISOR_DIR/trabalho/correcao/<pr>/), que `corrigir.py` consome. PR na fila
                      fica fora das rodadas até a correção terminar ou o PR mudar. O corretor não
                      tem cron: esta rodada o dispara assim que termina, se houver PR na fila e
                      nenhum corretor rodando (saída dele em $REVISOR_DIR/corretor.log).
"""
import datetime, fcntl, json, os, pathlib, shlex, shutil, subprocess, sys

import bitbucket

HERE = pathlib.Path(__file__).resolve().parent
CLONE = os.environ.get("REVISOR_CLONE")
DEST = os.environ.get("REVISOR_DEST", "alpha")
DIR = pathlib.Path(os.environ.get("REVISOR_DIR", "~/revisor")).expanduser()
MAX = int(os.environ.get("REVISOR_MAX", "10"))
TENTATIVAS = int(os.environ.get("REVISOR_TENTATIVAS", "3"))
TIMEOUT = int(os.environ.get("REVISOR_TIMEOUT", "50")) * 60
CLAUDE = shlex.split(os.environ.get("REVISOR_CLAUDE", "claude"))
STATE = DIR / "estado.json"
URGENT = "--urgente" in sys.argv[1:]
REVIEWER = os.environ.get("REVISOR_REVISOR")
TRIAGE = bool(os.environ.get("CORRETOR_CLAUDE"))
WORK = DIR / "trabalho" / "correcao"

PROMPT = ("/revisar-pr-bitbucket Rodada automática, sem ninguém acompanhando: não pergunte nada. "
          "Revise como lista (valem REVISAR/PULAR; nunca use --isolado) os PRs {prs} e aplique o "
          "resultado no Bitbucket. Escreva o relatório final em português.")
PROMPT_TRIAGE = ("/revisar-pr-bitbucket Rodada automática, sem ninguém acompanhando: não pergunte nada. "
                 "Modo triagem. Revise como lista (valem REVISAR/PULAR; nunca use --isolado) os PRs {prs}. "
                 "Aprove os que passarem; para os que tiverem achado, não escreva no Bitbucket: grave "
                 "{work}/<número do PR>/achados.md. Baixe os tickets em {work}/issues. "
                 "Escreva o relatório final em português.")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def log(msg):
    print(now(), msg, flush=True)


def warn(msg):
    log(f"AVISO {msg}")
    with open(DIR / "avisos.log", "a") as f:
        f.write(f"{now()} {msg}\n")
    cmd = os.environ.get("REVISOR_AVISAR")
    if cmd:
        r = subprocess.run([*shlex.split(cmd), msg], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"REVISOR_AVISAR falhou ({r.returncode}): {r.stderr.strip()[:200]}")


def changed_since(base, pr, since):
    """Houve atividade no PR depois de `since` (fim da última tentativa)? As escritas da própria
    rodada acontecem antes de `since`, então o que vem depois é de outra pessoa ou de outra sessão."""
    st, d = bitbucket.call("GET", f"{base}/{pr}/activity", params={"pagelen": 1})
    if st != 200 or not d.get("values"):
        return False
    last = next(v for k, v in d["values"][0].items() if isinstance(v, dict) and ("date" in v or "created_on" in v))
    return datetime.datetime.fromisoformat(last.get("date") or last["created_on"]) > datetime.datetime.fromisoformat(since)


def in_correction(base, pr, commit):
    """O PR está na fila do corretor, no mesmo commit e sem atividade nova desde a triagem?
    Marca velha (o PR mudou) é arquivada: a triagem recomeça."""
    mark = WORK / pr / "marca.json"
    if not mark.exists():
        return False
    m = json.loads(mark.read_text())
    if m["commit"] == commit and not changed_since(base, pr, m["desde"]):
        return True
    dest = WORK / "feitos" / f"{datetime.datetime.now():%Y%m%d-%H%M}-{pr}-mudou"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(WORK / pr), str(dest))
    return False


def wake():
    """Gatilho do corretor: com PR na fila e nenhum corretor rodando, sobe um, solto desta rodada.
    Se já há um rodando, ele mesmo esvazia a fila."""
    if not (TRIAGE and WORK.is_dir() and any((d / "marca.json").exists() for d in WORK.iterdir() if d.name.isdigit())):
        return
    with open(DIR / "corretor.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
    with open(DIR / "corretor.log", "a") as out:
        subprocess.Popen([sys.executable, str(HERE / "corrigir.py")], cwd=CLONE, stdin=subprocess.DEVNULL,
                         stdout=out, stderr=subprocess.STDOUT, start_new_session=True)


def to_review():
    """PRs que `bitbucket.py list` marca REVISAR: {pr: commit atual da branch de origem}."""
    r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), "list", "--dest", DEST,
                        *(["--reviewer", REVIEWER] if URGENT else [])],
                       cwd=CLONE, capture_output=True, text=True)
    if r.returncode != 0:
        warn(f"listagem falhou: {(r.stderr or r.stdout).strip()[:300]}")
        sys.exit(1)
    prs = {}
    for line in r.stdout.splitlines():
        parts = line.split(" | ", 4)
        if len(parts) == 5 and parts[3].startswith("REVISAR"):
            branch = parts[1].split(" -> ")[0]
            h = subprocess.run(["git", "rev-parse", "--short=12", f"origin/{branch}"],
                               cwd=CLONE, capture_output=True, text=True)
            prs[parts[0]] = h.stdout.strip() if h.returncode == 0 else "?"
    return prs


def main():
    if not CLONE:
        sys.exit("REVISOR_CLONE ausente: aponte para o clone do repo dos PRs")
    if URGENT and not REVIEWER:
        sys.exit("REVISOR_REVISOR ausente: --urgente precisa do nome da conta do agente no Bitbucket")
    os.chdir(CLONE)
    if URGENT and not to_review():  # a cada 2 min: sem pedido de urgência, sai antes do fetch
        return
    (DIR / "rodadas").mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}

    f = subprocess.run(["git", "fetch", "origin", "--prune", "-q"], cwd=CLONE, capture_output=True, text=True)
    if f.returncode != 0:
        warn(f"git fetch falhou: {f.stderr.strip()[:300]}")
        sys.exit(1)

    before = to_review()
    # a contagem vale enquanto o PR está como na última tentativa: commit ou atividade nova zera;
    # PR que saiu da lista some do estado (na via rápida a lista é parcial: o que não está nela fica)
    base = f"{bitbucket.resolve_repo(None)}/pullrequests"
    state = {pr: s for pr, s in state.items()
             if (URGENT and pr not in before)
             or (before.get(pr) == s["commit"] and not changed_since(base, pr, s["desde"]))}
    blocked = [pr for pr in before if state.get(pr, {}).get("tentativas", 0) >= TENTATIVAS]
    waiting = [pr for pr in before if TRIAGE and pr not in blocked and in_correction(base, pr, before[pr])]
    todo = [pr for pr in before if pr not in blocked and pr not in waiting][:MAX]
    if not todo:
        STATE.write_text(json.dumps(state, indent=1))
        if not URGENT:
            log(f"nada a revisar ({len(blocked)} fora das rodadas por falta de veredito"
                + (f", {len(waiting)} na fila do corretor)" if TRIAGE else ")"))
        wake()
        return

    log(f"rodada{' urgente' if URGENT else ''}: {', '.join('#' + pr for pr in todo)}"
        + (f" ({len(before) - len(blocked) - len(waiting) - len(todo)} ficam para a próxima)"
           if len(before) - len(blocked) - len(waiting) > len(todo) else ""))
    out = DIR / "rodadas" / f"{datetime.datetime.now():%Y%m%d-%H%M}.log"
    started = datetime.datetime.now().timestamp()
    prompt = (PROMPT_TRIAGE if TRIAGE else PROMPT).format(prs=", ".join("#" + pr for pr in todo), work=WORK)
    with open(out, "w") as fh:
        try:
            r = subprocess.run([*CLAUDE, "-p", prompt], cwd=CLONE, stdout=fh, stderr=subprocess.STDOUT, timeout=TIMEOUT,
                               env={k: v for k, v in os.environ.items() if k != "CORRETOR_BITBUCKET_TOKEN"})
            end = f"claude saiu com {r.returncode}"
        except subprocess.TimeoutExpired:
            end = f"cortada aos {TIMEOUT // 60} min"
        except FileNotFoundError:
            warn(f"comando do Claude não encontrado: {CLAUDE[0]}")
            sys.exit(1)

    subprocess.run(["git", "fetch", "origin", "--prune", "-q"], cwd=CLONE, capture_output=True)
    after = to_review()
    since = datetime.datetime.now(datetime.timezone.utc).isoformat()
    done = sent = 0
    for pr in todo:
        if after.get(pr) != before[pr]:  # saiu do REVISAR, ou recebeu commit durante a rodada
            done += pr not in after
            state.pop(pr, None)
            continue
        found = WORK / pr / "achados.md"
        if TRIAGE and found.exists() and found.stat().st_mtime >= started:  # triagem achou problema: vai ao corretor
            (WORK / pr / "marca.json").write_text(json.dumps({"commit": before[pr], "desde": since}))
            sent += 1
            state.pop(pr, None)
            continue
        n = state.get(pr, {}).get("tentativas", 0) + 1
        state[pr] = {"commit": before[pr], "tentativas": n, "desde": since}
        if n >= TENTATIVAS:
            warn(f"PR #{pr}: {n} rodadas sem veredito no commit {before[pr]}; fora das rodadas até commit, comentário "
                 f"ou mudança de estado. "
                 f"Última rodada: {out}")
    STATE.write_text(json.dumps(state, indent=1))
    log(f"fim ({end}): {done} de {len(todo)} saíram do REVISAR" + (f", {sent} para o corretor" if TRIAGE else "")
        + f"; saída em {out}")
    wake()


if __name__ == "__main__":
    main()
