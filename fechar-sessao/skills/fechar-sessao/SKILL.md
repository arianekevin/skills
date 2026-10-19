---
name: fechar-sessao
description: Registra onde a sessão parou para a próxima retomar sem perder nada — o que foi feito, combinado, adiado e o próximo passo — no doc de pendências da tarefa (docs/pendencias/<tarefa>.md) ou no doc de continuidade que o repo já exige. Use quando a pessoa disser "vamos fechar essa sessão", "fechar por hoje", "encerrar a sessão", "salva onde paramos", "deixa pronto pra retomar amanhã" ou similar. NÃO use para "finalizar a tarefa" (entrega concluída) — isso é a skill finalizar-tarefa.
---

# Fechar sessão

Objetivo: a próxima sessão, sem nada desta conversa, lê um arquivo e sabe onde retomar.
Registro, não relatório: o que a pessoa precisa para continuar, não o que a sessão fez de bonito.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: pergunta com escolha quando houver opções e aberta quando
não houver, procedência dos identificadores, escrita fora do repositório só com pedido
explícito, e saída honesta em vez de fechamento sem evidência.

## Passo 1 — Achar o destino certo

Siga `references/identificar-doc.md`. Resumo:
- Repo com doc de continuidade obrigatório (o CLAUDE.md manda manter) → é nele, pelas regras dele.
- Senão → `docs/pendencias/<tarefa>.md`, um por tarefa.
- Decida se um doc existente **pertence** a esta tarefa pelos sinais (tarefa nomeada, branch, escopo,
  continuidade). Ambíguo → uma pergunta. Nenhum → cria novo.

## Passo 2 — Levantar o material, com fato e não memória

Da conversa: o que foi feito, decidido (com o porquê), adiado (com o gatilho de volta), o que a
pessoa pediu e não foi feito, perguntas abertas.

Do repo, medido agora:
```bash
git status --short                 # não commitado
git log origin/<branch>..HEAD --oneline   # não empurrado (se houver remoto)
git branch --list                  # branches locais criadas na sessão
git log --since=<atualizado:> --oneline   # o que a sessão commitou
```
E o ambiente de que o trabalho depende (serviços que precisam estar no ar, como subir) — só se mudou
ou se a próxima sessão vai tropeçar nele.

## Passo 3 — Escrever

Regras:
1. **Fato verificado, não intenção.** "1405 testes verdes" vale; "deve estar passando" não. O que não
   foi medido diz que não foi medido.
2. **Decisão leva o porquê e o gatilho de revisita.** "Adiado" sem "volta quando…" vira ruído.
3. **Item resolvido muda de seção, não some.** De "Próximo passo" para "Feito"; de "Adiado" para
   "Combinado" se foi decidido de vez.
4. Datas absolutas (`2026-09-28`), nunca "hoje" ou "amanhã".
5. "Onde paramos" no topo: 2–4 linhas que bastam para começar. O primeiro passo concreto ao voltar,
   incluindo o que depende da pessoa (push esperando ok, decisão pendente).

Doc por tarefa: atualize `atualizado:` e o `escopo:` se cresceu. Doc do repo: siga o formato dele.

**Doc sem nada a fazer** — próximo passo cumprido, nenhum adiado esperando gatilho, nenhuma pergunta
aberta: a tarefa acabou. Não feche a sessão nele; siga a `finalizar-tarefa`, que pede o sim e apaga.

## Passo 4 — Local ou junto do projeto: escolhido uma vez por repo

A escolha fica guardada no próprio repo, só nesta máquina:
```bash
git config --local --get pendencias.modo    # local | compartilhado | (vazio)
```

**Vazio — primeira sessão fechada neste repo:** pergunte uma vez, com as duas opções:
- **Local** — o doc é trabalho entre sessões de quem está na máquina; nunca vai para commit nem push.
- **Junto do projeto** — o doc é commitado e sobe com o resto do trabalho.

Grave a resposta (`git config --local pendencias.modo local|compartilhado`) e diga que dá para mudar
pedindo. Daí em diante, siga o modo gravado sem perguntar.

**Modo `local`:**
- Se `docs/pendencias/` não estiver em `.git/info/exclude`, acrescente a linha — ignore só desta
  máquina, para o doc não entrar num commit por engano. Não mexa no `.gitignore`, que é compartilhado.
- Doc já rastreado pelo git: não o tire do índice por conta própria. Avise uma vez que ele está
  versionado e que `git rm --cached <doc>` o torna local.

**Modo `compartilhado`:**
- Tire `docs/pendencias/` do `.git/info/exclude`, se estiver lá.
- Commit só com o doc (e nada mais), na convenção de mensagem do repo. Sem convenção:
  `docs(pendencias): <tarefa> — onde paramos em AAAA-MM-DD`.
- Push: se o repo tem autorização registrada (memória ou CLAUDE.md), suba; senão, o commit sobe no
  próximo push do projeto — não peça push só por causa do doc.

**Pedido explícito diferente** ("esse não commita", "dessa vez sobe"): vale só para esta vez. Muda o
modo gravado apenas se a pessoa disser que é dali em diante.

**Doc de continuidade do repo** (o CLAUDE.md manda manter): não pergunte nem grave modo — a regra do
repo decide, e push só com autorização registrada.

Mudanças de código não commitadas: **nunca** as inclua. Registre-as em "Estado do ambiente" e avise.

## Passo 5 — Fechar a conversa

Três linhas, no máximo:
- o caminho do doc (criado ou atualizado);
- o primeiro passo ao retomar;
- o que ficou pendente da pessoa (push, decisão), se houver.

## O que não fazer

- Não escrever num doc de outra tarefa porque "é parecido".
- Não resumir a conversa inteira: o doc é para retomar, não para contar.
- Não apagar nada — remover o doc é da `finalizar-tarefa`.
- Não perguntar o que dá para medir (`git`, arquivos). Perguntar só a ambiguidade do passo 1 e o
  modo do passo 4 na primeira vez do repo — juntas, quando houver as duas.
- Não contrariar o modo gravado sem pedido explícito.
