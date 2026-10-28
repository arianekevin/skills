"""Sessão do Claude sem supervisão, com o passo a passo gravado na hora em <saída>.passos.jsonl.

Cada linha é um passo curto: o que o agente disse, a ferramenta que usou (com o alvo) ou o erro dela. Passo de
subagente leva "agente" com a descrição dele, para dar para ver as revisões em paralelo. O texto final da sessão
vai para o arquivo de saída, como antes.
"""
import datetime, json, pathlib, subprocess, threading

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
