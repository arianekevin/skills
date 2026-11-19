"""Sessão do Claude sem supervisão, com o passo a passo gravado na hora em <saída>.passos.jsonl.

Cada linha é um passo curto: o que o agente disse, a ferramenta que usou (com o alvo) ou o erro dela. Passo de
subagente leva "agente" com a descrição dele, para dar para ver as revisões em paralelo. O texto final da sessão
vai para o arquivo de saída, como antes.
"""
import datetime, json, os, pathlib, re, shlex, subprocess, threading

SUBAGENT = ("Task", "Agent")


def steps(ev, agents):
    now = f"{datetime.datetime.now():%H:%M:%S}"
    who = agents.get(ev.get("parent_tool_use_id"))
    base = {"t": now, **({"agente": who} if who else {})}
    if ev.get("type") == "assistant":
        for c in (ev.get("message") or {}).get("content") or []:
            if c.get("type") == "text" and c.get("text", "").strip():
                yield {**base, "tipo": "texto", "texto": c["text"].strip()[:400]}
            elif c.get("type") == "tool_use":
                i = c.get("input") or {}
                if c.get("name") in SUBAGENT:
                    agents[c.get("id")] = (i.get("description") or "subagente")[:60]
                target = i.get("description") or i.get("command") or i.get("file_path") or i.get("pattern") or i.get("path") or i.get("url") or ""
                yield {**base, "tipo": "ferramenta", "nome": c.get("name"), "texto": str(target)[:300]}
    elif ev.get("type") == "user":
        for c in (ev.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                txt = c.get("content")
                txt = txt if isinstance(txt, str) else " ".join(x.get("text", "") for x in txt or [] if isinstance(x, dict))
                yield {**base, "tipo": "erro", "texto": txt.strip()[:300]}


def run(cmd, prompt, cwd, env, out, timeout):
    """Roda `cmd -p prompt` em stream. Devolve o código de saída; estourou o tempo: mata a sessão e levanta
    TimeoutExpired, como o subprocess.run."""
    out = pathlib.Path(out)
    proc = subprocess.Popen([*cmd, "-p", prompt, "--output-format", "stream-json", "--verbose"], cwd=cwd, env=env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    timer = threading.Timer(timeout, proc.kill)
    timer.start()
    final, agents = [], {}
    try:
        with open(out.with_suffix(".passos.jsonl"), "w") as fh:
            for line in proc.stdout:
                try:
                    ev = json.loads(line)
                except ValueError:
                    final.append(line)
                    continue
                if ev.get("type") == "result":
                    final.append(ev.get("result") or "")
                for s in steps(ev, agents):
                    fh.write(json.dumps(s, ensure_ascii=False) + "\n")
                    fh.flush()
        proc.wait()
    finally:
        timer.cancel()
        out.write_text("".join(final))
    if proc.returncode < 0:
        raise subprocess.TimeoutExpired(proc.args, timeout)
    return proc.returncode


# Limite de uso da conta: com ele estourado, todo `claude -p` volta na hora com um texto como "You've hit your weekly
# limit · resets Nov 22, 4pm". A sessão não revisou nada; o que ela devolveu não é veredito, falha nem tentativa.
LIMITE = re.compile(r"hit your (?:\w+ )?limit|usage limit reached", re.I)
RESET = re.compile(r"resets\s+(?:([A-Z][a-z]{2})[a-z]*\s+(\d{1,2}),?\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap]m)", re.I)
MESES = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}


def reset_em(texto, agora=None):
    """Quando o limite volta, pelo texto ("resets Nov 22, 4pm", "resets 4:30pm"), na hora local, mais 5 minutos de folga.
    Sem data legível, ou no passado: daqui a 1 hora."""
    agora = agora or datetime.datetime.now()
    fallback = agora + datetime.timedelta(hours=1)
    m = RESET.search(texto)
    if not m:
        return fallback
    mes, dia, h, mi, ap = m.groups()
    h = int(h) % 12 + (12 if ap.lower() == "pm" else 0)
    try:
        if mes and mes[:3].lower() in MESES:
            t = datetime.datetime(agora.year, MESES[mes[:3].lower()], int(dia), h, int(mi or 0))
            if t < agora - datetime.timedelta(days=1):
                t = t.replace(year=agora.year + 1)
        else:
            t = agora.replace(hour=h, minute=int(mi or 0), second=0, microsecond=0)
            if t <= agora:
                t += datetime.timedelta(days=1)
    except ValueError:
        return fallback
    t += datetime.timedelta(minutes=5)
    return t if t > agora else fallback


def limite(out):
    """O texto final da sessão em `out` é o aviso de limite de uso? Devolve o texto, ou None. Só vale texto curto:
    uma revisão de verdade que cite a frase num relatório longo não é o limite."""
    try:
        texto = pathlib.Path(out).read_text().strip()
    except OSError:
        return None
    return texto if len(texto) < 600 and LIMITE.search(texto) else None


def pausar(texto, log):
    """Registra uma linha e, com $LIMITE_PAUSA, grava o arquivo que faz as próximas rodadas saírem quietas até o reset.
    Com $LIMITE_CMD (ex.: um gestor de várias contas), quem registra é ele: `$LIMITE_CMD pausar <texto>`, no mesmo
    ambiente da sessão, para saber qual conta estourou."""
    ate = reset_em(texto)
    log(f"limite de uso da conta: rodada parada até {ate:%Y-%m-%d %H:%M}")
    cmd = os.environ.get("LIMITE_CMD")
    if cmd:
        subprocess.run([*shlex.split(cmd), "pausar", texto[:500]], timeout=30, check=False)
        return
    alvo = os.environ.get("LIMITE_PAUSA")
    if alvo:
        arq = pathlib.Path(alvo).expanduser()
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps({"ate": ate.strftime("%Y-%m-%dT%H:%M"), "motivo": texto[:200],
                                   "quando": f"{datetime.datetime.now():%Y-%m-%d %H:%M}"}, ensure_ascii=False))


def pausada():
    """Há pausa por limite de uso ainda valendo em $LIMITE_PAUSA? Arquivo ausente ou ilegível: não."""
    alvo = os.environ.get("LIMITE_PAUSA")
    try:
        ate = datetime.datetime.fromisoformat(json.loads(pathlib.Path(alvo).expanduser().read_text())["ate"])
    except (TypeError, OSError, ValueError, KeyError):
        return False
    return ate > datetime.datetime.now()
