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

Regras (as mesmas do CONTINUIDADE do ndesk, que funcionam):
1. **Fato verificado, não intenção.** "1405 testes verdes" vale; "deve estar passando" não. O que não
   foi medido diz que não foi medido.
2. **Decisão leva o porquê e o gatilho de revisita.** "Adiado" sem "volta quando…" vira ruído.
3. **Item resolvido muda de seção, não some.** De "Próximo passo" para "Feito"; de "Adiado" para
   "Combinado" se foi decidido de vez.
4. Datas absolutas (`2026-09-28`), nunca "hoje" ou "amanhã".
5. "Onde paramos" no topo: 2–4 linhas que bastam para começar. O primeiro passo concreto ao voltar,
   incluindo o que depende da pessoa (push esperando ok, decisão pendente).

Doc por tarefa: atualize `atualizado:` e o `escopo:` se cresceu. Doc do repo: siga o formato dele.

## Passo 4 — Commitar ou manter local: a pessoa decide

**Por padrão o doc não é commitado.** Depois de escrever, pergunte uma vez: commitar ou manter local?
Se já houver outra pergunta a fazer (passo 1), junte as duas numa chamada só.

- Doc de continuidade do repo cujo CLAUDE.md manda atualizar "no mesmo commit": pergunte do mesmo
  jeito, mas diga na pergunta que a regra do repo espera o commit.
- **Commitar:** commit só com o doc (e nada mais), na convenção de mensagem do repo. Sem convenção:
  `docs(pendencias): <tarefa> — onde paramos em AAAA-MM-DD`. Push só se o repo tiver autorização
  registrada (memória ou CLAUDE.md); senão, o push fica em "Onde paramos" esperando o ok.
- **Manter local:** não faça `git add`. Diga que o arquivo aparece como não rastreado (ou modificado)
  no `git status` e que só existe nesta máquina.

Mudanças de código não commitadas: **nunca** as inclua. Registre-as em "Estado do ambiente" e avise.

## Passo 5 — Fechar a conversa

Três linhas, no máximo:
- o caminho do doc (criado ou atualizado; commitado ou local);
- o primeiro passo ao retomar;
- o que ficou pendente da pessoa (push, decisão), se houver.

## O que não fazer

- Não escrever num doc de outra tarefa porque "é parecido".
- Não resumir a conversa inteira: o doc é para retomar, não para contar.
- Não apagar nada — remover o doc é da `finalizar-tarefa`.
- Não perguntar o que dá para medir (`git`, arquivos). Perguntar só a ambiguidade do passo 1 e o
  commit-ou-local do passo 4 — juntas, quando houver as duas.
- Não commitar o doc sem o sim da pessoa.
