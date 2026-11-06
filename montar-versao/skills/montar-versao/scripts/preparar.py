#!/usr/bin/env python3
"""Prepara no YouTrack a próxima versão principal do nectarcrm (e a acerta na montagem).

  preparar.py --versao vYY.T.NNN [--plano] [--montagem]

1. Cria o valor <versão> no campo "Versão" (bundle compartilhado entre os projetos).
2. Acha os tickets WEB/IN em "Apto para teste" que são do backend: têm commit na alpha
   ainda fora da última versão, ou PR aberto para a alpha, no nectarcrm ou num serviço que
   sobe junto (sparknectarbi, automation-flow). Põe a versão no campo "Versão" deles.
3. Cria (ou atualiza, se já existe) o ticket de versão no PID para o Hugo:
   "Versão - DD/MM", com DD/MM = próxima segunda.
   Com --montagem, a linha "App" sai com a versão que está no insider hoje (a mais recente
   da principal anterior, com hotfix).

--plano mostra tudo e não grava nada. Rodar de novo é seguro: o que já está feito fica.

Ambiente: $YOUTRACK_API_TOKEN (escrita), $BITBUCKET_EMAIL + $BITBUCKET_API_TOKEN (ou
$BITBUCKET_ACCESS_TOKEN). Repositórios: $REPO (nectarcrm, padrão: o diretório atual) e
$SERVICOS ("caminho:rótulo ..."; padrão sparknectarbi:BI3 e automation-flow:automation-flow,
irmãos do nectarcrm). Saída: 0 ok · 2 uso/validação · 4 falha de API · 5 projeto a confirmar (nada gravado).
"""
import argparse, base64, datetime, json, os, re, subprocess, sys, urllib.error, urllib.parse, urllib.request

YT = os.environ.get("YOUTRACK_URL", "https://nectar.myjetbrains.com/youtrack").rstrip("/")
BB = "https://api.bitbucket.org/2.0/repositories"
PROJETOS = ("WEB", "IN")
ESTADO = "Apto para teste"
CAMPO = "Versão"
PID = {"Type": "Rotina", "Projeto": "Release e CI/CD", "Priority": "1 - Urgente"}
RESPONSAVEL = os.environ.get("PREPARAR_RESPONSAVEL", "Hugo_Freitas")
RE_VERSAO = re.compile(r"^v\d{2}\.[1-4]\.\d{3}$")
RE_BACKEND = re.compile(r"^v\d{2}\.[1-4]\.\d{3}(\.\d+)?$")  # o que a troca automática pode sobrescrever
A_DEFINIR = "a definir"
WORKSPACE = os.environ.get("BITBUCKET_WORKSPACE", "gitcolmeia")
CONF = os.path.expanduser(os.environ.get("PREPARAR_CONF", "~/.claude/montar-versao/projetos.conf"))
CONF_INICIAL = """# Projetos com ambiente de teste (alpha ou homolog) e se sobem na versão de bugfix de segunda.
# <slug do Bitbucket> <entra|fora> [rótulo no ticket de versão]
# O nectarcrm sempre entra. Projeto com ticket apto que não está aqui trava a gravação até alguém
# confirmar com quem acionou a skill; a resposta vem para cá.
sparknectarbi    entra  BI3
automation-flow  entra  automation-flow
nectar-reloaded  fora   # Vue sobe à parte (linha Vue do ticket de versão)
"""


def erro(msg, code=2):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------- HTTP ----------

def http(url, method="GET", body=None, auth=None):
    headers = {"Accept": "application/json", "Authorization": auth}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        erro(f"{method} {url.split('?')[0]} → HTTP {e.code}: {e.read()[:300].decode(errors='replace')}", 4)


def yt(path, params=None, method="GET", body=None):
    token = os.environ.get("YOUTRACK_API_TOKEN") or erro("YOUTRACK_API_TOKEN não está no ambiente")
    url = f"{YT}/api/{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    return http(url, method, body, f"Bearer {token}")


def bb(path, params):
    bearer = os.environ.get("BITBUCKET_ACCESS_TOKEN")
    email, token = os.environ.get("BITBUCKET_EMAIL"), os.environ.get("BITBUCKET_API_TOKEN")
    if bearer:
        auth = f"Bearer {bearer}"
    elif email and token:
        auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()
    else:
        erro("credencial do Bitbucket ausente: BITBUCKET_ACCESS_TOKEN, ou BITBUCKET_EMAIL + BITBUCKET_API_TOKEN")
    url = f"{BB}/{path}?{urllib.parse.urlencode(params)}"
    valores = []
    while url:
        r = http(url, auth=auth)
        valores += r.get("values", [])
        url = r.get("next")
    return valores


# ---------- git ----------

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def slug(repo):
    url = git(repo, "remote", "get-url", "origin").strip()
    m = re.search(r"bitbucket\.org[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit(f"{repo}: origin não é do Bitbucket")
    return f"{m.group(1)}/{m.group(2)}"


def ultima_principal(repo, antes_de=None):
    """Tag de versão principal mais recente do repo (opcionalmente anterior a antes_de)."""
    tags = [t for t in git(repo, "tag", "-l", "v*").split() if RE_VERSAO.match(t)]
    tags.sort(key=lambda t: [int(x) for x in t[1:].split(".")])
    if antes_de:
        tags = [t for t in tags if t != antes_de]
    return tags[-1] if tags else None


def mais_recente_da(repo, principal):
    """A principal ou o hotfix mais recente dela (vYY.T.NNN.H)."""
    tags = [t for t in git(repo, "tag", "-l", f"{principal}*").split()
            if t == principal or re.match(re.escape(principal) + r"\.\d+$", t)]
    tags.sort(key=lambda t: [int(x) for x in t[1:].split(".")])
    return tags[-1] if tags else None


def buscar(repo):
    git(repo, "fetch", "-q", "origin")
    # Tag local divergente do origin não derruba: avisa e segue com a local (como o montar.sh).
    if subprocess.run(["git", "-C", repo, "fetch", "-q", "origin", "--tags"], capture_output=True).returncode:
        print(f"AVISO: {os.path.basename(repo)}: tags locais diferentes do origin (ficou a local)", file=sys.stderr)


def ramo_de_teste(repo):
    """alpha se existe; senão homolog (ex.: for-whats). None: o projeto não tem ambiente de teste."""
    ramos = git(repo, "branch", "-r", "--format=%(refname:short)").split()
    return next((r for r in ("origin/alpha", "origin/homolog") if r in ramos), None)


def clones_locais(pasta):
    """slug -> caminho, para cada clone do workspace em `pasta` (o de nome igual ao slug vence)."""
    achados = {}
    for nome in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, nome)
        if not os.path.isdir(os.path.join(caminho, ".git")):
            continue
        try:
            s = slug(caminho)
        except (SystemExit, subprocess.CalledProcessError):  # sem origin, ou fora do Bitbucket
            continue
        ws, _, repo = s.partition("/")
        if ws == WORKSPACE and (repo not in achados or nome == repo):
            achados[repo] = caminho
    return achados


def ids_em_commits(repo, ramo, base):
    """IDs WEB/IN citados nos commits do ramo de teste que a última versão ainda não tem."""
    ramos = git(repo, "branch", "-r", "--format=%(refname:short)").split()
    if base:
        excluir = f"refs/tags/{base}"
    else:
        excluir = next((r for r in ("origin/master", "origin/main") if r in ramos and r != ramo), None)
    log = git(repo, "log", f"{excluir}..{ramo}" if excluir else ramo, "--since=90 days ago", "--format=%B")
    return set(re.findall(r"\b((?:%s)-\d+)\b" % "|".join(PROJETOS), log.upper()))


def ids_em_prs(repo_slug):
    """IDs WEB/IN no título ou na branch dos PRs abertos para alpha ou homolog."""
    prs = bb(f"{repo_slug}/pullrequests",
             {"state": "OPEN", "q": 'destination.branch.name="alpha" OR destination.branch.name="homolog"',
              "pagelen": 50, "fields": "next,values.id,values.title,values.source.branch.name"})
    achados = {}
    for pr in prs:
        texto = f"{pr['title']} {pr['source']['branch']['name']}".upper()
        for i in set(re.findall(r"\b((?:%s)-\d+)\b" % "|".join(PROJETOS), texto)):
            achados.setdefault(i, []).append(pr["id"])
    return achados


def carregar_conf():
    """slug -> (entra|fora, rótulo). Cria o arquivo com o que já se sabe se ele não existe."""
    if not os.path.exists(CONF):
        os.makedirs(os.path.dirname(CONF), exist_ok=True)
        with open(CONF, "w") as f:
            f.write(CONF_INICIAL)
    conf = {}
    for linha in open(CONF):
        linha = linha.split("#")[0].strip()
        if linha:
            partes = linha.split(None, 2)
            if len(partes) < 2 or partes[1] not in ("entra", "fora"):
                erro(f"{CONF}: linha inválida: {linha}")
            conf[partes[0].lower()] = (partes[1], partes[2] if len(partes) > 2 else partes[0])
    return conf


# ---------- YouTrack ----------

def bundle_da_versao():
    cfs = yt("admin/projects/WEB/customFields", {"fields": "field(name),bundle(id)", "$top": 200})
    for c in cfs:
        if c["field"]["name"] == CAMPO:
            return c["bundle"]["id"]
    erro(f'campo "{CAMPO}" não achado no projeto WEB')


def valor_existe(bundle, versao):
    vals = yt(f"admin/customFieldSettings/bundles/version/{bundle}/values",
              {"fields": "name", "$top": 2000, "query": versao})
    return any(v["name"] == versao for v in vals)


def campo(issue, nome):
    for c in issue["customFields"]:
        if c["name"] == nome:
            v = c["value"]
            return v.get("name") if isinstance(v, dict) else v
    return None


def proxima_segunda(hoje=None):
    hoje = hoje or datetime.date.today()
    return hoje + datetime.timedelta(days=(7 - hoje.weekday()) or 7)


def descricao(versao, servicos, app):
    linhas = ["--- App ---", f"Imagem do crm: {app or A_DEFINIR}", f"Vue: {A_DEFINIR}", "", "",
              "--- Insider ---", f"Imagem do crm: {versao}"]
    linhas += [f"Imagem do serviço {rot}: {versao}" for rot in servicos]
    linhas += [f"Vue: {A_DEFINIR}"]
    return "\n".join(linhas)


def mesclar(antiga, nova):
    """Mantém o que alguém já preencheu à mão: linha "chave: valor" só é trocada se estava 'a definir'."""
    if not antiga:
        return nova
    feitas = {}
    secao = ""
    for l in antiga.splitlines():
        if l.startswith("---"):
            secao = l
        elif ":" in l and A_DEFINIR not in l:
            feitas[(secao, l.split(":")[0])] = l
    saida, secao = [], ""
    for l in nova.splitlines():
        if l.startswith("---"):
            secao = l
        saida.append(feitas.get((secao, l.split(":")[0]), l) if ":" in l else l)
    return "\n".join(saida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", required=True)
    ap.add_argument("--plano", action="store_true")
    ap.add_argument("--montagem", action="store_true")
    ap.add_argument("--trocar", nargs="+", default=[], metavar="ID",
                    help="tickets cuja Versão de outra linha (ex.: vue26.4.005) pode ser trocada, já confirmado")
    a = ap.parse_args()
    RE_VERSAO.match(a.versao) or erro(f"versão inválida: {a.versao} (esperado vYY.T.NNN)")

    crm = os.environ.get("REPO") or git(".", "rev-parse", "--show-toplevel").strip()
    crm_slug = slug(crm).split("/")[1]
    conf = carregar_conf()

    # 1. Tickets aptos e os projetos onde cada um tem commit ou PR.
    aptos = yt("issues", {"query": f"project: {', '.join(PROJETOS)} State: {{{ESTADO}}}",
                          "fields": "idReadable,summary,description,customFields(name,value(name)),comments(text)",
                          "$top": 500})
    por_id = {i["idReadable"]: i for i in aptos}
    citados = {}  # slug -> ids que citam o repo no texto
    for i in aptos:
        texto = (i.get("description") or "") + " ".join(c.get("text") or "" for c in i.get("comments", []))
        for s in set(re.findall(r"bitbucket\.org/%s/([A-Za-z0-9._-]+)" % WORKSPACE, texto)):
            citados.setdefault(s.lower(), set()).add(i["idReadable"])

    clones = clones_locais(os.path.dirname(crm))
    clones[crm_slug] = crm
    achados = {}  # slug -> {id: ["commit", "PR #1"]}
    for s in sorted(set(clones) | set(citados)):
        if s in clones:
            repo = clones[s]
            ramo = ramo_de_teste(repo)
            if not ramo:
                continue
            buscar(repo)
            base = ultima_principal(repo, antes_de=a.versao if s == crm_slug else None)
            commits = ids_em_commits(repo, ramo, base)
        else:
            ramo, commits = None, set()
        try:
            prs = ids_em_prs(f"{WORKSPACE}/{s}")
        except SystemExit:
            if s in clones:
                raise
            print(f"AVISO: {s}: PRs não lidos (sem acesso?); fica pelo que o ticket cita", file=sys.stderr)
            prs = {}
        for i in por_id:
            onde = (["commit"] if i in commits else []) + (["PR " + ", ".join(f"#{n}" for n in prs[i])] if i in prs else [])
            if not onde and i in citados.get(s, ()) and s not in clones:
                onde = ["citado no ticket"]
            if onde:
                achados.setdefault(s, {})[i] = onde

    # Quem sobe na segunda. Projeto com ticket que a lista não conhece trava a gravação.
    a_confirmar = sorted(s for s in achados if s != crm_slug and s not in conf)
    servicos = [conf[s][1] for s in sorted(achados) if s != crm_slug and conf.get(s, ("",))[0] == "entra"]
    origem, so_fora = {}, {}
    for s, ids in achados.items():
        situacao = "entra" if s == crm_slug else conf.get(s, ("a confirmar",))[0]
        for i, onde in ids.items():
            alvo = origem if situacao in ("entra", "a confirmar") else so_fora
            alvo.setdefault(i, []).append(f"{s} ({'; '.join(onde)})" + ("" if situacao == "entra" else f" [{situacao}]"))
    entram = sorted(origem, key=lambda i: (i.split("-")[0], int(i.split("-")[1])))
    fora = sorted(set(por_id) - set(entram))
    # Versão de outra linha (Vue, hotfix do Vue...) no campo: trocar apaga a dela; só com confirmação.
    outra_linha = [i for i in entram if campo(por_id[i], CAMPO) and campo(por_id[i], CAMPO) != a.versao
                   and not RE_BACKEND.match(campo(por_id[i], CAMPO)) and i not in a.trocar]

    # 2. Ticket de versão.
    segunda = proxima_segunda()
    titulo = f"Versão - {segunda:%d/%m}"
    bundle = bundle_da_versao()
    tem_valor = valor_existe(bundle, a.versao)
    # Sem o valor no campo, a busca por ele é recusada pelo YouTrack: não há ticket de versão ainda.
    existente = yt("issues", {"query": f"project: PID {CAMPO}: {a.versao}",
                              "fields": "idReadable,summary,description", "$top": 5}) if tem_valor else []
    app = None
    if a.montagem:
        anterior = ultima_principal(crm, antes_de=a.versao)
        app = mais_recente_da(crm, anterior) if anterior else None
    desc = descricao(a.versao, servicos, app)
    if existente:
        desc = mesclar(existente[0].get("description"), desc)

    print(f"Versão:  {a.versao}  (campo {CAMPO}: {'já existe' if tem_valor else 'criar'})")
    print(f"Entram ({len(entram)}):")
    for i in entram:
        atual = campo(por_id[i], CAMPO)
        marca = "" if atual in (None, a.versao) else (f"  [A CONFIRMAR: tem {atual}]" if i in outra_linha else f"  [troca {atual}]")
        print(f"  {i}  {' + '.join(origem[i])}{marca}  {por_id[i]['summary'][:80]}")
    for i in sorted(so_fora):
        if i in fora:
            print(f"  fora: {i}  {' + '.join(so_fora[i])}  {por_id[i]['summary'][:80]}")
    sem = [i for i in fora if i not in so_fora]
    print(f"Ficam fora, sem commit nem PR em projeto com ambiente de teste ({len(sem)}): {' '.join(sem) or '-'}")
    print(f"Serviços na versão: {', '.join(servicos) or 'nenhum'}")
    if existente:
        print(f"Ticket de versão: {existente[0]['idReadable']} ({existente[0]['summary']}) — atualizar descrição")
    else:
        print(f"Ticket de versão: criar \"{titulo}\" no PID para {RESPONSAVEL}")
    print("  " + desc.replace("\n", "\n  "))
    if a_confirmar:
        print(f"A CONFIRMAR: {', '.join(a_confirmar)} tem ticket apto e não está em {CONF}.")
        print("  Sobe na versão de bugfix de segunda? Pergunte a quem acionou e registre lá (entra|fora).")
    if outra_linha:
        print(f"A CONFIRMAR: {' '.join(outra_linha)} já têm versão de outra linha no campo {CAMPO}; trocar apaga a dela.")
        print("  Pergunte a quem acionou; se for trocar, rode de novo com --trocar <IDs>.")
    if a.plano:
        print("(plano: nada gravado)")
        return
    if a_confirmar or outra_linha:
        erro("há projeto a confirmar; nada gravado", 5)

    # 3. Gravar.
    if not tem_valor:
        yt(f"admin/customFieldSettings/bundles/version/{bundle}/values", {"fields": "name"}, "POST",
           {"name": a.versao, "released": False, "archived": False})
    valor = {"name": CAMPO, "$type": "SingleVersionIssueCustomField", "value": {"name": a.versao}}
    for i in entram:
        if campo(por_id[i], CAMPO) != a.versao:
            yt(f"issues/{i}", {"fields": "idReadable"}, "POST", {"customFields": [valor]})

    if existente:
        pid = existente[0]["idReadable"]
        if existente[0].get("description") != desc:
            yt(f"issues/{pid}", {"fields": "idReadable"}, "POST", {"description": desc})
    else:
        projeto = yt("admin/projects", {"fields": "id,shortName", "query": "PID", "$top": 50})
        pid_id = next((p["id"] for p in projeto if p["shortName"] == "PID"), None) or erro("projeto PID não achado")
        campos = [{"name": n, "$type": "SingleEnumIssueCustomField", "value": {"name": v}} for n, v in PID.items()]
        campos += [{"name": "Responsável", "$type": "SingleUserIssueCustomField", "value": {"login": RESPONSAVEL}}, valor]
        novo = yt("issues", {"fields": "idReadable"}, "POST",
                  {"project": {"id": pid_id}, "summary": titulo, "description": desc, "customFields": campos})
        pid = novo["idReadable"]
    print(f"Pronto: {a.versao} em {len(entram)} tickets; ticket de versão {pid}")
    print(f"{YT}/issues?q=" + urllib.parse.quote(f"{CAMPO}: {a.versao}"))


if __name__ == "__main__":
    main()
