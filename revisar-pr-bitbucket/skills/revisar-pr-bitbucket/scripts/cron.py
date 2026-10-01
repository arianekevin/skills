#!/usr/bin/env python3
"""Rodada automática da revisão de PRs, para rodar no cron sem ninguém acompanhando.

Uso (crontab, de hora em hora em horário comercial; `flock` impede duas rodadas ao mesmo tempo):
  0 8-19 * * 1-5 . ~/revisor/env && flock -n /tmp/revisor.lock python3 <skill>/scripts/cron.py >> ~/revisor/cron.log 2>&1

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
  REVISOR_AVISAR      comando que recebe o aviso como último argumento (ex.: um script que manda
                      para o chat). Sem ele, o aviso fica só em $REVISOR_DIR/avisos.log.
"""
import datetime, json, os, pathlib, shlex, subprocess, sys

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

PROMPT = ("/revisar-pr-bitbucket Rodada automática, sem ninguém acompanhando: não pergunte nada. "
          "Revise como lista (valem REVISAR/PULAR; nunca use --isolado) os PRs {prs} e aplique o "
          "resultado no Bitbucket.")


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


def to_review():
    """PRs que `bitbucket.py list` marca REVISAR: {pr: commit atual da branch de origem}."""
    r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), "list", "--dest", DEST],
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
    os.chdir(CLONE)
    (DIR / "rodadas").mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}

    f = subprocess.run(["git", "fetch", "origin", "--prune", "-q"], cwd=CLONE, capture_output=True, text=True)
    if f.returncode != 0:
        warn(f"git fetch falhou: {f.stderr.strip()[:300]}")
        sys.exit(1)

    before = to_review()
    # a contagem vale enquanto o PR está como na última tentativa: commit ou atividade nova zera;
    # PR que saiu da lista some do estado
    base = f"{bitbucket.resolve_repo(None)}/pullrequests"
    state = {pr: s for pr, s in state.items()
             if before.get(pr) == s["commit"] and not changed_since(base, pr, s["desde"])}
    blocked = [pr for pr in before if state.get(pr, {}).get("tentativas", 0) >= TENTATIVAS]
    todo = [pr for pr in before if pr not in blocked][:MAX]
    if not todo:
        STATE.write_text(json.dumps(state, indent=1))
        log(f"nada a revisar ({len(blocked)} fora das rodadas por falta de veredito)")
        return

    log(f"rodada: {', '.join('#' + pr for pr in todo)}"
        + (f" ({len(before) - len(blocked) - len(todo)} ficam para a próxima)" if len(before) - len(blocked) > len(todo) else ""))
    out = DIR / "rodadas" / f"{datetime.datetime.now():%Y%m%d-%H%M}.log"
    with open(out, "w") as fh:
        try:
            r = subprocess.run([*CLAUDE, "-p", PROMPT.format(prs=", ".join("#" + pr for pr in todo))],
                               cwd=CLONE, stdout=fh, stderr=subprocess.STDOUT, timeout=TIMEOUT)
            end = f"claude saiu com {r.returncode}"
        except subprocess.TimeoutExpired:
            end = f"cortada aos {TIMEOUT // 60} min"
        except FileNotFoundError:
            warn(f"comando do Claude não encontrado: {CLAUDE[0]}")
            sys.exit(1)

    subprocess.run(["git", "fetch", "origin", "--prune", "-q"], cwd=CLONE, capture_output=True)
    after = to_review()
    since = datetime.datetime.now(datetime.timezone.utc).isoformat()
    done = 0
    for pr in todo:
        if after.get(pr) != before[pr]:  # saiu do REVISAR, ou recebeu commit durante a rodada
            done += pr not in after
            state.pop(pr, None)
            continue
        n = state.get(pr, {}).get("tentativas", 0) + 1
        state[pr] = {"commit": before[pr], "tentativas": n, "desde": since}
        if n >= TENTATIVAS:
            warn(f"PR #{pr}: {n} rodadas sem veredito no commit {before[pr]}; fora das rodadas até commit, comentário "
                 f"ou mudança de estado. "
                 f"Última rodada: {out}")
    STATE.write_text(json.dumps(state, indent=1))
    log(f"fim ({end}): {done} de {len(todo)} com veredito aplicado; saída em {out}")


if __name__ == "__main__":
    main()
