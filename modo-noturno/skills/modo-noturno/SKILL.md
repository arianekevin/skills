---
name: modo-noturno
description: "Toca sozinha o trabalho da sessão enquanto o dev dorme: faz tudo que já está decidido sem interromper, decide o que é pequeno pelo padrão sensato e anota, e congela o que é de grande impacto como pergunta para a manhã — implementando a opção recomendada numa branch à parte quando é seguro. Só para quando não sobra nada que dê para fazer sozinha, e deixa o relatório no chat e no doc de pendências da tarefa. Use quando o dev pedir 'modo noturno', 'entra em modo noturno', 'vou dormir, toca aí', 'faz tudo que conseguir sem mim', 'vou sair, segue sozinha', 'roda a pauta', 'executa as melhorias'. Também use de dia, quando ele pedir para deixar algo para a noite: 'anota pra rodar à noite', 'põe na pauta', 'deixa pra noite', 'o que tem pra noite'."
---

# Modo noturno

## O que esta skill faz

O dev vai dormir no meio de um trabalho. Você continua **o trabalho desta sessão** — o que já foi
combinado na conversa, no doc de pendências, no plano — até onde dá para ir sozinha, e deixa para a
manhã só o que realmente precisa dele.

Duas falhas opostas, e as duas custam a noite:

- **Parar cedo demais** — perguntar algo que tinha resposta sensata, e ele acorda com oito horas de
  nada feito e uma pergunta boba esperando.
- **Decidir o que não era seu** — escolher a arquitetura, apagar dado, publicar, e ele acorda com um
  fato consumado difícil de desfazer.

A régua entre as duas está em **A régua da decisão**, abaixo. Tudo o mais serve a ela.

## De dia: deixar para a noite

Quando ele diz de passagem "anota pra rodar à noite" ou "põe na pauta", **não execute agora**. Escreva
um item na seção `## Para a noite` do doc de pendências da tarefa (`references/identificar-doc.md`):

- o que fazer, em uma frase no indicativo ("todo texto explicativo de formulário vira `<Tooltip>`");
- **o precedente ou a causa raiz**, com caminho e linha conferidos na fonte — sem isso, a noite vai
  inventar padrão sozinha;
- **o critério de pronto**, um comando, com o resultado medido agora (`grep … | wc -l → 14`);
- o escopo, se não for óbvio.

Investigue você (`grep`, leitura); não pergunte o que o código responde. Mostre o item em três
linhas e volte ao que ele estava fazendo. "O que tem pra noite": liste a seção, com o que falta em
cada item incompleto.

Bug só entra com causa raiz confirmada e reprodução determinística. Bug que mexe em dado, cobrança,
permissão, autenticação ou contrato de API não fica para a noite: é trabalho de dia, com ele.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Procedência, escrita fora do repositório
só com autorização, e saída honesta valem inteiros aqui.

**Uma exceção:** a regra de "pergunte com opções para marcar" fica suspensa **durante** a noite — não
há ninguém para marcar. A pergunta não some: ela é guardada, com as opções, e volta inteira no fim.

## Ao entrar

1. **Uma linha de confirmação, e comece.** Não pergunte nada — ele já saiu. Ex.: *"Modo noturno:
   5 itens decididos, começo pelo teste do importador."*
2. **Inventário do que está decidido.** Fontes, nesta ordem: a conversa da sessão, o doc de pendências
   da tarefa (`references/identificar-doc.md`) — inclusive a seção `## Para a noite` —, o plano ou ADR
   que a sessão seguia, e os itens de `docs/melhorias/pronto/` se o repo tiver essa pasta (formato
   antigo; ao fechar, mova o arquivo para `feito/` ou `bloqueado/`). Liste em itens
   numerados, cada um com o critério de pronto (o comando que passa, a tela que abre).
3. **A base está verde?** Rode os testes e o build do projeto antes de mexer. Já vermelho: registre a
   saída no relatório e não misture a noite com uma base quebrada — ele não saberia o que foi você.
   Siga só com itens que não dependem da parte vermelha.
4. **Ordem: do menor risco para o maior.** O primeiro item prova o mecanismo (guarda, commit, doc)
   barato. Itens independentes não esperam na fila: vão em paralelo (**Itens em paralelo**, abaixo).
5. **Grave o inventário no disco antes do primeiro item**, no doc de pendências, numa seção
   `## Modo noturno <AAAA-MM-DD>`. A conversa pode ser resumida no meio da noite; o disco não.
6. **Nada decidido?** Não invente trabalho. Uma linha dizendo isso, e pare.

Doc de pendências ambíguo (`references/identificar-doc.md` mandaria perguntar): à noite não há a
quem. Crie um doc novo com o assunto da noite e diga no relatório qual era a dúvida.

## Itens em paralelo

A noite rende o tamanho da fila, não o de um item. Com dois ou mais itens que não dependem um do
outro, dispare um subagente por item já ao entrar. Antes, liste os arquivos (e o trecho) de cada um:

- **Arquivos não se cruzam** → paralelo na pasta principal. Os subagentes não commitam: você commita
  item a item, com a lista exata de arquivos de cada um.
- **Mesmo arquivo, trechos diferentes** → paralelo, cada um na sua worktree, com dependências
  instaladas nela. Crie as worktrees uma por vez: várias ao mesmo tempo disputam a criação e falham.
- **Mesmo trecho ou mesmo comportamento** → um por vez.

Cada subagente no modelo mais leve que dá conta: o mais capaz para decidir desenho e código difícil;
verificar, testar e usar a tela pelo navegador vão no mais leve. O prompt de cada um leva a régua
desta skill — decide o pequeno sozinho, devolve o grande como pergunta, não pergunta nada — senão ele
congela o que você mesma decidiria. Quem integra é você: guarda verde, commit, doc, um item por vez.

## A régua da decisão

Para cada escolha que aparecer no caminho, uma pergunta só: **se eu errar, ele desfaz de manhã em
poucos minutos, sem perder nada?**

**Sim → decida.** Pelo padrão do próprio projeto primeiro (como o código vizinho faz, o que o
`CLAUDE.md` e as memórias dizem), pelo convencional depois. Anote na lista *"decidi sozinha"*: a
escolha, o porquê em uma frase, e como desfazer. Exemplos: nome de função, formato de mensagem de
erro, qual de duas bibliotecas já instaladas usar, ordem dos itens, texto de label, como estruturar
um teste, tamanho de botão, densidade, espaçamento, lista em uma linha ou duas.

**Não → grande impacto: congele.** É grande impacto, sempre:

- ação **irreversível ou destrutiva** — apagar arquivo, branch, dado, tabela; reescrever histórico;
- **sair da máquina** sem autorização registrada para aquele repo — push, merge, deploy, PR,
  mensagem, comentário em ticket (`PADROES.md`, seção 3);
- **arquitetura** — nova dependência, novo serviço, mudança de modelo de dados, algo que pede ADR;
- **regra de produto ou de domínio** — o que o sistema deve fazer para o usuário, quando não está
  escrito em lugar nenhum;
- **segurança** — afrouxar permissão, expor dado, abrir exceção;
- **custo** — gastar dinheiro, contratar serviço, consumir cota paga;
- **mudar o que foi combinado** — descobriu que o plano está errado.

Na dúvida entre as duas, é grande impacto.

## O que fazer com o congelado

**Se dá para implementar sem destruir nada e sem sair da máquina**, implemente a opção que você
recomenda numa **branch à parte**, para ele só aprovar de manhã:

```bash
git worktree add .claude/worktrees/noturno-<slug> -b noturno/<AAAA-MM-DD>-<slug>
```

- Worktree, e não `git switch`: a árvore principal continua onde estava, com o trabalho da noite.
- A branch parte do ponto atual do trabalho, já com os commits da noite.
- Dependências instaladas de verdade na worktree (`npm ci`, etc.), nunca link para o `node_modules`
  da principal — remover a worktree depois levaria o original junto.
- Commit na branch à parte, com a guarda verde (abaixo). Nada de push.
- O que depender dessa decisão também vai para a mesma branch, não para a principal.

**Se não dá** — é destrutivo, sai da máquina, ou custa dinheiro —, não implemente nada. Só registre.

Em qualquer caso, a pergunta vai para o doc **no momento em que aparece**: contexto em duas linhas,
as opções que existem de fato (investigadas, não genéricas), a sua recomendação e por quê, e a branch
à parte se houver. Depois, siga para o próximo item.

## Durante a noite

- **Siga as regras do repo.** Push, commit na main, numeração de migration, convenção de mensagem: o
  que o `CLAUDE.md` e as memórias daquele projeto dizem vale aqui como valeria de dia. Autorização de
  push registrada para o repo continua valendo; ausência dela continua barrando.
- **Guarda antes de cada commit:** os testes da área mexida, o build se o projeto tiver. Vermelho que
  você não consegue corrigir sem afrouxar a régua: reverta aquele pedaço, registre a saída colada, e
  siga para o próximo item.
- **Item com tela só fecha clicado** pelo caminho do usuário — teste de render que clica onde ele
  clicaria, ou o navegador. API respondendo 200 não prova que existe botão que leve até ela. Clique
  automático só numa lista do que abre e mostra (abrir, ver, editar, expandir), nunca "tudo menos os
  verbos perigosos": sempre sobra um "Desligar" ou "Voltar ao padrão" que grava. Anote antes o estado
  do que pode mudar.
- **Item de bug começa pelo teste que falha**, pela razão que a causa raiz diz. Falhou por outro
  motivo, ou passou de cara: a causa está errada — congele o item com a saída colada.
- **Item que revela uma escolha entre dois comportamentos defensáveis** passa pela régua como qualquer
  outra decisão, mesmo que tenha vindo "pronto" de dia.
- **Um commit por item fechado**, com pathspec explícito. Trabalho não commitado que já estava na
  árvore ao entrar é da sessão — siga com ele, mas não faça `stash` nem descarte nada que você não
  escreveu.
- **Outra sessão pode commitar na mesma pasta.** Nada fica preparado no índice esperando — ela leva
  junto. Arquivo novo pede `git add` do próprio caminho no mesmo comando do commit (o pathspec não
  pega arquivo não rastreado); arquivo que outra sessão também mexeu vai só com os seus trechos
  (`git add -p`, ou patch com contexto — nunca `--unidiff-zero`). Depois, `git status`: nada seu
  ficou de fora. Número de migration ou ADR: confira o remoto e o não rastreado antes de criar.
- **Não encoste em processo, porta ou container que não foi você quem subiu** (`PADROES.md`, seção 3).
- **Atualize o doc ao fechar cada item**: feito, decidido sozinha, congelado. Se você perder o fio,
  `git log` e o doc dizem onde estava.
- **Silêncio útil no chat:** uma linha por item fechado (*"3 de 7 feito: importador com teste"*).
  Nada de narrar.

## Quando parar

Só quando **todo** item do inventário estiver em um destes estados:

- **feito** — critério de pronto atingido, commitado;
- **congelado** — esperando decisão dele, registrado (com ou sem branch à parte);
- **travado** — bloqueado por algo fora do seu alcance (serviço fora do ar, credencial, acesso),
  registrado com o que falta e como obter.

Antes de parar, releia o inventário inteiro. Item que dependia de um congelado mas tinha uma parte
independente: faça a parte independente. Depois, confira cada **feito** contra o pedido de origem —
de preferência por um subagente verificador, que não escreveu o código, clicando na tela quando
houver. "Pedi e não foi feito" é o pior achado da manhã. Achado no caminho que é trabalho novo, fora do combinado:
não faça — vira uma linha no relatório.

Pare também, mais cedo, se **três itens seguidos** falharem — o problema é o ambiente, não os itens —,
ou se a base ficar vermelha e você não conseguir voltar ao verde revertendo o
que fez. Um repositório quebrado de manhã é o pior desfecho possível.

## O relatório da manhã

Nos dois lugares, com o mesmo conteúdo:

1. **No doc de pendências**, na seção `## Modo noturno <AAAA-MM-DD>`. Respeite o modo do repo
   (`git config --local --get pendencias.modo`); se estiver vazio, não dá para perguntar: trate como
   `local` e diga isso no relatório.
2. **No chat**, como mensagem final.

Formato em **`references/relatorio.md`**. Depois do relatório, as perguntas congeladas vão em
`AskUserQuestion` (até quatro por chamada, a mais importante primeiro), com a sua recomendação como
primeira opção — é o que ele vai responder ao acordar. Respondida uma leva, chame a próxima, até
acabarem; não espere ele pedir o resto.

## Quando ele responder

- **Aprovou a branch à parte:** traga para a branch de trabalho seguindo a regra de merge do repo, e
  remova a worktree (`git worktree remove`, sem `--force` se houver algo não commitado).
- **Recusou ou escolheu outra opção:** remova a worktree e a branch, e implemente o que ele escolheu.
- **Atualize o doc**: pergunta respondida sai de "Perguntas" e vai para "Combinado", com a decisão.
- **Resposta é combinado:** construa já, em paralelo quando der, sem pedir um "pode ir".

## Limites inegociáveis

- Nada sai da máquina sem autorização registrada para aquele repo.
- Nada destrutivo, nem em branch à parte.
- Nunca afrouxar teste, asserção ou critério para fechar um item.
- Nunca sair do escopo do trabalho da sessão, nem do repositório (ou repositórios) em que ela estava.
- Nunca decidir sozinha o que caiu na lista de grande impacto — nem "provisoriamente" na principal.
