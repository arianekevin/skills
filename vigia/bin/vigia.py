#!/usr/bin/env python3
"""Lê o histórico (.jsonl) de outra sessão do Claude Code e devolve os passos novos.

Uso:
  vigia.py ler <arquivo.jsonl> <offset>   offset -1 = começa perto do fim
  vigia.py listar                          sessões com atividade recente
  vigia.py achar <prefixo-do-id>           caminho do .jsonl

Saída sempre em JSON. Os alertas por padrão (CUIDADO / Atenção) são decididos
aqui, sem IA; o julgamento fica para o Haiku no mod.
"""
import datetime
import glob
import json
import os
import re
import sys

PROJETOS = os.path.expanduser("~/.claude/projects")
INICIO_BYTES = 150_000  # ao ligar, olha só o fim recente
MAX_TEXTO = 1200

# --- alertas por padrão -----------------------------------------------------
# (nível, motivo, regex) — testados no comando do Bash
CUIDADO_BASH = [
    ("irreversível", r"^git(\s+-C\s+\S+)?\s+push\b[^|;&]*(--force\b|--force-with-lease\b|\s-f\b|\s\+\S)"),
    ("irreversível", r"^git(\s+-C\s+\S+)?\s+reset\s+--hard"),
    ("irreversível", r"^rm\s+-[a-zA-Z]*r[a-zA-Z]*f|^rm\s+-[a-zA-Z]*f[a-zA-Z]*r"),
    ("irreversível", r"^git(\s+-C\s+\S+)?\s+branch\s+-D\b|^git(\s+-C\s+\S+)?\s+push\b[^|;&]*(--delete|\s:\S)"),
    ("irreversível", r"^git(\s+-C\s+\S+)?\s+worktree\s+remove|^git(\s+-C\s+\S+)?\s+clean\s+-[a-zA-Z]*f"),
    ("irreversível", r"^git(\s+-C\s+\S+)?\s+checkout\s+--\s|^git(\s+-C\s+\S+)?\s+restore\s+(?!--staged)"),
    ("irreversível", r"\b(DROP\s+(TABLE|DATABASE|SCHEMA|COLUMN)|TRUNCATE\s+TABLE?)\b"),
    ("irreversível", r"\bDELETE\s+FROM\s+\S+\s*(;|\"|'|$)"),
    ("sai da máquina", r"^git(\s+-C\s+\S+)?\s+push\b"),
    ("sai da máquina", r"^git(\s+-C\s+\S+)?\s+merge\b|^gh\s+pr\s+merge"),
    ("sai da máquina", r"^git(\s+-C\s+\S+)?\s+tag\b(?!.*\s(-l|--list|--sort\S*|-n\d*|--contains|--merged|--points-at)\b)(?=\s+\S)"),
    ("sai da máquina", r"^curl\b.*(-X\s*(POST|PUT|PATCH|DELETE)\b|--data(-\w+)?\b|\s-d\s|\s-F\s)"),
    ("sai da máquina", r"\b(kubectl\s+(apply|delete|rollout|scale)|helm\s+(upgrade|install|uninstall))\b"),
    ("sai da máquina", r"^npm\s+publish\b|^docker\s+push\b"),
    ("mexe em dado", r"\bflyway\b[^|;&]*migrate|alembic\s+upgrade|\bmigrate\b.*--prod"),
    ("mexe em dado", r"\b(psql|mysql|mongosh?|redis-cli)\b(?![^|;&]*(localhost|127\.0\.0\.1))[^|;&]*-h\s*\S"),
    ("mexe em dado", r"\bprod(u[cç][aã]o)?\b[^|;&]*\b(psql|ssh|mysql|mongo)|\b(ssh|psql)\b[^|;&]*\bprod"),
]
ATENCAO_BASH = [
    ("commit", r"^git(\s+-C\s+\S+)?\s+commit\b"),
    ("rebase", r"^git(\s+-C\s+\S+)?\s+rebase\b"),
]
MIGRATION_PATH = re.compile(r"(db/migration|/migrations?/|alembic/versions|/V\d+(_\d+)*__\w+\.sql$)", re.I)
FALHA_RESULTADO = re.compile(
    r"(BUILD FAILURE|Tests run:.*(Failures|Errors): [1-9]|\b[1-9]\d* (failed|failing)\b|"
    r"FAIL(ED)?\b.*\btest|npm ERR!|Traceback \(most recent call last\)|error TS\d+)",
    re.I,
)

CUIDADO_RX = [(m, re.compile(r, re.I)) for m, r in CUIDADO_BASH]
ATENCAO_RX = [(m, re.compile(r, re.I)) for m, r in ATENCAO_BASH]


def cortar(s, n=MAX_TEXTO):
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def hora(ts):
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return d.astimezone().strftime("%H:%M")
    except Exception:
        return ""


HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\s*(\n|$)", re.S)
ASPAS = re.compile(r"'[^'\n]*'|\"(?:[^\"\\\n]|\\.)*\"")


def segmentos(cmd):
    """Quebra o comando em comandos simples, sem corpo de heredoc nem texto entre aspas
    (mensagem de commit, script inline), para o padrão não casar com prosa."""
    cmd = HEREDOC.sub("\n", cmd)
    cmd = ASPAS.sub(lambda m: m.group(0) if m.group(0).startswith('"$') else "''", cmd)
    return [x.strip() for x in re.split(r"&&|\|\||[;|\n(){}]", cmd) if x.strip()]


def alerta_bash(cmd):
    segs = segmentos(cmd)
    for motivo, rx in CUIDADO_RX:
        for sg in segs:
            if rx.search(sg):
                return {"nivel": "cuidado", "motivo": motivo, "trecho": cortar(sg, 140)}
    for motivo, rx in ATENCAO_RX:
        for sg in segs:
            if rx.search(sg):
                return {"nivel": "atencao", "motivo": motivo, "trecho": cortar(sg, 140)}
    return None


def descrever_ferramenta(nome, inp):
    inp = inp or {}
    base = lambda p: os.path.basename(p or "")
    if nome == "Bash":
        return inp.get("description") or cortar(inp.get("command"), 160)
    if nome in ("Edit", "MultiEdit"):
        return f"Edita {base(inp.get('file_path'))}"
    if nome == "Write":
        return f"Escreve {base(inp.get('file_path'))}"
    if nome == "Read":
        return f"Lê {base(inp.get('file_path'))}"
    if nome in ("Grep", "Glob"):
        return f"Procura {cortar(inp.get('pattern'), 80)}"
    if nome == "Agent":
        return f"Agente: {inp.get('description', '')}"
    if nome == "SendMessage":
        return f"Mensagem para {inp.get('to', '?')}"
    if nome == "Skill":
        return f"Skill {inp.get('skill', '')}"
    if nome == "AskUserQuestion":
        qs = inp.get("questions") or []
        return "Pergunta: " + cortar(qs[0].get("question", "") if qs else "", 200)
    d = inp.get("description") or inp.get("prompt") or ""
    return f"{nome}" + (f": {cortar(d, 120)}" if d else "")


BASH_IDS = set()  # só resultado de Bash conta como falha (Read de código com "FAILED" não)


def passos_da_linha(obj):
    tipo = obj.get("type")
    ts = hora(obj.get("timestamp", ""))
    msg = obj.get("message") or {}
    conteudo = msg.get("content")
    if obj.get("isSidechain"):
        return []
    out = []
    if tipo == "user":
        if isinstance(conteudo, str):
            t = conteudo.strip()
            if t and not t.startswith("<") and not obj.get("isMeta"):
                out.append({"tipo": "pedido", "texto": cortar(t), "hora": ts})
        elif isinstance(conteudo, list):
            for b in conteudo:
                if b.get("type") == "text":
                    t = (b.get("text") or "").strip()
                    if t and not t.startswith("<") and not obj.get("isMeta"):
                        out.append({"tipo": "pedido", "texto": cortar(t), "hora": ts})
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in BASH_IDS:
                    c = b.get("content")
                    if isinstance(c, list):
                        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                    c = c or ""
                    m = FALHA_RESULTADO.search(c)
                    if m:
                        ini = max(0, m.start() - 150)
                        out.append({
                            "tipo": "falha",
                            "texto": cortar(c[ini: m.end() + 250], 400),
                            "hora": ts,
                            "alerta": {"nivel": "atencao", "motivo": "falha ou teste vermelho"},
                        })
    elif tipo == "assistant" and isinstance(conteudo, list):
        for b in conteudo:
            bt = b.get("type")
            if bt == "text":
                t = (b.get("text") or "").strip()
                if t:
                    out.append({"tipo": "fala", "texto": cortar(t, 2500), "hora": ts})
            elif bt == "thinking":
                t = (b.get("thinking") or "").strip()
                if t:
                    out.append({"tipo": "raciocinio", "texto": cortar(t, 600), "hora": ts})
            elif bt == "tool_use":
                nome = b.get("name", "")
                inp = b.get("input") or {}
                p = {"tipo": "comando", "texto": descrever_ferramenta(nome, inp), "hora": ts}
                if nome == "Bash":
                    BASH_IDS.add(b.get("id"))
                    cmd = inp.get("command") or ""
                    p["cmd"] = cortar(cmd, 300)
                    a = alerta_bash(cmd)
                    if a:
                        p["alerta"] = a
                elif nome in ("Write", "Edit", "MultiEdit") and MIGRATION_PATH.search(inp.get("file_path") or ""):
                    p["alerta"] = {"nivel": "cuidado", "motivo": "migration"}
                elif nome == "SendMessage":
                    p["alerta"] = {"nivel": "atencao", "motivo": "mensagem para outra sessão"}
                out.append(p)
    return out


def _ids_path(caminho):
    d = os.path.expanduser("~/.cache/vigia")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, os.path.basename(caminho) + ".bash-ids")


def ler(caminho, offset):
    try:
        BASH_IDS.update(open(_ids_path(caminho)).read().split())
    except OSError:
        pass
    r = _ler(caminho, offset)
    try:
        with open(_ids_path(caminho), "w") as f:
            f.write("\n".join(list(BASH_IDS)[-300:]))
    except OSError:
        pass
    return r


def _ler(caminho, offset):
    tam = os.path.getsize(caminho)
    cortado = False
    if offset < 0:
        offset = max(0, tam - INICIO_BYTES)
        cortado = offset > 0
    if offset > tam:  # arquivo trocado/recriado
        offset = 0
    with open(caminho, "rb") as f:
        f.seek(offset)
        dados = f.read()
    fim = dados.rfind(b"\n")
    if fim < 0:
        return {"offset": offset, "passos": []}
    bloco = dados[: fim + 1]
    novo = offset + fim + 1
    linhas = bloco.split(b"\n")
    if cortado:
        linhas = linhas[1:]  # primeira linha pode estar cortada
    passos = []
    for ln in linhas:
        if not ln.strip():
            continue
        try:
            obj = json.loads(ln)
        except Exception:
            continue
        passos.extend(passos_da_linha(obj))
    return {"offset": novo, "passos": passos}


def ultimo_pedido(caminho):
    try:
        with open(caminho, "rb") as f:
            f.seek(max(0, os.path.getsize(caminho) - 400_000))
            linhas = f.read().split(b"\n")[1:]
    except Exception:
        return ""
    for ln in reversed(linhas):
        try:
            obj = json.loads(ln)
        except Exception:
            continue
        for p in passos_da_linha(obj):
            if p["tipo"] == "pedido":
                return p["texto"]
    return ""


def listar(excluir):
    arqs = glob.glob(os.path.join(PROJETOS, "*", "*.jsonl"))
    agora = datetime.datetime.now().timestamp()
    recentes = sorted(
        (a for a in arqs if agora - os.path.getmtime(a) < 6 * 3600 and excluir not in a),
        key=os.path.getmtime,
        reverse=True,
    )[:8]
    out = []
    for a in recentes:
        out.append({
            "id": os.path.basename(a)[:8],
            "caminho": a,
            "pasta": os.path.basename(os.path.dirname(a)),
            "mexida": datetime.datetime.fromtimestamp(os.path.getmtime(a)).strftime("%H:%M"),
            "ultimo_pedido": cortar(ultimo_pedido(a), 110),
        })
    return out


def achar(prefixo):
    if os.path.isfile(prefixo):
        return prefixo
    arqs = glob.glob(os.path.join(PROJETOS, "*", prefixo + "*.jsonl"))
    arqs.sort(key=os.path.getmtime, reverse=True)
    return arqs[0] if arqs else ""


def main():
    acao = sys.argv[1] if len(sys.argv) > 1 else ""
    if acao == "ler":
        caminho, offset = sys.argv[2], int(sys.argv[3])
        r = ler(caminho, offset)
        if offset < 0:
            r["pedido"] = ultimo_pedido(caminho)
        print(json.dumps(r, ensure_ascii=False))
    elif acao == "listar":
        print(json.dumps(listar(sys.argv[2] if len(sys.argv) > 2 else "\0"), ensure_ascii=False))
    elif acao == "achar":
        print(json.dumps({"caminho": achar(sys.argv[2])}))
    else:
        print(json.dumps({"erro": "uso: ler|listar|achar"}))
        sys.exit(2)


if __name__ == "__main__":
    main()
