---
name: finalizar-tarefa
description: Encerra uma tarefa de vez — lê o doc de pendências dela, aponta o que ainda está aberto (próximo passo, adiados, código não commitado ou não empurrado), confirma com a pessoa e, confirmado, remove o doc num commit dizendo que a tarefa foi finalizada. Use quando a pessoa disser "vamos finalizar essa tarefa", "tarefa concluída", "pode encerrar a tarefa X", "terminamos isso" ou similar. NÃO use para pausar e retomar depois ("fechar a sessão") — isso é a skill fechar-sessao.
---

# Finalizar tarefa

Objetivo: a tarefa sai da lista de pendências sem levar junto nada que ainda devia ser feito.
Remover o doc é irreversível na prática (sobra só no histórico), por isso há uma confirmação.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: pergunta com escolha quando houver opções e aberta quando
não houver, procedência dos identificadores, escrita fora do repositório só com pedido
explícito, e saída honesta em vez de fechamento sem evidência.

## Passo 1 — Achar o doc desta tarefa

Siga `references/identificar-doc.md`. Aqui o critério "pertence" é
mais estrito que no fechamento, porque o resultado é apagar:
- A pessoa nomeou a tarefa, ou só existe um doc e dois sinais batem → é esse.
- Qualquer dúvida → pergunte qual, listando os candidatos pelo `tarefa:`.
- Nenhum doc da tarefa → diga que não há pendências registradas e não remova nada.

## Passo 2 — Levantar o que segue aberto

Do doc: "Próximo passo" não feito, "Adiado", perguntas ou decisões abertas.
Do repo, medido agora:
```bash
git status --short                          # código não commitado
git log origin/<branch>..HEAD --oneline     # commits não empurrados
git branch --list                           # branches da tarefa (ex.: parked/*)
```
Cruze com o `escopo:` do doc: mudança não commitada fora do escopo não é desta tarefa — não conte.

## Passo 3 — Apontar e confirmar

Mostre em até 5 itens, o mais importante primeiro. Separe:
- **Bloqueia finalizar:** código da tarefa não commitado. Não finalize com isso; diga como resolver.
- **Fica em aberto se finalizar:** próximo passo não feito, adiados, push pendente, branch local.

Então uma pergunta só: finalizar assim? Se não houver nada aberto, diga isso e pergunte do mesmo
jeito — apagar pede um sim explícito.

Adiados com gatilho **não se perdem**: vão no corpo do commit de remoção (passo 4), que fica no
`git log`. Se a pessoa quiser que algum continue visível, pergunte para onde (outro doc de pendências,
issue) antes de remover.

## Passo 4 — Remover, e commitar só se a pessoa quiser

**Por padrão nada é commitado.** Veja se o doc é rastreado: `git ls-files --error-unmatch <doc>`.

- **Doc local (não rastreado):** apague o arquivo (`rm`). Não há commit a fazer. Os adiados, que iriam
  no corpo do commit, vão na resposta final — é o único registro que sobra; diga isso.
- **Doc commitado:** na mesma pergunta de confirmação do passo 3, pergunte também se a remoção deve
  ser commitada ou ficar só no disco (aparece como `deleted` no `git status`). Commitar é o que deixa
  os adiados guardados no `git log`; diga isso na pergunta.

Commitando, doc por tarefa:
```bash
git rm docs/pendencias/<tarefa>.md
# se a pasta ficou vazia, o git já não a rastreia
```
Mensagem (convenção do repo se houver; senão):
```
docs(pendencias): tarefa "<tarefa>" finalizada

Entregue: <1–3 linhas, com commits curtos>
Ficou de fora, por decisão: <adiados com o gatilho de volta; "nada" se nada>
```

Doc de continuidade do repo (o CLAUDE.md manda mantê-lo): **não apague o arquivo**. Mova o bloco da
tarefa para a seção de fechados do próprio doc ("Fechado em <data>"), pelas regras dele. Commitar
segue a mesma pergunta — avise se o CLAUDE.md do repo espera o commit.

Push: só com autorização registrada para o repo; senão, avise que o commit espera o ok.

## Passo 5 — Fechar a conversa

Uma linha com o commit, e uma com o que ficou em aberto por decisão (ou "nada ficou aberto").

## O que não fazer

- Não finalizar sem o sim explícito, mesmo com tudo verde.
- Não apagar doc de outra tarefa, nem o doc de continuidade do repo.
- Não misturar código no commit de remoção.
- Não commitar sem o sim da pessoa — nem a remoção.
