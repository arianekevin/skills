# vigia

Mod do Claude Code: um painel ao lado do chat que acompanha **outra** sessão e explica o que ela
está fazendo e por quê — sem você ler o terminal dela.

- Lê o histórico (`~/.claude/projects/*/*.jsonl`) da sessão escolhida a cada 4 s, só o que é novo. O histórico
  tem tudo o que a sessão fez: comando inteiro, resultado, raciocínio. Fica de fora o que os subagentes dela fazem
  por dentro (só entra o pedido e a resposta).
- Lê o plano da sessão: o documento de plano que ela escreveu (`docs/plans/`, `PLANO-*`, `pendencias/`, ou o
  plano aprovado no modo plano) e os pedidos da pessoa. O que está no plano não vira alerta.
- **CUIDADO**, na hora e sem IA, para o que apaga ou não tem volta: push forçado, push direto na principal, apagar
  branch, `reset --hard`, `rm -rf` fora de pasta temporária, `checkout --`/`restore`/`clean`, `DROP`/`TRUNCATE`/
  `DELETE` sem `WHERE`, banco remoto, produção, kubectl/helm, publicar pacote, editar migration que já está na
  principal. Também é CUIDADO, julgado pelo Haiku, a mensagem para outra sessão que muda o rumo do trabalho de lá.
- **Atenção**, julgada pelo Haiku contra o plano: o agente diz que terminou ou segue em frente com teste vermelho
  em aberto; desliga ou afrouxa teste para ficar verde; push, merge, tag, chamada que altera serviço externo ou
  migration que apaga dado sem o plano cobrir; faz o contrário de uma regra que a pessoa deu.
- Não alerta: teste vermelho enquanto o agente corrige, commit, rebase, migration nova prevista no plano.
- O Haiku resume cada bloco de passos: o que fez e por quê (do plano, do pedido, do raciocínio ou da fala; sem nada
  escrito, "motivo não declarado").
- CUIDADO vira toast e, no macOS, notificação do sistema, com o nome da sessão.

## Instalação

```
/plugin marketplace add arianekevin/skills
/plugin install vigia@skills
```

Requer `python3` no PATH. Reinicie a sessão depois de instalar.

## Uso

```
/vigia                    # lista as sessões com atividade nas últimas 6 h
/vigia <id> [nome]        # passa a vigiar essa sessão (prefixo do id basta); nome opcional, ex.: ndesk
/vigia parar [nome|id]    # para uma sessão, ou todas sem argumento
/vigia limpar             # esvazia o painel
```

Até 3 sessões ao mesmo tempo, num painel só: lado a lado quando o painel tem largura (45 colunas por sessão),
uma embaixo da outra quando não tem. Cada uma mostra os itens mais recentes que cabem na altura.

## Ajustar os alertas

- Por padrão (sem IA): `SINAIS_BASH` em `bin/vigia.py` (`True` = CUIDADO na hora; `False` = o Haiku julga contra o
  plano).
- Por julgamento (Haiku): `REGRAS` em `hooks/register.tsx`.
