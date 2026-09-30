#!/usr/bin/env python3
"""Operações mínimas no Bitbucket Cloud para a revisão de PRs.

Uso:
  bitbucket.py find BRANCH [BRANCH ...]        # PR aberto de cada branch (id, destino, autor, revisão)
  bitbucket.py info PR [PR ...]                # título, branches, autor, estado, revisão
  bitbucket.py describe PR                     # descrição do PR
  bitbucket.py comment ARQUIVO.md              # posta cada seção "## ... (#<pr>)" no PR indicado
  bitbucket.py request-changes PR [PR ...]     # marca request changes
  bitbucket.py approve PR [PR ...]             # aprova (não faz merge)

Repo: --repo workspace/slug, ou $BITBUCKET_REPO, ou o remote `origin` do git no diretório atual.
Credenciais: $BITBUCKET_EMAIL e $BITBUCKET_API_TOKEN (API token do Atlassian com
read:pullrequest:bitbucket + write:pullrequest:bitbucket).
Nunca recusa (decline) nem faz merge.

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
    email, token = os.environ.get("BITBUCKET_EMAIL"), os.environ.get("BITBUCKET_API_TOKEN")
    if not email or not token:
        sys.exit("BITBUCKET_EMAIL/BITBUCKET_API_TOKEN ausentes no ambiente")
    url = f"{API}/{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"})
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


def post_state(base, pr, action):
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
    sub.add_parser("describe").add_argument("pr")
    sub.add_parser("comment").add_argument("file")
    sub.add_parser("request-changes").add_argument("prs", nargs="+")
    sub.add_parser("approve").add_argument("prs", nargs="+")
    a = ap.parse_args()
    base = f"{resolve_repo(a.repo)}/pullrequests"

    if a.cmd == "find":
        for b in a.branches:
            st, d = call("GET", base, params={"q": f'source.branch.name="{b}"', "state": "OPEN",
                                               "fields": "values.id,values.destination.branch.name,values.author.display_name,"
                                                         "values.participants.state,values.participants.user.display_name"})
            print(b, [(p["id"], p["destination"]["branch"]["name"], p["author"]["display_name"], review(p)) for p in d["values"]]
                  if st == 200 else f"ERRO {st} {d}")

    elif a.cmd == "info":
        for pr in a.prs:
            st, d = call("GET", f"{base}/{pr}")
            if st != 200:
                print(pr, "ERRO", st, d); continue
            print(pr, "|", d["state"], "|", d["source"]["branch"]["name"], "->", d["destination"]["branch"]["name"],
                  "|", d["author"]["display_name"], "|", review(d), "|", d["title"])

    elif a.cmd == "describe":
        st, d = call("GET", f"{base}/{a.pr}", params={"fields": "description"})
        print(d.get("description", "") if st == 200 else f"ERRO {st} {d}")

    elif a.cmd == "comment":
        txt = open(a.file).read()
        parts = re.split(r"^## (.+)\n", txt, flags=re.M)[1:]
        skipped = []
        for head, body in zip(parts[0::2], parts[1::2]):
            m = re.search(r"#(\d+)", head)
            if not m or not body.strip():
                skipped.append(head.strip()); continue
            st, d = call("POST", f"{base}/{m.group(1)}/comments", body={"content": {"raw": body.strip()}})
            print(head.strip(), "ok" if st in (200, 201) else f"ERRO {st} {d}")
        if skipped:
            print("não postado (sem número de PR ou vazio):", ", ".join(skipped))

    elif a.cmd == "request-changes":
        for pr in a.prs:
            post_state(base, pr, "request-changes")

    elif a.cmd == "approve":
        for pr in a.prs:
            post_state(base, pr, "approve")


if __name__ == "__main__":
    main()
