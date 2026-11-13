# vigia

Mod do Claude Code: um painel ao lado do chat que acompanha **outra** sessão e explica o que ela
está fazendo e por quê — sem você ler o terminal dela.

- Lê o histórico (`~/.claude/projects/*/*.jsonl`) da sessão escolhida a cada 4 s, só o que é novo.
- Um script Python, sem IA, marca os alertas por padrão: **CUIDADO** (irreversível, sai da máquina
  — push, merge, tag, POST/PUT/DELETE, kubectl —, mexe em dado: migration, banco remoto) e
  **Atenção** (commit, rebase, teste vermelho).
- O Haiku resume cada bloco de passos: o que fez, por quê (tirado do pedido, do raciocínio ou da
  fala; sem nada escrito, "motivo não declarado") e CUIDADO quando a sessão decidiu sozinha algo de
  arquitetura ou regra, saiu do escopo ou mandou dado de cliente para IA.
- CUIDADO vira toast e, no macOS, notificação do sistema.

## Instalação

```
/plugin marketplace add arianekevin/skills
/plugin install vigia@skills
```

Requer `python3` no PATH. Reinicie a sessão depois de instalar.

## Uso

```
/vigia            # lista as sessões com atividade nas últimas 6 h
/vigia <id>       # liga o painel nessa sessão (prefixo do id basta)
/vigia parar
/vigia limpar     # esvazia o painel
```

## Ajustar os alertas

- Por padrão (sem IA): `CUIDADO_BASH` e `ATENCAO_BASH` em `bin/vigia.py`.
- Por julgamento (Haiku): `REGRAS` em `hooks/register.tsx`.
