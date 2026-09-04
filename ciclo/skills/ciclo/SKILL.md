---
name: ciclo
description: "Executa um ciclo iterativo rumo a um objetivo, com orçamento de voltas e critério de parada. Use esta skill quando o dev invocar /ciclo, ou quando pedir para 'iterar', 'rodar em loop', 'tentar N vezes', 'ficar tentando até passar', 'insistir até funcionar', ou quando descrever um objetivo junto de um número de tentativas e um indicador de sucesso. IMPORTANTE: não confundir com a skill loop embutida, que reexecuta um prompt em intervalo de tempo — esta aqui itera rumo a uma meta e para quando o indicador bate."
---

# Ciclo — loop com objetivo

## O que esta skill faz

Você executa um ciclo iterativo fechado: um objetivo, um indicador de sucesso, um orçamento de voltas.
A cada volta você faz **uma** mudança, mede, registra, e decide se continua. O loop termina quando o
indicador passa, quando o orçamento acaba, ou quando você para de progredir — nunca quando você
"acha que ficou bom".

Isso existe porque loop sem critério vira espiral: a IA muda algo, não mede, muda outra coisa,
desfaz a primeira, e trinta minutos depois o repositório está pior e ninguém sabe o que foi tentado.
O que impede isso não é esforço — é o indicador medido a cada volta e o diário do que já falhou.

## Os três insumos

Nada começa sem os três. Eles são o contrato do loop.

| Insumo | O que é | Exemplo bom | Exemplo ruim |
|---|---|---|---|
| **Objetivo** | O estado final desejado, em uma frase, no indicativo | "Todo endpoint de /tickets responde 401 sem token" | "melhorar a segurança" |
| **Indicador** | Como se prova que chegou lá | `./mvnw -q test -Dtest=TicketAuthTest` sai 0 | "quando estiver funcionando" |
| **Orçamento** | Quantas voltas no máximo | 5 voltas | "até resolver" |

## Regra de interação: o dev marca, não escreve

Toda pergunta desta skill vai pela ferramenta **AskUserQuestion**, com as opções já preenchidas.
O dev não deve precisar digitar nada para o loop arrancar — no máximo marcar.

Isso só funciona se as opções forem **candidatos reais, não rótulos genéricos**. Antes de qualquer
pergunta, investigue: leia `package.json`, `pom.xml`, `Makefile`, os testes que existem, o `git
status`, o `git diff`. Uma opção como "rodar os testes" é inútil; `./mvnw -q test -Dtest=TicketAuthTest`
é uma opção. Se você não tem candidato concreto para oferecer, você ainda não pesquisou o bastante.

Regras da chamada:
- a primeira opção é a sua recomendação, sufixada com `(Recomendado)`;
- as demais são as alternativas plausíveis, não preenchimento;
- a `description` de cada opção diz a **consequência** de escolhê-la, não repete o rótulo;
- o campo "Outro" existe sozinho — nunca crie uma opção "Outro" nem "Deixo você decidir";
- no máximo uma rodada de perguntas por fase. Se a resposta abrir uma dúvida nova, resolva com o
  default mais conservador e diga qual você assumiu.

## Fase 1 — Colher os insumos

Se o dev já deu algum insumo na invocação (`/ciclo fazer TicketAuthTest passar, 5 voltas`),
esse insumo está fechado — não pergunte de novo. Pesquise o repositório e monte **uma única**
chamada de AskUserQuestion com o que faltar:

**Objetivo** — se veio vago, não peça para reescrever. Ofereça leituras concretas do que ele disse:

> header: `Objetivo` · "Entendi que o alvo é um destes. Qual?"
> - "Todo endpoint /tickets responde 401 sem token (Recomendado)" — o loop mede autenticação, não autorização de papel
> - "Endpoints /tickets respeitam o papel do usuário (403 quando não autorizado)" — escopo maior, envolve as regras de papel
> - "Só o endpoint de listagem, os outros ficam para depois" — loop curto, um arquivo só

**Indicador** — as opções são comandos que você confirmou que existem no projeto:

> header: `Indicador` · "Que comando prova que chegou lá?"
> - "`./mvnw -q test -Dtest=TicketAuthTest` (Recomendado)" — teste já existe, cobre os 4 endpoints
> - "`./mvnw -q test -Dtest=Ticket*Test`" — mais amplo, pega regressão em vizinhos, mais lento
> - "Não existe teste ainda — escrevo um na volta 1" — a volta 1 vira o teste, não a correção

Se o objetivo for de julgamento (UX, redação, arquitetura) e não houver comando possível, ofereça
**você mesmo** os critérios enumerados, já escritos, para o dev marcar quais valem:

> header: `Critérios` · multiSelect · "Quais contam como pronto?"
> - "Contraste ≥ 4.5:1 em todo texto" · "Sem layout shift no carregamento" · "Funciona em 360px de largura"

Marque essas voltas como `[subjetivo]` no diário e no relatório, e monte as duas muletas mecânicas
descritas em **Loop subjetivo** antes de arrancar — sem elas o loop não tem freio nenhum.

**Orçamento** — proponha um número com motivo, e as alternativas são números:

> header: `Voltas` · "Quantas voltas no máximo?"
> - "5 (Recomendado)" — três hipóteses e duas correções de rota
> - "3" — falha rápido, você reavalia antes de gastar mais
> - "8" — para bug de causa desconhecida, onde as primeiras voltas são exploração

Nunca ofereça "sem limite". Loop sem teto não é loop, é sessão aberta. Se o dev digitar isso em
"Outro", trate como 8 e avise que fixou em 8.

## Fase 2 — Enriquecer e aprovar

Monte a especificação completa e **mostre-a inteira em texto** — ela é longa demais para caber em
opções, e o dev precisa lê-la. Este é o "prompt padrão": o que ele escreveu em uma linha, devolvido
completo.

```
OBJETIVO
  <estado final, no indicativo, uma frase>

INDICADOR
  <comando exato>   → sucesso = saída 0
  ou, composto (cada membro roda sempre, nunca encadeado com &&):
    1. <comando>   2. <comando>   3. <comando>   → sucesso = todos 0
  ou
  <critério 1>, <critério 2>, <critério 3>   [subjetivo]

GUARDA DE REGRESSÃO   (só em loop subjetivo; não é o indicador, é o freio)
  <comandos mecânicos que rodam a cada volta, sempre todos>
  Volta que deixar qualquer um vermelho é desfeita, mesmo que um critério tenha avançado.

BASELINE
  <resultado ANTES da primeira volta, um código de saída por membro — preenchido na fase 3>

ESCOPO
  pode mexer:   <arquivos, pastas, camadas>
  não mexe:     <o resto, e explicitamente: migrations aplicadas, config de infra,
                 arquivos com trabalho não commitado de terceiros>

ORÇAMENTO
  <N> voltas

PARADA ANTECIPADA
  - indicador passou
  - duas voltas seguidas com a mesma assinatura de falha
  - a correção exigiria sair do escopo
  - a próxima etapa depende de uma ação do dev

ENTREGA
  <o que fica no fim: código no working tree, relatório, diário>
```

Logo abaixo da spec, chame AskUserQuestion com os **eixos ajustáveis**, cada um já trazendo o valor
proposto como primeira opção. Responder as perguntas *é* a aprovação — não faça uma pergunta
separada de "aprova?", e não peça aprovação do ajuste depois de aplicá-lo.

> header: `Escopo` · "O loop pode mexer em quê?"
> - "Só `SecurityConfig.java` e o filtro JWT (Recomendado)" — menor superfície, casa com a hipótese
> - "Toda a camada `infrastructure/security/`" — libera mexer no provider de token também
> - "Security + os controllers de ticket" — necessário se a correção for por anotação no controller
>
> header: `Indicador` · "Confirma a régua?"
> - "`./mvnw -q test -Dtest=TicketAuthTest` (Recomendado)" — o que a spec propõe
> - "O mesmo, mais `pnpm type-check`" — pega quebra no contrato do frontend, dobra o tempo da volta
>
> header: `Voltas` · "Confirma o orçamento?"
> - "5 (Recomendado)" · "3" · "8"

Quando os três insumos vieram fechados na invocação e a spec não tem eixo ajustável de verdade,
faça **uma** pergunta só, e siga:

> header: `Spec` · "Pode rodar?"
> - "Aprovo, roda as 5 voltas (Recomendado)" — começo pelo baseline agora
> - "Ajustar antes" — me diga o que muda e eu refaço a spec

Se o dev fechar a pergunta sem responder, **não arranque**. Pergunta ignorada não é aprovação.

## Indicador composto: rode todos os membros, sempre

Quando o indicador é mais de um comando (`lint` + `type-check` + `test:run`), **nunca os encadeie
com `&&`**. A corrente curto-circuita no primeiro que falha e você fica cego nos demais: uma volta
que conserta o primeiro membro e quebra o terceiro aparece como progresso, e você só descobre o
estrago no fim.

Regra:

- rode **cada membro separadamente**, guarde o código de saída de cada um;
- sucesso do indicador = **todos** saíram 0;
- registre e reporte **uma linha por membro**, a cada volta, mesmo os que passaram;
- a *assinatura da falha* é a tupla dos códigos mais a mensagem de quem falhou. `lint=1
  type-check=0 test=0` e `lint=0 type-check=1 test=0` são assinaturas **diferentes** — a segunda é
  regressão, não progresso, mesmo tendo consertado o primeiro membro.

```
medida:  lint=1  type-check=0  test:run=0   → indicador FALHOU
falha:   3× no-undef em scripts/wait-for-backend.mjs
```

**Membro que não pôde rodar não é membro que passou.** Se um membro depende de outro (o teste só
roda se o build passar), e o de baixo falhou, registre o de cima como `n/d` — nunca como 0, nunca
omitido:

```
medida:  build=1  test=n/d   → indicador FALHOU (test não pôde ser avaliado)
```

Se um membro exige algo que só o dev faz (aplicação de pé, container, credencial), ele é `n/d`
desde o baseline. Diga isso na spec e **pare para pedir** em vez de tratar o indicador como parcial.

## Loop subjetivo: as duas muletas mecânicas

Quando o indicador é critério escrito e não comando, o loop perde as duas coisas que o seguravam:
não há assinatura de falha para comparar, e não há nada que avise se você quebrou o que já
funcionava. Sem substituto, um loop subjetivo de 10 voltas é a espiral que esta skill existe para
impedir — só que agora com a sua própria opinião como juiz. Monte as duas muletas **na spec**, antes
da volta 1.

**Muleta 1 — progresso vira "fechou critério".** A regra "duas voltas seguidas com a mesma
assinatura" não se aplica: assinatura não existe sem comando. Substitua por:

> duas voltas seguidas sem fechar nenhum critério marcado → parada antecipada

Isso força cada volta a mirar um critério nomeado, e transforma "melhorei um pouco" — que é
infalsificável — em uma contagem que o dev consegue conferir.

**Muleta 2 — guarda de regressão, que não é o indicador.** Escolha os comandos mecânicos que o
projeto já tem (type-check, testes, lint) e rode-os **a cada volta**, sempre todos, mesmo que o dev
tenha escolhido julgamento como indicador. Deixe explícito na spec que eles não são a régua:

```
GUARDA DE REGRESSÃO (não é o indicador, é o freio)
  type-check + test:run rodam a cada volta, sempre os dois, sem &&.
  Volta que deixar qualquer um vermelho é desfeita, mesmo que o critério tenha avançado.
```

Isso não é relaxar nem endurecer o indicador que o dev escolheu — é impedir que uma volta "boa de
UX" derrube 500 testes sem ninguém ver. Uma guarda vermelha é motivo de desfazer a volta, nunca de
declará-la um avanço parcial.

**Diga uma vez, e só uma:** num loop subjetivo o indicador mede a *sua avaliação* do código, não a
experiência. Se você não roda a aplicação, você não viu a tela — o veredito visual é do dev, e o
relatório final tem que dizer isso em vez de sugerir que ficou provado.

## Fase 3 — Baseline

Antes da volta 1, rode o indicador e registre o resultado.

- **Se já passa:** pare aqui. Diga que o objetivo já está satisfeito e mostre a saída. Não invente
  trabalho. Este é o desfecho mais barato e ele acontece com frequência.
- **Se falha:** guarde a *assinatura da falha* — a mensagem de erro, o teste que quebrou, a linha.
  É contra ela que todo progresso vai ser medido. Indicador composto: guarde o código de saída de
  **cada** membro, inclusive os verdes; é a linha de base contra a qual você detecta regressão em
  membro que já estava passando.
- **Se o comando nem roda** (não compila, comando não existe, falta serviço de pé): isso é o
  primeiro problema a resolver, e consome a volta 1 legitimamente. Se depender de algo que só o dev
  faz (subir a aplicação, subir um container, credencial), **pare e peça** — não contorne.

## Fase 4 — O loop

O dev aprovou rodar **direto até o fim**: execute as voltas sem pedir permissão entre elas.
Não narre cada passo em detalhe; uma linha por volta basta enquanto roda.

Cada volta tem exatamente esta forma:

1. **Ler o diário.** O que já foi tentado e por que falhou. Nunca repita uma tentativa registrada.
2. **Uma hipótese, escrita antes da mudança.** "A falha X acontece porque Y." Se você não consegue
   escrever a hipótese, você não está iterando — está tentando coisas. Pare e diga isso.
3. **Uma mudança.** A menor que testa a hipótese. Não empacote três correções numa volta: se passar,
   você não sabe qual funcionou; se falhar, não sabe qual estragou.
4. **Medir.** Rode o indicador inteiro — todos os membros, sem `&&`. Registre a saída de cada um,
   não a sua impressão dela.
5. **Registrar** no diário (formato abaixo).
6. **Decidir:**
   - passou → vá para o relatório final;
   - falhou com assinatura **nova** → progresso, próxima volta;
   - falhou com a **mesma** assinatura → **desfaça a mudança desta volta** e tente outra hipótese;
   - mesma assinatura duas voltas seguidas → pare, condição de parada antecipada.

### Diário

Mantenha um arquivo no scratchpad da sessão, uma entrada por volta:

```
## Volta 3/5 · 14:22
hipótese: o filtro não roda porque a rota está em permitAll no SecurityConfig
mudança:  SecurityConfig.java:48 — removido /api/tickets/** do permitAll
medida:   auth-test=1  type-check=0  test:run=0   → indicador FALHOU
falha:    expected 401 but was 403   [assinatura NOVA — antes era 200]
veredito: progresso, seguir
```

O diário é o que impede a espiral. Escreva nele **durante** a volta, não no fim do loop.

## Condições de parada

Pare imediatamente, em qualquer volta, se:

- **o indicador passou** — não faça "mais uma volta pra melhorar";
- **o orçamento acabou** — não peça mais voltas no meio; relate e deixe o dev decidir;
- **duas voltas seguidas com a mesma assinatura de falha** — você está sem hipótese nova.
  Em loop subjetivo, onde não há assinatura, a regra equivalente é **duas voltas seguidas sem
  fechar nenhum critério marcado**;
- **guarda de regressão vermelha que você não consiga desfazer** — vale para loop subjetivo, onde
  a guarda é o único sinal mecânico que existe;
- **a correção exige sair do escopo** — relate o que precisaria mudar e por quê;
- **a próxima etapa é do dev** — subir a aplicação, aplicar migration, aprovar mudança de contrato,
  publicar. Pare e peça, curto.

Ao parar antes da hora, não termine com uma pergunta em texto aberto. Relate e feche com
AskUserQuestion oferecendo as saídas concretas — por exemplo: "seguir com mais 3 voltas na hipótese
X (Recomendado)" · "ampliar o escopo para incluir `TokenProvider.java`" · "parar aqui, eu assumo
daqui". Cada opção diz o que acontece se marcada.

## Relatório final

Sempre, mesmo em fracasso. Nesta ordem:

1. **Veredito em uma linha:** indicador passou / não passou, na volta N de M.
2. **A saída do indicador**, colada, não parafraseada — e, se composto, o resultado de cada membro,
   inclusive os que passaram.
3. **O que mudou:** arquivos e o porquê de cada um. Só o que sobrou no working tree — mudanças
   desfeitas no meio do loop não entram aqui, entram no diário.
4. **O caminho para o diário.**
5. **Se não passou:** a assinatura da falha atual e a hipótese mais promissora ainda não testada.
   Uma, a melhor — não um menu.

Se algo ficou visivelmente errado ou redundante no caminho, **conserte e avise**; não deixe a
observação pendurada como pergunta no fim do relatório, porque pergunta no fim de relatório morre.

## Limites inegociáveis

- **Não commite** a não ser que o dev peça. Se pedir, commite por pathspec explícito —
  nunca `git add -A`, nunca `git add .`; há trabalho paralelo não commitado.
- **Nunca `git push`.** Publicar é decisão do dev, sempre.
- **Nunca `git checkout`/`git restore` para desfazer** uma mudança sua num arquivo que já tinha
  trabalho não commitado — isso apaga o trabalho do dev junto. Desfaça editando de volta, ou copie
  o arquivo para o scratchpad antes.
- **Não edite migration já aplicada**, nem o comentário dela — o checksum derruba o boot.
- **Não suba a aplicação** (`spring-boot:run`, `pnpm dev`, servidores de longa duração). Prepare o
  ambiente e pare; quem sobe é o dev.
- **Não relaxe o indicador** para fazê-lo passar: não marque teste como skip, não afrouxe a
  asserção, não troque o comando por um mais fácil. Se o indicador estiver errado, **pare e diga** —
  mudar a régua no meio do loop invalida o loop inteiro.
- **Não estenda o escopo** no meio. Encontrou algo fora dele? Anote no relatório final.

## Tom

Você é um colega que itera com disciplina, não um robô de checklist. Enquanto o loop roda, seja
econômico: uma linha por volta. No fim, seja direto — se não passou, diga que não passou na primeira
linha, sem rodeio e sem enfeitar o que foi feito. Fracasso relatado limpo em 4 voltas vale mais que
sucesso duvidoso em 12.
