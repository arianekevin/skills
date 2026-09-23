---
name: turno
description: "Executa sozinho, sem supervisão, os itens — melhorias e bugs já diagnosticados — que a skill pauta deixou prontos em docs/melhorias/pronto/. Use esta skill quando o dev invocar /turno, ou quando pedir para 'rodar as melhorias', 'executar a pauta', 'deixar rodando enquanto eu durmo', 'trabalho noturno', 'toca a lista de melhorias'. Entrega uma branch da noite com um commit por item e um relatório para a manhã. NÃO decide nada e NÃO pergunta nada durante a execução: item que exige decisão é parado e devolvido para a pauta. Sem itens prontos, quem escreve é a skill pauta."
---

# Turno — o trabalho da noite

## O que esta skill faz

Você pega os itens de `docs/melhorias/pronto/` — melhorias e bugs já diagnosticados —, executa um
por um numa branch só da noite, commita cada um separado, e deixa um relatório para a manhã.
**Ninguém está na sala.** O dev aprovou o orçamento e foi dormir.

Isso existe porque a melhoria pequena e repetitiva — a que não tem decisão nenhuma dentro — é
exatamente o trabalho que nunca acontece de dia, e é exatamente o que uma máquina faz bem à noite.
O que a torna segura não é a máquina ser boa: é o item já vir com critério medido, escopo escrito e
precedente apontado, e é a branch da noite ficar inteira reversível por uma linha de manhã.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: procedência dos identificadores, escrita fora do repositório só
com pedido explícito, e saída honesta em vez de fechamento sem evidência.

**Uma exceção, e só uma:** a regra de "pergunte com opções para marcar" não vale depois que o
orçamento é aprovado. Não há ninguém para marcar. Dúvida vira item parado e registrado — nunca uma
escolha que você tomou no lugar dele. Ver **A inversão**, abaixo.

## Cancelas

Confira **todas** antes de tocar em qualquer coisa. Cancela fechada termina a sessão com uma linha
dizendo qual foi — não contorne nenhuma.

1. **É repositório git?** Se não, não há como entregar nem como reverter. Pare.
2. **Working tree limpo?** `git status --porcelain` vazio. Trabalho não commitado do dev na árvore
   torna impossível separar o que foi você — e impossível reverter um item sem levar o dele junto.
   Não faça `stash`: mexer no trabalho não commitado de alguém que não está presente é pior que não
   rodar. Pare e diga o que está sujo.
3. **Existe pauta?** `docs/melhorias/pronto/` com pelo menos um item. Se a pasta não existe ou está
   vazia, pare: *"não há item pronto aqui — quem escreve é a `pauta`."* Nunca invente item, nunca
   promova um `rascunho/` ou `bloqueado/` por conta própria. Bloqueado foi bloqueado por faltar algo
   que só o dev resolve.
4. **A guarda de regressão está verde agora?** Rode os comandos mecânicos do projeto antes de
   começar. **Se algo já está vermelho, a noite não é sua:** o dev vai acordar sem saber se foi ele
   ou você. Pare, registre a saída no relatório, e pare mesmo — não é para "consertar primeiro".
5. **Um repositório por noite.** O escopo é o projeto atual. Não saia dele, não abra outro, não
   varra `~/Documents/Projects`.

## A inversão: ninguém está na sala

Esta é a diferença entre esta skill e todas as outras do repositório.

- **Você não pergunta.** Depois do orçamento aprovado, toda pergunta que você faria é um item
  **parado**: registre no relatório o que você precisaria saber, e passe para o próximo.
- **Você não decide no lugar dele.** Descobriu, no meio do item, que há duas formas defensáveis de
  fazer? O item falhou no teste 1 da `pauta` e ninguém percebeu. Reverta o que fez, mova o arquivo
  para `docs/melhorias/bloqueado/` com a decisão escrita, e siga.
- **Você não amplia escopo.** Encontrou mais quinze lugares com o mesmo problema, fora dos globs do
  item? Isso é um item novo em `rascunho/`, não uma noite mais produtiva.
- **Você não relaxa critério.** Vale o `PADROES.md` inteiro aqui: não marque teste como skip, não
  afrouxe asserção, não troque o comando por um mais fácil. Um item falho relatado limpo vale mais
  que seis commits duvidosos.

A régua é a manhã: **o dev precisa conseguir olhar cada commit e decidir em trinta segundos se fica
ou sai.** Tudo nesta skill serve a isso.

## A única interação: o orçamento

Antes de ele sair, uma rodada de `AskUserQuestion` — e só ela. Liste antes, em texto, os itens
prontos com tamanho e orçamento de voltas, para a escolha ser informada.

> header: `Noite` · "O que eu rodo?"
> - "Os 3 prontos, nesta ordem (Recomendado)" — ~13 arquivos no total, 11 voltas somadas
> - "Só `tooltips-explicativas-settings`" — o maior; se der certo, os outros rodam amanhã
> - "Os 2 menores" — noite curta, prova o mecanismo sem arriscar o item grande

Se o dev já disse tudo na invocação (`/turno roda os dois menores`), não pergunte: confirme em uma
linha e comece. Se ele invocou e saiu sem responder, **não arranque** — pergunta ignorada não é
aprovação, e uma noite inteira não autorizada é o pior desfecho possível desta skill.

## A branch da noite

Uma só, para a noite toda, a partir da branch atual:

```
git switch -c melhorias/<AAAA-MM-DD>
```

Um commit por item, sempre. Se a branch do dia já existir (segunda rodada na mesma noite), continue
nela. Ao terminar tudo — inclusive em parada por cancela ou por falha —, **volte para a branch
original**: ele vai abrir o terminal de manhã onde parou, e encontrar-se numa branch que não
reconhece é o primeiro susto que a skill deve poupar.

Nunca `git push`, nunca abra PR. Publicar é decisão dele, na manhã seguinte, com o diff lido.

## A ordem: do menor risco para o maior

Ordene os itens escolhidos por tamanho crescente (arquivos que o critério pega hoje). O primeiro
item da noite é o que **prova o mecanismo** — branch, guarda, commit, relatório. Se o mecanismo está
quebrado, você descobre no item barato, não depois de três horas no item caro.

Item de bug entra na mesma fila, pelo mesmo critério de tamanho. Ele não tem prioridade: um bug que
esperou o dia inteiro na pauta pode esperar mais duas horas, e um bug que **não** podia esperar não
deveria estar aqui — deveria ter sido corrigido de dia, pela `bug-guardrail`, com o dev presente.

## O ritual de cada item

Idêntico para todos, sem atalho. Está em **`references/ritual-do-item.md`** — leia antes do primeiro
item e siga passo a passo: baseline, execução pela `ciclo`, revisão do próprio diff pela
`bug-reviewer`, guarda de regressão, commit por pathspec, atualização do item no disco.

## A memória é o disco, não a conversa

Uma noite é longa e a conversa pode ser resumida no meio. Trate cada item como uma unidade que
começa e termina no disco:

- leia o item **do arquivo**, sempre, mesmo que você "lembre" do conteúdo;
- escreva o resultado no relatório **assim que o item fecha**, não no fim da noite;
- mova o arquivo do item para a pasta do novo estado **no mesmo momento**.

Se você perder o fio, `git log --oneline` na branch da noite mais o relatório em disco dizem
exatamente onde você estava. O que só existe na conversa não sobrevive à noite.

## As outras skills

| Quando | Skill | Como |
|---|---|---|
| Executar o item | **`ciclo`** | O item já traz os três insumos prontos: `objetivo`, `criterio`, `orcamento`. A spec está fechada — a `ciclo` não deve perguntar nada, e o escopo dela são os globs do item. |
| Antes de cada commit | **`bug-reviewer`** | Revise o **seu próprio** diff. Código de IA sem nenhum olho humano, de madrugada, é literalmente o caso de uso dela. Achado grave reverte o item. |
| A guarda quebrou e você não sabe por quê | **`bug-diagnostico`** | Só para **entender**, nunca para corrigir. O resultado vira um item em `rascunho/` com a investigação anexada. |
| O item é `tipo: bug` | **`bug-guardrail`** | As cancelas dela (causa raiz, cenários, escopo) já estão no item — confira as três e siga por ela, não pela `ciclo` direto. Causa raiz ausente ou que não bate com o código: pare e devolva para `bloqueado/`. |

## Paradas

Pare a noite inteira, imediatamente, se:

- **três itens seguidos falharem** — o problema não são os itens, é o ambiente ou a base;
- **a guarda de regressão ficar vermelha e você não conseguir voltar ao verde** revertendo o item —
  isso é um repositório que o dev vai encontrar quebrado, e é o pior estado possível de manhã;
- **o orçamento aprovado acabar** — não "aproveite que está indo bem" para pegar mais um item;
- **uma cancela reaparecer** — a árvore ficou suja por algo que não foi você, um processo externo
  mexeu no repositório.

Parada não é fracasso da noite: é o desfecho honesto. Escreva o relatório do mesmo jeito, volte para
a branch original, e diga na primeira linha que parou e por quê.

## O relatório da manhã

Sempre, mesmo quando nada rodou. Formato e conteúdo em **`references/relatorio.md`**. Ele mora em
`docs/melhorias/relatorio/<AAAA-MM-DD>.md` e é o **último commit** da branch da noite.

A primeira linha é o veredito, e ela não enfeita: *"3 itens, 2 commitados, 1 revertido"* é a frase.
Quem lê está com café na mão e trinta segundos de paciência.

## Limites inegociáveis

- **Nunca `git push`**, nunca abrir PR, nunca comentar em ticket. Nada sai da máquina.
- **Nunca `git add -A` nem `git add .`.** Sempre pathspec explícito, derivado dos globs do item.
  Antes de commitar, confira com `git status --porcelain` que **nada** fora do escopo foi tocado —
  se foi, reverta o item inteiro: escopo estourado é item falho, mesmo que o critério tenha passado.
- **Não instale dependência**, não altere `package.json`/`pom.xml`, não suba versão de biblioteca.
  Item que precisa disso está bloqueado, não adiantado.
- **Não edite migration**, `.env`, config de infra, pipeline de CI, nem nada em `nao_mexe`.
- **Não suba a aplicação** nem serviço de longa duração, e não encoste em processo, porta ou
  container que não foi você quem subiu — a máquina dele tem outros projetos de pé, e é madrugada.
- **Não mexa em arquivo fora do repositório atual.**
- **Não execute item de bug que toque dado, cobrança, permissão, autenticação ou contrato de API**,
  nem bug sem reprodução determinística — mesmo que o item tenha passado pela pauta e chegado a
  `pronto/`. Este limite é seu também: pare o item, devolva para `bloqueado/` com o motivo. Uma
  melhoria errada custa um `git revert` de manhã; um `UPDATE` errado custa a semana.
- **Não apague nem reescreva item** que você não executou.

## Tom

Enquanto roda, silêncio útil: uma linha por item, sem narrar o caminho. O texto que importa é o
relatório, e ele é lido por alguém que acabou de acordar. Diga o que falhou antes do que deu certo,
sem enfeitar e sem se desculpar.
