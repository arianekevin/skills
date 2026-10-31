---
name: finalizar-tarefa
description: Encerra uma tarefa de vez — lê o doc de pendências dela, aponta o que ainda está aberto (próximo passo, adiados, código não commitado ou não empurrado), confirma com a pessoa e, confirmado, apaga o doc — com commit ou só no disco, conforme o modo do repo. Use quando a pessoa disser "vamos finalizar essa tarefa", "tarefa concluída", "pode encerrar a tarefa X", "terminamos isso" ou similar; quando perguntar se acabou ("fizemos tudo?", "falta alguma coisa?", "acabou?", "terminou?") e existir um doc em docs/pendencias/; ou quando o trabalho da sessão cumprir o último item a fazer de um doc de pendências. NÃO use para pausar e retomar depois ("fechar a sessão") — isso é a skill fechar-sessao.
---

# Finalizar tarefa

Objetivo: a tarefa sai da lista de pendências sem levar junto nada que ainda devia ser feito.
Remover o doc é irreversível na prática (sobra só no histórico), por isso há uma confirmação.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: pergunta com escolha quando houver opções e aberta quando
não houver, procedência dos identificadores, escrita fora do repositório só com pedido
explícito, e saída honesta em vez de fechamento sem evidência.

## Como ela chega aqui

Nem sempre alguém diz "finalizar". Três entradas:
- **Pedido explícito** ("vamos finalizar essa tarefa") → siga os passos.
- **Pergunta se acabou** ("fizemos tudo?", "falta alguma coisa?") → faça os passos 1 e 2 e responda a
  pergunta. Sobrou algo a fazer: liste e pare — não proponha finalizar. Não sobrou nada: diga isso e
  siga para o passo 3.
- **A sessão cumpriu o último item a fazer do doc** → ao terminar esse trabalho, diga que o doc ficou
  sem nada a fazer e siga para o passo 3.

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
git worktree list                           # worktree da tarefa com trabalho sem commit ou sem remota
```
O doc e o trabalho podem estar em outra worktree que não a atual: meça lá (`git -C <worktree> status`). Cruze com o `escopo:` do doc: mudança não commitada fora do escopo, ou de outra sessão na mesma pasta, não é desta tarefa — não conte.

## Passo 3 — Apontar e confirmar

Mostre em até 5 itens, o mais importante primeiro. Separe:
- **Bloqueia finalizar:** código da tarefa não commitado. Não finalize com isso; diga como resolver.
- **Fica em aberto se finalizar:** próximo passo não feito, adiados, push pendente, branch local.

Então uma pergunta só: finalizar assim? Se não houver nada aberto, diga isso e pergunte do mesmo
jeito — apagar pede um sim explícito.

Adiados com gatilho **não se perdem**: vão na resposta final (doc local) ou no corpo do commit de
remoção (doc já versionado, passo 4). Se a pessoa quiser que algum continue visível, pergunte para onde (outro doc de pendências,
issue) antes de remover.

## Passo 4 — Remover, seguindo o modo do repo

O modo é o que a `fechar-sessao` gravou: `git config --local --get pendencias.modo`.

- **`local`, ou doc não rastreado:** apague o arquivo (`rm`). Não há commit. Os adiados vão na
  resposta final — é o único registro que sobra; diga isso.
- **`compartilhado`:** commite a remoção (abaixo), sem perguntar de novo — o sim do passo 3 basta.
- **Doc rastreado sem modo gravado:** na mesma pergunta do passo 3, pergunte se a remoção deve ser
  commitada ou ficar só no disco. Commitar é o que deixa os adiados no `git log`; diga isso.

Commitando, doc por tarefa:
```bash
git rm docs/pendencias/<tarefa>.md
git commit -m "..." -- docs/pendencias/<tarefa>.md   # só o doc; nada preparado no índice (pasta pode ser compartilhada)
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
segue a regra do repo.

Push: só com autorização registrada para o repo; senão, o commit sobe no próximo push do projeto.

## Passo 5 — Fechar a conversa

Uma linha com o commit, e uma com o que ficou em aberto por decisão (ou "nada ficou aberto").

## O que não fazer

- Não finalizar sem o sim explícito, mesmo com tudo verde.
- Não apagar doc de outra tarefa, nem o doc de continuidade do repo.
- Não misturar código no commit de remoção.
- Não commitar a remoção contra o modo gravado do repo.
