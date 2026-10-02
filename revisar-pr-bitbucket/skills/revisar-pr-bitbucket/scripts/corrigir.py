#!/usr/bin/env python3
"""Esteira de correção: leva ao corretor os PRs que a triagem do revisor deixou com achado.

Não tem cron: a rodada de triagem (`cron.py`) dispara este script assim que termina, se deixou PR
na fila. Sem argumento ele esvazia a fila, um PR por vez, e sai. Um lock próprio
($REVISOR_DIR/corretor.lock) garante um corretor só de cada vez, sem disputar com as rodadas de revisão.

À mão:
  corrigir.py --pr 123            só este PR (precisa estar na fila)
  corrigir.py --reabrir 123       PR que já recebeu request changes: monta a fila a partir dos
                                  comentários do PR e roda
  corrigir.py ... --ensaio        faz as voltas e mostra o que publicaria; não dá push nem escreve
                                  no Bitbucket, e deixa a cópia da branch para conferir
                                  (o PR sai da fila ao fim do ensaio)

O que faz, por PR na fila ($REVISOR_DIR/trabalho/correcao/<pr>/ com achados.md e marca.json,
deixados pela triagem — `cron.py` com $CORRETOR_CLAUDE definido):
  1. Cria uma cópia da branch (git worktree) em $CORRETOR_DIR/pr-<pr>.
  2. Até $CORRETOR_VOLTAS voltas: o corretor (skill corrigir-pr) mexe na cópia e responde achado
     por achado; o revisor, em modo portão, confere a mudança e a resposta e dá o veredito.
  3. Publica conforme o veredito:
     aprovado  commit + push + comentário do que foi corrigido + aprovação (sem mudança: só aprova)
               o comentário lista também o que ficou de fora sem bloquear
     parcial   commit + push + comentário (o corrigido e o que ficou para o dev) + request changes
     sem acordo ao fim das voltas: descarta a mudança; comentário com os achados + request changes
  O commit vai em cima da branch, sem force-push. Se a branch andou no meio, nada é publicado e o
  PR volta para a triagem.

Ambiente (além do que cron.py já usa):
  CORRETOR_CLAUDE     comando do Claude Code do corretor, com as permissões dele (obrigatório)
  CORRETOR_DIR        onde ficam as cópias das branches (padrão: ~/corretor)
  CORRETOR_VOLTAS     voltas corretor/revisor por PR (padrão: 5)
  CORRETOR_MAX        PRs por execução (padrão: 10)
  CORRETOR_TIMEOUT    minutos até cortar cada sessão (padrão: 40)
  CORRETOR_VERIFICAR  comando de verificação que o corretor deve rodar na cópia (ex.: um script
                      que compila e roda os testes); entra no pedido
  CORRETOR_SUITE      comando que roda a suíte completa de testes na cópia e imprime, um por linha,
                      os testes que falharam; saída diferente de 0 = a suíte não rodou (não compilou).
                      Com ele, depois que o revisor aceita a mudança, a suíte roda onde o PR vai parar:
                      o destino atual com a branch e a mudança por cima, comparado com o destino sozinho
                      (se a branch conflita com o destino, a comparação é na própria branch).
                      Teste que passa sem o PR e falha com ele volta para o corretor como achado
                      (ele arruma o teste, se o teste fixava o comportamento que o ticket muda, ou
                      conserta a mudança), e sem resolver nada é publicado. Teste que já falhava no
                      destino não conta.
  CORRETOR_GIT_NAME, CORRETOR_GIT_EMAIL   autor do commit (obrigatórios para publicar)
  CORRETOR_BITBUCKET_TOKEN  access token do repositório só do corretor (Repositories: write; Pull
                      requests: write). Com ele o corretor tem identidade própria no Bitbucket: o push
                      e o comentário do que foi corrigido saem com o nome desse token, e a aprovação ou
                      o request changes continuam saindo com a credencial do revisor. O token não chega
                      a nenhuma sessão do Claude. Sem ele, o push usa o remoto do clone e tudo o que é
                      escrito no PR sai com a credencial do revisor.
"""
import argparse, datetime, fcntl, json, os, pathlib, re, shlex, shutil, subprocess, sys, time

import bitbucket

HERE = pathlib.Path(__file__).resolve().parent
CLONE = os.environ.get("REVISOR_CLONE")
DIR = pathlib.Path(os.environ.get("REVISOR_DIR", "~/revisor")).expanduser()
WORK = DIR / "trabalho" / "correcao"
TREES = pathlib.Path(os.environ.get("CORRETOR_DIR", "~/corretor")).expanduser()
REVISOR = shlex.split(os.environ.get("REVISOR_CLAUDE", "claude"))
CORRETOR = shlex.split(os.environ.get("CORRETOR_CLAUDE", ""))
VOLTAS = int(os.environ.get("CORRETOR_VOLTAS", "5"))
MAX = int(os.environ.get("CORRETOR_MAX", "10"))
TIMEOUT = int(os.environ.get("CORRETOR_TIMEOUT", "40")) * 60
VERIFY = os.environ.get("CORRETOR_VERIFICAR")
FIXER_TOKEN = os.environ.get("CORRETOR_BITBUCKET_TOKEN")
SUITE = os.environ.get("CORRETOR_SUITE")
TICKET = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
SECRET = re.compile(r"TOKEN|SECRET|PASSWORD|BITBUCKET_|YOUTRACK_|TEAMCITY_")

HEAD = "Rodada automática, sem ninguém acompanhando: não pergunte nada. "
ASK_FIX = ("/revisar-pr-bitbucket:corrigir-pr " + HEAD + "PR #{pr} ({branch} -> {dest}), volta {v} de {n}. O diretório atual é a sua "
           "cópia da branch. Achados: {work}/achados.md.{prev} Tickets (JSON): {issues}.{context}{verify} Escreva "
           "{work}/resposta.md e, se mudar código, {work}/commit.txt. Responda em português.")
ASK_GATE = ("/revisar-pr-bitbucket " + HEAD + "Modo portão, PR #{pr} ({branch} -> {dest}), volta {v} de {n}{last}. "
            "O diretório atual é a cópia da branch com a mudança do corretor sem commit. Pasta: {work} "
            "(achados.md e resposta.md). Tickets (JSON): {issues}.{context} Entregue {work}/veredito.json e regrave "
            "{work}/achados.md. Responda em português.")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def log(msg):
    print(now(), msg, flush=True)


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd or CLONE, capture_output=True, text=True)
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr).strip()


def session(cmd, prompt, cwd, env, out):
    """Uma sessão do Claude sem supervisão; a saída vai para `out`. Devolve como terminou."""
    with open(out, "w") as fh:
        try:
            r = subprocess.run([*cmd, "-p", prompt], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=fh, stderr=subprocess.STDOUT, timeout=TIMEOUT)
            return f"saiu com {r.returncode}"
        except subprocess.TimeoutExpired:
            return f"cortada aos {TIMEOUT // 60} min"


def suite(tree, out):
    """Roda a suíte completa na cópia. Devolve o conjunto dos testes que falharam, ou None se não rodou."""
    with open(out, "w") as err:
        try:
            r = subprocess.run(SUITE, shell=True, cwd=tree, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=err, text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return None
    return {line.strip() for line in r.stdout.splitlines() if line.strip()} if r.returncode == 0 else None


def scratch(name, ref):
    """Cópia descartável do repo em `ref`, ou None."""
    path = TREES / name
    git("worktree", "remove", "--force", str(path))
    return path if git("worktree", "add", "--detach", str(path), ref)[0] == 0 else None


def baseline(ref, logs):
    """Testes que já falham em `ref`. Guardado por commit: enquanto o destino não anda, não roda de novo."""
    cache = TREES / f"suite-{git('rev-parse', '--short=12', ref)[1]}.txt"
    if cache.exists():
        return set(cache.read_text().split())
    path = scratch(cache.stem, ref)
    found = suite(path, logs / f"{cache.stem}.log") if path else None
    git("worktree", "remove", "--force", str(TREES / cache.stem))
    if found is not None:
        cache.write_text("\n".join(sorted(found)))
    return found


def broken(pr, tree, branch, dest, hist):
    """Testes que o PR, com a mudança do corretor, quebra: (lista, onde foi medido). Lista vazia: nada quebrou.
    Mede onde o PR vai parar: o destino atual, com a branch e a mudança por cima, contra o destino sozinho.
    Se a branch conflita com o destino, mede na própria branch. None: não deu para comparar.
    Só conta o que falha em duas rodadas seguidas (teste instável não segura a correção)."""
    git("add", "-A", cwd=tree)
    patch = hist / "mudanca.patch"
    patch.write_text(git("diff", "--cached", "--binary", "HEAD", cwd=tree)[1] + "\n")
    git("reset", "-q", cwd=tree)  # a mudança continua sem commit e fora do índice, como o revisor espera ver
    stage, where, ref = scratch(f"pr-{pr}-{dest}", f"origin/{dest}"), f"em cima da {dest} atual", f"origin/{dest}"
    if not (stage and git("merge", "--no-commit", "--no-ff", f"origin/{branch}", cwd=stage)[0] == 0
            and git("apply", "--index", str(patch), cwd=stage)[0] == 0):
        git("worktree", "remove", "--force", str(TREES / f"pr-{pr}-{dest}"))
        stage, where, ref = tree, f"na própria branch, porque ela conflita com a {dest}", f"origin/{branch}"
    try:
        base = baseline(ref, hist)
        if base is None:
            return None, where
        after = suite(stage, hist / "suite-depois.log")
        if after is None:
            return ["a suíte não rodou com a mudança (não compila?)"], where
        new = after - base
        if new:
            again = suite(stage, hist / "suite-depois-2.log")
            new &= again if again is not None else new
        return sorted(new), where
    finally:
        if stage != tree:
            git("worktree", "remove", "--force", str(stage))


def queue():
    """PRs na fila: pasta com achados.md e marca.json, do número menor para o maior."""
    if not WORK.is_dir():
        return []
    return sorted((d.name for d in WORK.iterdir() if d.name.isdigit() and (d / "achados.md").exists()
                   and (d / "marca.json").exists()), key=int)


def reopen(base, pr, d):
    """Monta a fila de um PR que já foi comentado: os comentários do PR viram o achados.md."""
    reviewers = {p["user"].get("uuid") for p in d.get("participants", []) if p.get("state")}
    parts = [f"## {d['title'][:80]} (#{pr})", "",
             "Comentários do PR, do mais antigo para o mais novo. Os do revisor são os achados; os outros são respostas do dev.", ""]
    found = False
    for c in sorted(bitbucket.paginate(f"{base}/{pr}/comments", {"pagelen": 100}), key=lambda c: c["created_on"]):
        if c.get("deleted") or not c["content"]["raw"].strip():
            continue
        mine = (c.get("user") or {}).get("uuid") in reviewers
        found = found or mine
        parts += [f"**{'Revisor' if mine else 'Dev (' + c['user']['display_name'] + ')'}, {c['created_on'][:10]}:**", "",
                  c["content"]["raw"].strip(), ""]
    if not found:
        sys.exit(f"PR #{pr}: nenhum comentário de quem tem marca de revisão ativa; nada a reabrir")
    work = WORK / pr
    work.mkdir(parents=True, exist_ok=True)
    (work / "achados.md").write_text("\n".join(parts))
    for old in ("resposta.md", "veredito.json", "commit.txt"):
        (work / old).unlink(missing_ok=True)


def tickets(d, issues):
    """Baixa o ticket do PR se ainda não está na pasta (o corretor não tem credencial do YouTrack)."""
    ids = set(TICKET.findall(d["source"]["branch"]["name"] + " " + d["title"]))
    missing = [i for i in ids if not (issues / f"{i}.json").exists()]
    if missing and os.environ.get("YOUTRACK_API_TOKEN"):
        subprocess.run([sys.executable, str(HERE / "youtrack.py"), "--ids", *missing, "--out", str(issues)],
                       cwd=CLONE, capture_output=True, text=True)


def write(cmd, *args, fixer=False):
    """Chama bitbucket.py para escrever no PR; devolve (deu certo?, saída).
    `fixer`: escreve com a identidade do corretor, quando ele tem token próprio."""
    env = os.environ.copy()
    if fixer and FIXER_TOKEN:
        env["BITBUCKET_ACCESS_TOKEN"] = FIXER_TOKEN
    r = subprocess.run([sys.executable, str(HERE / "bitbucket.py"), cmd, *args, "--isolado"],
                       cwd=CLONE, env=env, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0 and out.endswith("ok"), out


def body(work, pr):
    """Cabeçalho e corpo do achados.md (o cabeçalho precisa do número do PR para o comment)."""
    text = (work / "achados.md").read_text().strip() if (work / "achados.md").exists() else ""
    head, _, rest = text.partition("\n")
    if not head.startswith("## ") or f"#{pr}" not in head:
        head, rest = f"## PR (#{pr})", text
    return head, rest.strip()


def correct(base, pr, dry):
    work, tree, issues = WORK / pr, TREES / f"pr-{pr}", WORK / "issues"
    st, d = bitbucket.call("GET", f"{base}/{pr}")
    if st != 200 or d["state"] != "OPEN":
        log(f"#{pr}: fora da fila ({d['state'] if st == 200 else f'ERRO {st}'})")
        return archive(work, pr)
    branch, dest = d["source"]["branch"]["name"], d["destination"]["branch"]["name"]
    git("fetch", "origin", "--prune", "-q")
    head = git("rev-parse", "--short=12", f"origin/{branch}")[1]
    mark = json.loads((work / "marca.json").read_text())
    if mark["commit"] != head:
        log(f"#{pr}: a branch andou desde a triagem ({mark['commit']} -> {head}); volta para a triagem")
        return archive(work, pr)

    issues.mkdir(parents=True, exist_ok=True)
    tickets(d, issues)
    git("worktree", "remove", "--force", str(tree))
    git("worktree", "prune")
    TREES.mkdir(parents=True, exist_ok=True)
    rc, out = git("worktree", "add", "--detach", str(tree), f"origin/{branch}")
    if rc != 0:
        log(f"#{pr}: não consegui criar a cópia da branch: {out[:200]}")
        return
    log(f"#{pr}: correção{' (ensaio)' if dry else ''}, {branch} em {head}")

    safe = {k: v for k, v in os.environ.items() if not SECRET.search(k) or k == "CLAUDE_CODE_OAUTH_TOKEN"}
    # o caminho vai no pedido: deixado por conta da skill, o contexto do projeto não era lido nestas sessões
    ctx = pathlib.Path("~/.claude/revisar-pr-bitbucket/contexto").expanduser() / f"{bitbucket.resolve_repo(None).split('/')[-1]}.md"
    fmt = dict(pr=pr, branch=branch, dest=dest, n=VOLTAS, work=work, issues=issues,
               context=f" Antes de tudo, leia o contexto do projeto: {ctx}." if ctx.exists() else "",
               verify=f" Para verificar, rode na cópia: {VERIFY}" if VERIFY else "")
    verdict, fresh = None, False  # fresh: o achados.md é texto do revisor, já discutido com o corretor
    for v in range(1, VOLTAS + 1):
        stamp = f"{datetime.datetime.now():%Y%m%d-%H%M}"
        hist = work / "voltas" / str(v)
        hist.mkdir(parents=True, exist_ok=True)
        shutil.copy(work / "achados.md", hist / "achados-entrada.md")
        prev = f" Sua resposta anterior: {work}/resposta.md." if (work / "resposta.md").exists() else ""
        before = (work / "resposta.md").stat().st_mtime if prev else 0
        end = session(CORRETOR, ASK_FIX.format(v=v, prev=prev, **fmt), tree, safe, DIR / "rodadas" / f"{stamp}-corretor-{pr}-{v}.log")
        if not (work / "resposta.md").exists() or (work / "resposta.md").stat().st_mtime <= before:
            log(f"#{pr}: volta {v}, corretor sem resposta ({end})")
            verdict = None
            break
        shutil.copy(work / "resposta.md", hist / "resposta.md")
        (hist / "mudanca.diff").write_text(git("diff", cwd=tree)[1] + "\n" + git("status", "--porcelain", cwd=tree)[1])

        (work / "veredito.json").unlink(missing_ok=True)
        end = session(REVISOR, ASK_GATE.format(v=v, last=" — é a última volta" if v == VOLTAS else "", **fmt),
                      tree, {k: v for k, v in os.environ.items() if k != "CORRETOR_BITBUCKET_TOKEN"},
                      DIR / "rodadas" / f"{stamp}-portao-{pr}-{v}.log")
        try:
            verdict = json.loads((work / "veredito.json").read_text())
            verdict["estado"] = str(verdict.get("estado", "")).strip().lower()
        except (OSError, ValueError):
            verdict = None
            log(f"#{pr}: volta {v}, portão sem veredito ({end})")
            continue
        shutil.copy(work / "veredito.json", hist / "veredito.json")
        shutil.copy(work / "achados.md", hist / "achados-saida.md")
        fresh = True
        log(f"#{pr}: volta {v}, {verdict['estado']}: {str(verdict.get('motivo', ''))[:160]}")
        if verdict["estado"] not in ("aprovado", "parcial"):
            continue
        broke, where = broken(pr, tree, branch, dest, hist) if SUITE and git("status", "--porcelain", cwd=tree)[1] else ([], "")
        if broke is None:
            log(f"#{pr}: volta {v}, suíte sem comparação ({where}): a base não rodou")
        elif where:
            log(f"#{pr}: volta {v}, suíte completa {where}: {len(broke)} teste(s) quebrado(s)")
        if not broke:
            break
        log(f"#{pr}: volta {v}, quebrou: {', '.join(broke)[:200]}")
        (hist / "suite-quebrou.txt").write_text("\n".join(broke) + "\n")
        verdict = None
        if v == VOLTAS:  # sem volta para consertar: a mudança é descartada e vale o que o revisor achou no início
            shutil.copy(work / "voltas" / "1" / "achados-entrada.md", work / "achados.md")
            fresh = not json.loads((work / "marca.json").read_text()).get("reaberto")
            break
        (work / "achados.md").write_text(
            body(work, pr)[0] + f"\n\n❌ **O PR, com a sua mudança, quebra testes que hoje passam.** A suíte completa rodou "
            f"{where}; estes passam sem o PR e falham com ele:\n" + "\n".join(f"- `{x}`" for x in broke)
            + "\n\nPara cada um: se o teste afirmava exatamente o comportamento que o ticket manda mudar, arrume o teste "
            "(só essa asserção, para o comportamento do ticket) e diga isso na resposta. Se o teste cobre outra coisa, a "
            "mudança tem efeito colateral: conserte a mudança. Se não dá para dizer pelo ticket, desfaça a mudança daquele "
            "achado e responda DECISÃO.\n")

    publish(pr, branch, head, tree, work, verdict, dry, fresh, quiet=bool(mark.get("validador")))
    if dry:  # ensaio não fica na fila: senão o próximo gatilho publicaria de verdade
        (work / "marca.json").rename(work / "marca-ensaio.json")
    else:
        git("worktree", "remove", "--force", str(tree))
        archive(work, pr)


def publish(pr, branch, head, tree, work, verdict, dry, fresh, quiet=False):
    """`quiet`: o PR veio do validador, que espera o veredito e é quem comenta. Os textos ficam na pasta;
    no PR entram só o push e a marca (aprovação ou request changes)."""
    state = verdict["estado"] if verdict and verdict["estado"] in ("aprovado", "parcial") else "sem acordo"
    changed = bool(git("status", "--porcelain", cwd=tree)[1]) and state != "sem acordo"
    title, rest = body(work, pr)
    fixed = [str(x).strip() for x in (verdict or {}).get("corrigido", []) if str(x).strip()]
    notes = [str(x).strip() for x in (verdict or {}).get("nao_bloqueia", []) if str(x).strip()] if state != "sem acordo" else []
    commit = None
    if changed:
        name, email = os.environ.get("CORRETOR_GIT_NAME"), os.environ.get("CORRETOR_GIT_EMAIL")
        if not (name and email):
            log(f"#{pr}: CORRETOR_GIT_NAME/CORRETOR_GIT_EMAIL ausentes; nada publicado")
            return
        msg = work / "commit.txt"
        if not msg.exists() or not msg.read_text().strip():
            msg.write_text(f"fix: correções da revisão do PR #{pr}\n")
        git("add", "-A", cwd=tree)
        rc, out = git("-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-q", "-F", str(msg), cwd=tree)
        if rc != 0:
            log(f"#{pr}: commit falhou, nada publicado: {out[:200]}")
            return
        commit = git("rev-parse", "--short=12", "HEAD", cwd=tree)[1]

    # o que o corretor diz (o que mudou) e o que o revisor diz (o que ficou para o dev)
    mine, theirs = [], []
    if commit:
        mine.append(f"🔧 **Corrigido automaticamente no commit `{commit}`.**\n" + "\n".join(f"- {x}" for x in fixed))
    if state != "aprovado" and rest:
        theirs.append(rest)
    if notes:
        (mine if commit else theirs).append("ℹ️ **Ficou de fora, não bloqueia:**\n" + "\n".join(f"- {x}" for x in notes))
    if commit:
        mine.append("Puxe a branch antes de continuar (`git pull --rebase`).")
    if not FIXER_TOKEN and mine and theirs:  # uma identidade só: um comentário só
        mine, theirs = [], [*mine, "**O que ficou para você:**\n\n" + "\n\n".join(theirs)]
    posts = [(who, f"{title}\n" + "\n\n".join(parts) + "\n", work / name)
             for who, parts, name in ((True, mine, "comentario-corretor.md"), (False, theirs, "comentario.md")) if parts]
    # sem texto novo do revisor para um PR reaberto: o achados.md ainda é o histórico de comentários do
    # próprio PR, e o request changes já está lá. Não há nada novo a dizer.
    if state == "sem acordo" and not fresh and json.loads((work / "marca.json").read_text()).get("reaberto"):
        log(f"#{pr}: sem acordo e sem texto novo do revisor; o PR fica como estava")
        return
    final = "approve" if state == "aprovado" else "request-changes"
    plan = f"{state}: " + ", ".join(x for x in (f"push do commit {commit}" if commit else "", f"{len(posts)} comentário(s)" if posts else "",
                                              "aprovação" if final == "approve" else "request changes") if x)
    for _, text, path in posts:
        path.write_text(text)
    if dry:
        log(f"#{pr}: ENSAIO, publicaria — {plan}. Cópia em {tree}, arquivos em {work}")
        return

    if commit:
        git("fetch", "origin", "--prune", "-q")
        if git("rev-parse", "--short=12", f"origin/{branch}")[1] != head:
            log(f"#{pr}: a branch andou durante a correção; nada publicado, volta para a triagem")
            return
        if FIXER_TOKEN:  # o token vem do ambiente pelo helper, não entra na linha de comando
            helper = "!f() { echo username=x-token-auth; echo \"password=$CORRETOR_BITBUCKET_TOKEN\"; }; f"
            rc, out = git("-c", "credential.helper=", "-c", f"credential.helper={helper}", "push",
                          f"https://bitbucket.org/{bitbucket.resolve_repo(None)}.git", f"HEAD:refs/heads/{branch}", cwd=tree)
        else:
            rc, out = git("push", "origin", f"HEAD:refs/heads/{branch}", cwd=tree)
        if rc != 0:
            log(f"#{pr}: push falhou, nada publicado: {out[:200]}")
            return
        # o Bitbucket registra o push no PR com atraso; a marca do revisor tem que vir depois dele,
        # senão o PR volta como "commit novo depois de <revisão>" e é revisado de novo à toa
        for _ in range(30):
            st, d = bitbucket.call("GET", f"{bitbucket.resolve_repo(None)}/pullrequests/{pr}", params={"fields": "source.commit.hash"})
            if st == 200 and d["source"]["commit"]["hash"][:12] == commit:
                break
            time.sleep(2)
        time.sleep(3)
    done = [f"push do commit {commit}"] if commit else []
    for who, _, path in [] if quiet else posts:  # o do corretor primeiro: a marca do revisor fecha a conversa
        ok, out = write("comment", str(path), fixer=who)
        done.append(f"comentário do {'corretor' if who else 'revisor'}" if ok else f"comentário FALHOU ({out[:120]})")
    ok, out = write(final, pr)
    done.append(("aprovação" if final == "approve" else "request changes") if ok else f"{final} FALHOU ({out[:120]})")
    log(f"#{pr}: {state} — " + ", ".join(done))


def archive(work, pr):
    if work.is_dir():
        dest = WORK / "feitos" / f"{datetime.datetime.now():%Y%m%d-%H%M}-{pr}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(work), str(dest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr")
    ap.add_argument("--reabrir")
    ap.add_argument("--ensaio", action="store_true")
    a = ap.parse_args()
    if not CLONE:
        sys.exit("REVISOR_CLONE ausente: aponte para o clone do repo dos PRs")
    if not CORRETOR:
        sys.exit("CORRETOR_CLAUDE ausente: o comando do Claude Code do corretor, com as permissões dele")
    os.chdir(CLONE)
    base = f"{bitbucket.resolve_repo(None)}/pullrequests"
    (DIR / "rodadas").mkdir(parents=True, exist_ok=True)
    lock = open(DIR / "corretor.lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)  # espera o corretor que estiver rodando
    todo = queue() if not (a.pr or a.reabrir) else [a.pr or a.reabrir]
    if not todo:
        return
    rc, out = git("fetch", "origin", "--prune", "-q")
    if rc != 0:
        sys.exit(f"{now()} git fetch falhou: {out[:300]}")
    if a.reabrir:
        st, d = bitbucket.call("GET", f"{base}/{a.reabrir}")
        if st != 200 or d["state"] != "OPEN":
            sys.exit(f"PR #{a.reabrir}: {d['state'] if st == 200 else f'ERRO {st} {d}'}")
        reopen(base, a.reabrir, d)
        head = git("rev-parse", "--short=12", f"origin/{d['source']['branch']['name']}")[1]
        (WORK / a.reabrir / "marca.json").write_text(json.dumps(
            {"commit": head, "desde": datetime.datetime.now(datetime.timezone.utc).isoformat(), "reaberto": True}))
    elif a.pr and a.pr not in queue():
        sys.exit(f"PR #{a.pr} não está na fila de correção ({WORK})")
    seen = set()
    while todo and len(seen) < MAX:  # a fila pode crescer enquanto um PR é corrigido
        pr = todo[0]
        seen.add(pr)
        correct(base, pr, a.ensaio)
        todo = [] if a.pr or a.reabrir else [p for p in queue() if p not in seen]


if __name__ == "__main__":
    main()
