#!/usr/bin/env python3
"""Rodada automática da revisão de PRs, para rodar no cron sem ninguém acompanhando.

Uso (crontab, em horário comercial; `flock` impede duas rodadas ao mesmo tempo):
  */30 8-19 * * 1-5 . ~/revisor/env && flock -n /tmp/revisor.lock python3 <skill>/scripts/cron.py >> ~/revisor/cron.log 2>&1
  */2  8-19 * * 1-5 . ~/revisor/env && flock -n /tmp/revisor.lock python3 <skill>/scripts/cron.py --urgente >> ~/revisor/cron.log 2>&1

`--so PR` restringe a rodada a um PR.

`--rever PR[,PR...]` refaz a revisão desses PRs mesmo que já tenham aprovação (à mão, quando a régua
mudou). A aprovação de outro usuário não dá para retirar: se a revisão achar problema, o request
changes que sai no fim pesa mais que ela.

`--urgente` é a via rápida: olha só os PRs que têm a conta do agente ($REVISOR_REVISOR) entre os
revisores. O dev pede urgência adicionando essa conta como revisor do PR. Sem PR a revisar, sai
sem fetch, sem chamar o Claude e sem escrever no log.

O que faz:
  1. `git fetch` no clone e `bitbucket.py list --dest <destino>`. Sem PR marcado REVISAR, sai sem
     chamar o Claude. PR a revisar que conflita com o destino atual não é revisado (o código que vai
     entrar ainda não existe): com o corretor na esteira, vai à fila dele, que traz o destino para a
     branch e resolve o conflito (o que exige decisão volta ao dev pelo revisor); sem corretor, recebe
     request changes pedindo a atualização da branch.
  2. Chama `claude -p` com a skill sobre os PRs a revisar (no máximo $REVISOR_MAX por rodada).
  3. Lista de novo. PR que entrou na rodada e continua REVISAR no mesmo commit ficou sem veredito
     (inconclusivo, erro ao aplicar, rodada cortada): conta uma tentativa.
  3b. Com o validador na esteira (REVISOR_VALIDADOR=1, em triagem): PR que passa não é aprovado no
     Bitbucket. Vai para a fila do validador ($REVISOR_DIR/trabalho/validacao-fila/<pr>/) e a rodada o
     chama na hora ($REVISOR_VALIDAR --pr <pr>) e espera: provado, ele aprova, faz o merge e posta o
     comentário final na voz do revisor. O corretor faz o mesmo quando a correção dele é aprovada.
  3c. PR que o validador devolveu ($REVISOR_DIR/trabalho/validacao/<pr>/: a prova não fechou) é
     reavaliado em seguida, na mesma execução (--so), ou na rodada seguinte se veio do cron do validador, sem a aprovação do próprio revisor, com a evidência no pedido. Quem fala com o dev
     é o revisor: achado vai ao corretor (ou direto ao dev, se a validação já falhou depois do corretor);
     revisão mantida mesmo com a evidência vira aprovação com nota de merge manual.
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
ONLY = sys.argv[sys.argv.index("--so") + 1] if "--so" in sys.argv[1:-1] else None
REDO = sys.argv[sys.argv.index("--rever") + 1].split(",") if "--rever" in sys.argv[1:-1] else []
REVIEWER = os.environ.get("REVISOR_REVISOR")
TRIAGE = bool(os.environ.get("CORRETOR_CLAUDE"))
WORK = DIR / "trabalho" / "correcao"
FLAGS = DIR / "trabalho" / "validacao"
# com o validador na esteira, PR que passa na triagem não é aprovado no Bitbucket: vai para esta fila,
# e quem aprova e faz o merge é o validador, depois de provar
HANDOFF = TRIAGE and os.environ.get("REVISOR_VALIDADOR") == "1"
VQUEUE = DIR / "trabalho" / "validacao-fila"
PROVEN = DIR / "trabalho" / "validacao-provada"  # PR aprovado à mão que o validador já provou: falta o veredito do revisor

PROMPT = ("/revisar-pr-bitbucket Rodada automática, sem ninguém acompanhando: não pergunte nada. "
          "Revise como lista (valem REVISAR/PULAR; nunca use --isolado) os PRs {prs} e aplique o "
          "resultado no Bitbucket. Escreva o relatório final em português.")
PROMPT_TRIAGE = ("/revisar-pr-bitbucket Rodada automática, sem ninguém acompanhando: não pergunte nada. "
                 "Modo triagem. Revise como lista (valem REVISAR/PULAR; nunca use --isolado) os PRs {prs}. "
                 "{passed} para os que tiverem achado, não escreva no Bitbucket: grave "
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
    if "comment" in d["values"][0] and ((d["values"][0]["comment"].get("user") or {}).get("display_name") in bitbucket.SILENT):
        return False  # o retorno do validador não é novidade para a revisão
    last = next(v for k, v in d["values"][0].items() if isinstance(v, dict) and ("date" in v or "created_on" in v))
    return datetime.datetime.fromisoformat(last.get("date") or last["created_on"]) > datetime.datetime.fromisoformat(since)


def in_validation(base, pr, commit):
    """O PR passou na revisão e está com o validador, no mesmo commit e sem atividade nova desde então?
    Marca velha (o PR mudou) é arquivada: o PR volta para a revisão."""
    mark = VQUEUE / pr / "marca.json"
    if not mark.exists():
        return False
    m = json.loads(mark.read_text())
    if m["commit"][:12] == commit[:12] and not changed_since(base, pr, m["desde"]):
        return True
    dest = VQUEUE / "feitos" / f"{datetime.datetime.now():%Y%m%d-%H%M}-{pr}-mudou"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(VQUEUE / pr), str(dest))
    return False


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


def proven(base, before):
    """PRs aprovados à mão que o validador provou, no commit em que estão: entram na rodada para o veredito
    do revisor (a aprovação de quem aprovou fica; se a revisão achar problema, o request changes pesa mais)."""
    found = []
    for d in sorted(PROVEN.iterdir()) if PROVEN.is_dir() else []:
        if not (d.name.isdigit() and (d / "marca.json").exists()):
            continue
        st, info = bitbucket.call("GET", f"{base}/{d.name}", params={"fields": "state,source.commit.hash"})
        if st != 200 or info["state"] != "OPEN" or json.loads((d / "marca.json").read_text())["commit"][:12] != info["source"]["commit"]["hash"][:12]:
            shutil.rmtree(d, ignore_errors=True)
            continue
        before.setdefault(d.name, info["source"]["commit"]["hash"][:12])
        found.append(d.name)
    return found


def validator(pr):
    """Chama o validador neste PR e espera (a rodada segura o lock do revisor enquanto isso). Sem o comando
    configurado, o PR fica na fila e o cron do validador o encontra."""
    cmd = os.environ.get("REVISOR_VALIDAR")
    if not cmd:
        return log(f"#{pr}: na fila do validador (REVISOR_VALIDAR ausente: fica para o cron dele)")
    log(f"#{pr}: validador chamado; aguardando")
    subprocess.run(["flock", "/tmp/testador-prova.lock", "bash", "-c", f"{cmd} --pr {shlex.quote(pr)} --chamado >> \"$HOME/testador/cron.log\" 2>&1"],
                   cwd=CLONE, stdin=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k != "CORRETOR_BITBUCKET_TOKEN"})
    log(f"#{pr}: validador terminou: " + subprocess.run(["bash", "-c", f"grep '#{pr}:' \"$HOME/testador/cron.log\" | tail -1 | cut -c18-200"],
                                                        capture_output=True, text=True).stdout.strip())


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


def unflag(pr, why):
    dest = FLAGS / "feitos" / f"{datetime.datetime.now():%Y%m%d-%H%M}-{pr}-{why}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(FLAGS / pr), str(dest))


def flagged(base, before):
    """O PR da rodada (--so), se o validador deixou evidência para o commit em que ele está: entra em
    `before`, sem a aprovação do próprio revisor (a de outra pessoa não dá para retirar; entra assim mesmo)."""
    found = []
    for d in sorted(FLAGS.iterdir()) if FLAGS.is_dir() else []:
        if ONLY and d.name != ONLY:
            continue
        if not (d.name.isdigit() and (d / "marca.json").exists() and (d / "evidencia.md").exists()):
            continue
        st, info = bitbucket.call("GET", f"{base}/{d.name}", params={"fields": "state,source.commit.hash"})
        commit = info["source"]["commit"]["hash"][:12] if st == 200 else ""
        if st != 200 or info["state"] != "OPEN" or json.loads((d / "marca.json").read_text())["commit"][:12] != commit:
            unflag(d.name, "mudou")
            continue
        if d.name not in before:
            bitbucket.call("DELETE", f"{base}/{d.name}/approve")
            bitbucket.forget(f"{base}/{d.name}")
            before[d.name] = commit
        found.append(d.name)
    return found


def conflicts(commit):
    """Arquivos em que o PR conflita com o destino atual (lista vazia: entra limpo)."""
    r = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", "--no-messages", f"origin/{DEST}", commit],
                       cwd=CLONE, capture_output=True, text=True)
    return r.stdout.splitlines()[1:] if r.returncode == 1 else []


def hold(pr, files, commit, quiet=False):
    """PR em conflito com o destino, sem chamar o Claude. Devolve se segurou. Com o corretor na esteira,
    o conflito vai à fila dele como achado; sem ele, comentário + request changes.
    `quiet`: só o request changes (rodada acionada pelo validador, que é quem comenta)."""
    if not files:
        return False
    if TRIAGE:
        (WORK / pr).mkdir(parents=True, exist_ok=True)
        (WORK / pr / "achados.md").write_text(
            f"## PR (#{pr})\n❌ **O PR conflita com a `{DEST}` atual.** O conflito está em:\n" + "\n".join(f"- `{f}`" for f in files)
            + f"\n\nA `{DEST}` já foi trazida para a sua cópia e o merge parou no conflito. Resolva mantendo o que o PR faz "
            f"e o que entrou na `{DEST}`. Se as duas mudanças disputam a mesma regra e não dá para manter as duas, é DECISÃO.\n")
        (WORK / pr / "marca.json").write_text(json.dumps({"commit": commit, "conflito": True,
                                                          "desde": datetime.datetime.now(datetime.timezone.utc).isoformat()}))
        log(f"#{pr}: conflita com a {DEST} ({len(files)} arquivo(s)); para o corretor resolver")
        return True
    text = DIR / "rodadas" / f"conflito-{pr}.md"
    text.write_text(f"## PR (#{pr})\n⚠️ **O PR conflita com a `{DEST}` atual; não revisei.** O conflito está em:\n"
                    + "\n".join(f"- `{f}`" for f in files)
                    + f"\n\nAtualize a branch em cima da `{DEST}` e resolva o conflito. A revisão vale para o código que vai "
                    "entrar, e com conflito ele ainda não existe. Com o commit novo, o PR volta para a revisão.\n")
    for cmd, arg in (("comment", str(text)), ("request-changes", pr))[quiet:]:
        r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), cmd, arg], cwd=CLONE, capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip().endswith("ok"):
            log(f"#{pr}: conflita com a {DEST}, mas {cmd} falhou ({(r.stdout + r.stderr).strip()[:160]}); segue para a revisão")
            return False
    log(f"#{pr}: conflita com a {DEST} ({len(files)} arquivo(s)); request changes pedindo a atualização da branch")
    return True


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
    base = f"{bitbucket.resolve_repo(None)}/pullrequests"
    flags = [] if URGENT else flagged(base, before)
    vetted = [] if URGENT or not HANDOFF else proven(base, before)
    if ONLY:
        before = {pr: commit for pr, commit in before.items() if pr == ONLY}
    for pr in REDO:
        st, info = bitbucket.call("GET", f"{base}/{pr}", params={"fields": "state,source.commit.hash"})
        if pr not in before and st == 200 and info["state"] == "OPEN":
            before[pr] = info["source"]["commit"]["hash"][:12]
    if REDO:
        before = {pr: commit for pr, commit in before.items() if pr in REDO}
    forced = set(flags) | set(REDO) | set(vetted)  # entram na rodada mesmo sem estar no REVISAR
    # a contagem vale enquanto o PR está como na última tentativa: commit ou atividade nova zera;
    # PR que saiu da lista some do estado (na via rápida a lista é parcial: o que não está nela fica)
    state = {pr: s for pr, s in state.items()
             if ((URGENT or ONLY or REDO) and pr not in before)
             or (before.get(pr) == s["commit"] and not changed_since(base, pr, s["desde"]))}
    blocked = [pr for pr in before if state.get(pr, {}).get("tentativas", 0) >= TENTATIVAS]
    waiting = [pr for pr in before if TRIAGE and pr not in blocked and pr not in flags and pr not in vetted
               and (in_correction(base, pr, before[pr]) or HANDOFF and in_validation(base, pr, before[pr]))]
    for pr in [pr for pr in before if pr not in blocked and pr not in waiting]:
        if not URGENT and hold(pr, conflicts(before[pr]), before[pr]):
            del before[pr]
            if pr in flags:
                unflag(pr, "conflito")
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
    passed = (f"Para os que passarem, também não escreva no Bitbucket: grave {VQUEUE}/<número do PR>/aprovado.md com o "
              "veredito ✅ e, em uma ou duas linhas, o que o PR corrige — quem aprova e faz o merge é o validador, depois de "
              "provar;" if HANDOFF else "Aprove os que passarem;")
    prompt = (PROMPT_TRIAGE if TRIAGE else PROMPT).format(prs=", ".join("#" + pr for pr in todo), work=WORK, passed=passed)
    back = [pr for pr in todo if pr in flags]
    manual = [pr for pr in todo if pr in vetted]
    if manual:
        prompt += (f" {', '.join('#' + pr for pr in manual)} foram aprovados à mão por alguém e o validador já provou rodando "
                   f"(o que ele provou está em {PROVEN}/<número do PR>/validacao.md). A aprovação dessa pessoa não é o seu "
                   "veredito: revise do zero e decida você, com a prova como mais uma evidência.")
    again = []
    if forced & set(todo):
        prompt += (f" Os PRs {', '.join('#' + pr for pr in todo if pr in forced)} entram nesta rodada mesmo que a listagem os marque "
                   "PULAR por aprovação: a aprovação está sendo refeita. Revise-os do zero, pela régua atual.")
    if back:
        prompt += (f" Atenção a {', '.join('#' + pr for pr in back)}: já tinha passado na sua revisão, mas o validador rodou a "
                   f"prova depois e ela não fechou. A evidência está em {FLAGS}/<número do PR>/evidencia.md: leia antes de julgar, "
                   "porque ela mostra o que a revisão não viu.")
        again = [pr for pr in back if json.loads((FLAGS / pr / "marca.json").read_text()).get("falhas", 1) >= 2]
        if again:
            prompt += (f" Em {', '.join('#' + pr for pr in again)} a validação já falhou mais de uma vez, inclusive depois do "
                       "corretor: se houver achado, não mande ao corretor — escreva o achado para o dev (no achados.md, como "
                       "sempre) dizendo que a correção automática já foi tentada.")
    with open(out, "w") as fh:
        try:
            r = subprocess.run([*CLAUDE, "-p", prompt], cwd=CLONE, stdout=fh, stderr=subprocess.STDOUT, timeout=TIMEOUT,
                               env={k: v for k, v in os.environ.items() if k not in ("CORRETOR_BITBUCKET_TOKEN", "YOUTRACK_WRITE_TOKEN")})
            end = f"claude saiu com {r.returncode}"
        except subprocess.TimeoutExpired:
            end = f"cortada aos {TIMEOUT // 60} min"
        except FileNotFoundError:
            warn(f"comando do Claude não encontrado: {CLAUDE[0]}")
            sys.exit(1)

    subprocess.run(["git", "fetch", "origin", "--prune", "-q"], cwd=CLONE, capture_output=True)
    after = to_review()
    since = datetime.datetime.now(datetime.timezone.utc).isoformat()
    done = sent = handed = 0
    validate = []
    for pr in todo:
        found = WORK / pr / "achados.md"
        fresh = TRIAGE and found.exists() and found.stat().st_mtime >= started  # a triagem achou problema
        verdict = VQUEUE / pr / "aprovado.md"
        to_validator = HANDOFF and not fresh and verdict.exists() and verdict.stat().st_mtime >= started  # passou
        if pr in manual and not to_validator:
            shutil.rmtree(PROVEN / pr, ignore_errors=True)  # sem o aval do revisor, a prova guardada não serve mais
        # PR forçado pode nunca ter estado no REVISAR (a aprovação de outro usuário continua lá): o veredito vale assim mesmo
        if after.get(pr) != before[pr] and not ((fresh or to_validator) and pr in forced and pr not in after):  # saiu do REVISAR, ou recebeu commit durante a rodada
            done += pr not in after
            state.pop(pr, None)
            if pr in back and pr not in after:
                unflag(pr, "revisado")
            continue
        if fresh and pr in again:  # a correção automática já foi tentada: o achado vai direto ao dev
            for cmd, arg in (("comment", str(found)), ("request-changes", pr)):
                r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), cmd, arg, "--isolado"], cwd=CLONE, capture_output=True, text=True)
                if not r.stdout.strip().endswith("ok"):
                    log(f"#{pr}: {cmd} FALHOU ({(r.stdout + r.stderr).strip()[:160]})")
            log(f"#{pr}: validação falhou de novo depois do corretor; achado e request changes direto para o dev")
            (WORK / "feitos").mkdir(parents=True, exist_ok=True)
            shutil.move(str(WORK / pr), str(WORK / "feitos" / f"{datetime.datetime.now():%Y%m%d-%H%M}-{pr}-dev"))
            unflag(pr, "dev")
            state.pop(pr, None)
            continue
        if fresh:  # vai ao corretor
            shutil.rmtree(VQUEUE / pr, ignore_errors=True)  # aprovação de uma rodada anterior não vale mais
            (WORK / pr / "marca.json").write_text(json.dumps({"commit": before[pr], "desde": since}))
            sent += 1
            state.pop(pr, None)
            if pr in back:
                unflag(pr, "corretor")
            continue
        if to_validator and pr in back:  # passou de novo, mesmo com a evidência: aprova, e o merge fica com uma pessoa
            for cmd, arg in (("comment", str(FLAGS / pr / "nota.md")), ("approve", pr)):
                r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), cmd, arg, "--isolado"], cwd=CLONE, capture_output=True, text=True)
                if not r.stdout.strip().endswith("ok"):
                    log(f"#{pr}: {cmd} FALHOU ({(r.stdout + r.stderr).strip()[:160]})")
            log(f"#{pr}: revisão mantida mesmo com a evidência do validador; aprovado, com nota de merge manual")
            shutil.rmtree(VQUEUE / pr, ignore_errors=True)
            unflag(pr, "mantido")
            state.pop(pr, None)
            continue
        if to_validator:  # sem aprovação no Bitbucket: o validador prova, aprova e faz o merge
            (VQUEUE / pr / "marca.json").write_text(json.dumps({"commit": before[pr], "desde": since}))
            handed += 1
            validate.append(pr)
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
        + (f", {handed} para o validador" if HANDOFF else "")
        + f"; saída em {out}")
    wake()
    for pr in validate:
        validator(pr)
        if (FLAGS / pr / "marca.json").exists():  # a prova não fechou: reavalia já, com a evidência, sem esperar o cron
            log(f"#{pr}: o validador devolveu; reavaliando agora com a evidência")
            subprocess.run([sys.executable, __file__, "--so", pr], cwd=CLONE, stdin=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
