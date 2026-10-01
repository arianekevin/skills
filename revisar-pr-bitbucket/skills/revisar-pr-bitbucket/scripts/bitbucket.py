#!/usr/bin/env python3
"""Operações mínimas no Bitbucket Cloud para a revisão de PRs.

Uso:
  bitbucket.py find BRANCH [BRANCH ...]        # PR aberto de cada branch (id, destino, autor, REVISAR/PULAR)
  bitbucket.py info PR [PR ...]                # título, branches, autor, estado, REVISAR/PULAR
  bitbucket.py list [--dest B] [--author NOME] [--reviewer NOME]
                                               # PRs abertos (id, branches, autor, revisão, título);
                                               # --reviewer: só os que têm NOME entre os revisores
  bitbucket.py describe PR                     # descrição do PR
  bitbucket.py comments PR                     # comentários do PR (autor, arquivo:linha se inline, texto)
  bitbucket.py related PR [--grep TXT ...]     # outros PRs abertos para o mesmo destino que tocam os
                                               # mesmos arquivos ou citam TXT no título/commits
                                               # (só linhas que casaram; usa o clone local, rode git fetch antes)
  bitbucket.py comment ARQUIVO.md              # posta cada seção "## ... (#<pr>)" no PR indicado
  bitbucket.py request-changes PR [PR ...]     # marca request changes
  bitbucket.py approve PR [PR ...]             # aprova (não faz merge)

Repo: --repo workspace/slug, ou $BITBUCKET_REPO, ou o remote `origin` do git no diretório atual.
Credenciais, uma das duas:
  - $BITBUCKET_ACCESS_TOKEN: access token do repositório (Repository settings > Access tokens), com
    Repositories: Read e Pull requests: Read + Write. Age como um usuário-bot com o nome do token.
    Se estiver definido, é o que vale.
  - $BITBUCKET_EMAIL e $BITBUCKET_API_TOKEN: API token do Atlassian, com read:pullrequest:bitbucket
    + write:pullrequest:bitbucket. Age como o dono do token.
Nunca recusa (decline) nem faz merge.
Só entra na análise PR aberto, fora de draft e sem revisão ativa (request changes ou aprovação): `find`, `info`
e `list` marcam REVISAR ou PULAR: <motivo>, e `comment`, `request-changes` e `approve` recusam
o resto. Revisão anterior ao último commit do PR, ou a um comentário de quem não é o revisor,
não conta como ativa: o PR volta como `REVISAR: commit novo depois de <revisão>` (ou
`comentário novo`). Exceção: PR pedido sozinho pelo número, com `--isolado` na escrita.

Formato do ARQUIVO.md para `comment`: seções `## <rótulo> (#<pr>)`. Seção sem número
de PR é ignorada e listada no fim.
"""
import argparse, base64, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.bitbucket.org/2.0/repositories"


def resolve_repo(arg):
    if arg:
        return arg
    if os.environ.get("BITBUCKET_REPO"):
        return os.environ["BITBUCKET_REPO"]
    try:
        url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        url = ""
    m = re.search(r"bitbucket\.org[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        sys.exit("repo não identificado: rode dentro do clone do repo, ou use --repo workspace/slug / $BITBUCKET_REPO")
    return f"{m.group(1)}/{m.group(2)}"


def call(method, path, body=None, params=None):
    bearer = os.environ.get("BITBUCKET_ACCESS_TOKEN")
    email, token = os.environ.get("BITBUCKET_EMAIL"), os.environ.get("BITBUCKET_API_TOKEN")
    if bearer:
        auth = f"Bearer {bearer}"
    elif email and token:
        auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()
    else:
        sys.exit("credencial ausente no ambiente: BITBUCKET_ACCESS_TOKEN, ou BITBUCKET_EMAIL + BITBUCKET_API_TOKEN")
    url = f"{API}/{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    # Content-Type só com corpo: POST sem corpo (approve, request-changes) com application/json volta 400
    headers = {"Authorization": auth}
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None, headers=headers)
    try:
        r = urllib.request.urlopen(req)
        raw = r.read()
        return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode(errors="replace")


def review(pr):
    """Revisão ativa no PR: `changes_requested`, `approved` ou `sem revisão`, com quem marcou.
    Request changes pesa mais que aprovação: se houver os dois, vale o request changes."""
    for state in ("changes_requested", "approved"):
        who = [p["user"]["display_name"] for p in pr.get("participants", []) if p.get("state") == state]
        if who:
            return f"{state} ({', '.join(who)})"
    return "sem revisão"


def news_after_review(base, pr_id, reviewers):
    """O que chegou ao PR depois da última revisão: (commit novo?, comentário novo?).
    Revisão = aprovação, request changes ou comentário de um revisor (`reviewers`: uuids de quem
    tem marca ativa) — a resposta do revisor também fecha o que veio antes dela.
    A activity vem da mais nova para a mais antiga; cada `update` traz o commit de origem daquele momento."""
    head, commented, reviewed = None, False, False
    for v in paginate(f"{base}/{pr_id}/activity", {"pagelen": 50}):
        by_reviewer = "comment" in v and (v["comment"].get("user") or {}).get("uuid") in reviewers
        if "approval" in v or "changes_requested" in v or by_reviewer:
            if head is None:  # nenhum update depois da revisão
                return False, commented
            reviewed = True
        elif "update" in v:
            h = ((v["update"].get("source") or {}).get("commit") or {}).get("hash")
            if reviewed:  # primeiro update anterior à revisão: o commit que foi revisado
                return h != head, commented
            head = head or h
        elif "comment" in v and not reviewed:
            commented = True
    return False, False


def mark(base, pr, pr_id=None):
    """REVISAR ou PULAR: <motivo>. Fica fora da análise o PR que não está aberto, que está em
    draft ou que tem revisão ativa sem commit nem comentário de terceiro depois dela."""
    if pr.get("state", "OPEN") != "OPEN":
        return f"PULAR: {pr['state']}"
    if pr.get("draft"):
        return "PULAR: draft"
    r = review(pr)
    if r == "sem revisão":
        return "REVISAR"
    reviewers = {p["user"].get("uuid") for p in pr.get("participants", []) if p.get("state")}
    commit, comment = news_after_review(base, pr_id or pr["id"], reviewers)
    if commit or comment:
        news = " e ".join(n for n, on in (("commit", commit), ("comentário", comment)) if on)
        return f"REVISAR: {news} novo depois de {r}"
    return f"PULAR: {r}"


def guard(base, pr, isolated=False):
    """Escrita só em PR que `mark` manda revisar. `isolated`: o dev pediu este PR sozinho, pelo número."""
    if isolated:
        return True
    st, d = call("GET", f"{base}/{pr}", params={"fields": "state,draft,participants.state,participants.user.display_name,participants.user.uuid"})
    if st != 200:
        print(pr, f"ERRO {st} {d}"); return False
    m = mark(base, d, pr)
    if m.startswith("PULAR"):
        print(pr, m.replace("PULAR", "PULADO", 1)); return False
    return True


def paginate(path, params):
    """Todas as páginas de uma listagem da API (segue `next`)."""
    st, d = call("GET", path, params=params)
    while True:
        if st != 200:
            sys.exit(f"ERRO {st} {d}")
        yield from d.get("values", [])
        nxt = d.get("next")
        if not nxt:
            return
        st, d = call("GET", nxt.split(f"{API}/", 1)[1])


def open_prs(base, dest=None, author=None, reviewer=None):
    # o estado vai dentro do `q`: com `q` presente, o parâmetro `state` solto é ignorado
    q = 'state="OPEN"' + (f' AND destination.branch.name="{dest}"' if dest else "")
    prs = paginate(base, {"q": q, "pagelen": 50,
                          "fields": "next,values.id,values.title,values.source.branch.name,values.destination.branch.name,"
                                    "values.author.display_name,values.author.nickname,values.draft,"
                                    "values.reviewers.display_name,values.reviewers.nickname,"
                                    "values.participants.state,values.participants.user.display_name,values.participants.user.uuid"})
    if author:
        a = author.lower()
        prs = (p for p in prs if a in (p["author"].get("display_name") or "").lower()
               or a in (p["author"].get("nickname") or "").lower())
    if reviewer:
        r = reviewer.lower()
        prs = (p for p in prs if any(r in (u.get("display_name") or "").lower() or r in (u.get("nickname") or "").lower()
                                     for u in p.get("reviewers", [])))
    return list(prs)


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def changed_files(dest, branch):
    mb = git("merge-base", f"origin/{dest}", f"origin/{branch}")
    out = git("diff", "--name-only", mb, f"origin/{branch}") if mb else None
    return None if out is None else set(filter(None, out.splitlines()))


def post_state(base, pr, action, isolated=False):
    if not guard(base, pr, isolated):
        return
    st, d = call("POST", f"{base}/{pr}/{action}")
    if st == 400:  # logo após comentar o Bitbucket às vezes devolve 400; a segunda tentativa passa
        time.sleep(3)
        st, d = call("POST", f"{base}/{pr}/{action}")
    print(pr, "ok" if st == 200 else f"ERRO {st} {d}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("find").add_argument("branches", nargs="+")
    sub.add_parser("info").add_argument("prs", nargs="+")
    p = sub.add_parser("list")
    p.add_argument("--dest")
    p.add_argument("--author")
    p.add_argument("--reviewer")
    sub.add_parser("describe").add_argument("pr")
    sub.add_parser("comments").add_argument("pr")
    p = sub.add_parser("related")
    p.add_argument("pr")
    p.add_argument("--grep", action="append", default=[])
    for name, arg in (("comment", "file"), ("request-changes", "prs"), ("approve", "prs")):
        p = sub.add_parser(name)
        p.add_argument(arg, nargs=None if arg == "file" else "+")
        p.add_argument("--isolado", action="store_true", help="PR pedido sozinho pelo número: sem a trava")
    a = ap.parse_args()
    base = f"{resolve_repo(a.repo)}/pullrequests"

    if a.cmd == "find":
        for b in a.branches:
            st, d = call("GET", base, params={"q": f'source.branch.name="{b}" AND state="OPEN"',
                                               "fields": "values.id,values.draft,values.destination.branch.name,values.author.display_name,"
                                                         "values.participants.state,values.participants.user.display_name,values.participants.user.uuid"})
            print(b, [(p["id"], p["destination"]["branch"]["name"], p["author"]["display_name"], mark(base, p)) for p in d["values"]] or "sem PR aberto"
                  if st == 200 else f"ERRO {st} {d}")

    elif a.cmd == "info":
        for pr in a.prs:
            st, d = call("GET", f"{base}/{pr}")
            if st != 200:
                print(pr, "ERRO", st, d); continue
            print(pr, "|", d["state"], "|", d["source"]["branch"]["name"], "->", d["destination"]["branch"]["name"],
                  "|", d["author"]["display_name"], "|", mark(base, d), "|", d["title"])

    elif a.cmd == "list":
        prs = open_prs(base, a.dest, a.author, a.reviewer)
        n = 0
        for p in prs:
            m = mark(base, p)
            n += m.startswith("REVISAR")
            print(p["id"], "|", p["source"]["branch"]["name"], "->", p["destination"]["branch"]["name"],
                  "|", p["author"]["display_name"], "|", m, "|", p["title"])
        print(f"{len(prs)} PR(s) aberto(s); {n} a revisar, {len(prs) - n} pulado(s) por draft ou revisão ativa")

    elif a.cmd == "describe":
        st, d = call("GET", f"{base}/{a.pr}", params={"fields": "description"})
        print(d.get("description", "") if st == 200 else f"ERRO {st} {d}")

    elif a.cmd == "comments":
        n = 0
        for c in paginate(f"{base}/{a.pr}/comments", {"pagelen": 100}):
            if c.get("deleted"):
                continue
            n += 1
            inline = c.get("inline") or {}
            where = f" [{inline.get('path')}:{inline.get('to') or inline.get('from')}]" if inline else ""
            reply = " (resposta)" if c.get("parent") else ""
            print(f"--- {c['user']['display_name']} {c['created_on'][:10]}{where}{reply}")
            print(c["content"]["raw"].strip())
        print(f"{n} comentário(s)")

    elif a.cmd == "related":
        st, d = call("GET", f"{base}/{a.pr}")
        if st != 200:
            sys.exit(f"ERRO {st} {d}")
        dest, src = d["destination"]["branch"]["name"], d["source"]["branch"]["name"]
        mine = changed_files(dest, src)
        if mine is None:
            sys.exit(f"branch origin/{src} ou origin/{dest} ausente no clone: rode git fetch origin --prune")
        greps = [g.lower() for g in a.grep]
        hits, missing = 0, []
        for p in open_prs(base, dest):
            if str(p["id"]) == str(a.pr):
                continue
            branch = p["source"]["branch"]["name"]
            files = changed_files(dest, branch)
            if files is None:
                missing.append(str(p["id"])); continue
            common = sorted(mine & files)
            cited = []
            if greps:
                text = (p["title"] + "\n" + (git("log", "--format=%B", f"origin/{dest}..origin/{branch}") or "")).lower()
                cited = [g for g in a.grep if g.lower() in text]
            if common or cited:
                hits += 1
                parts = []
                if common:
                    parts.append("arquivos em comum: " + ", ".join(f.rsplit("/", 1)[-1] for f in common))
                if cited:
                    parts.append("cita: " + ", ".join(cited))
                print(p["id"], "|", branch, "|", p["author"]["display_name"], "|", " | ".join(parts))
        print(f"{hits} PR(s) relacionado(s)" + (f"; sem branch no clone: {', '.join(missing)}" if missing else ""))

    elif a.cmd == "comment":
        txt = open(a.file).read()
        parts = re.split(r"^## (.+)\n", txt, flags=re.M)[1:]
        skipped = []
        for head, body in zip(parts[0::2], parts[1::2]):
            m = re.search(r"#(\d+)", head)
            if not m or not body.strip():
                skipped.append(head.strip()); continue
            if not guard(base, m.group(1), a.isolado):
                continue
            st, d = call("POST", f"{base}/{m.group(1)}/comments", body={"content": {"raw": body.strip()}})
            print(head.strip(), "ok" if st in (200, 201) else f"ERRO {st} {d}")
        if skipped:
            print("não postado (sem número de PR ou vazio):", ", ".join(skipped))

    elif a.cmd == "request-changes":
        for pr in a.prs:
            post_state(base, pr, "request-changes", a.isolado)

    elif a.cmd == "approve":
        for pr in a.prs:
            post_state(base, pr, "approve", a.isolado)


if __name__ == "__main__":
    main()
