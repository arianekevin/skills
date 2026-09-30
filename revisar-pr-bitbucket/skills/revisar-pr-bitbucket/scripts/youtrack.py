#!/usr/bin/env python3
"""Baixa tickets do YouTrack (descrição + comentários) e extrai PRs e commits citados.

Uso:
  youtrack.py --url '<link de busca do YouTrack>' --out DIR
  youtrack.py --query 'Versão: X tag: {Y}' --out DIR
  youtrack.py --ids ABC-1 ABC-2 --out DIR

Grava DIR/<ID>.json e imprime uma linha por ticket: ID | prioridade | estado | PRs | commits | título.
Precisa de $YOUTRACK_API_TOKEN. A instância sai do --url; com --query/--ids, de $YOUTRACK_URL
(ex.: https://empresa.myjetbrains.com/youtrack).
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request


def get(base, path, params):
    token = os.environ.get("YOUTRACK_API_TOKEN")
    if not token:
        sys.exit("YOUTRACK_API_TOKEN não está no ambiente")
    url = f"{base}/api/{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--query")
    g.add_argument("--url")
    g.add_argument("--ids", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.url:
        u = urllib.parse.urlparse(a.url)
        prefix = u.path.split("/issues")[0].split("/issue/")[0]
        base = f"{u.scheme}://{u.netloc}{prefix}"
        a.query = urllib.parse.parse_qs(u.query)["q"][0]
    else:
        base = os.environ.get("YOUTRACK_URL", "").rstrip("/")
        if not base:
            sys.exit("defina $YOUTRACK_URL (ex.: https://empresa.myjetbrains.com/youtrack) ou passe --url")

    if a.query:
        ids = [i["idReadable"] for i in get(base, "issues", {"query": a.query, "fields": "idReadable", "$top": 500})]
    else:
        ids = a.ids

    fields = "idReadable,summary,description,customFields(name,value(name)),comments(text,created,author(login))"
    for id_ in ids:
        d = get(base, f"issues/{id_}", {"fields": fields})
        json.dump(d, open(os.path.join(a.out, f"{id_}.json"), "w"), ensure_ascii=False, indent=1)
        cf = {c["name"]: (c["value"] or {}).get("name") if isinstance(c["value"], dict) else c["value"] for c in d["customFields"]}
        txt = " ".join(c["text"] or "" for c in d["comments"])
        prs = sorted(set(re.findall(r"pull-requests/(\d+)", txt)))
        commits = sorted(set(re.findall(r"commits? `([0-9a-f]{7,40})`", txt)))
        print(f"{id_} | {cf.get('Priority')} | {cf.get('State')} | PRs={','.join(prs) or '-'} | commits={','.join(commits) or '-'} | {d['summary']}")


if __name__ == "__main__":
    main()
