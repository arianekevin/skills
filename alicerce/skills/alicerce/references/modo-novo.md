# Modo NOVO — especificar a fundação

Objetivo: produzir os cinco documentos do contrato, com uma seção que a `obra` consiga
executar sem tomar decisão estrutural nem perguntar a cada passo.

Você não escreve código. Se der vontade de criar um arquivo de configuração, pare: o
que você tem a fazer é **descrever o requisito** com precisão suficiente para a `obra`
criá-lo sozinha.

## 1. O domínio já está na mão

Você cumpriu o Passo 0: tem a frase do projeto. Leia `dominio.md`, passe pelo filtro
("isso é dor de fundação?") e derive de 2 a 5 exigências, cada uma com **o que quebra
sem ela** e **onde é imposta**.

Isso já responde muita coisa — não pergunte o que o domínio respondeu.

## 2A. Caminho genérico — 4 perguntas, uma rodada

Use `AskUserQuestion` **uma vez**. O que não for perguntado, você assume e registra
como suposição no documento — corrigir lendo é mais barato que responder.

| # | Pergunta | Por que é decisiva |
|---|---|---|
| 1 | Horizonte: protótipo descartável, produto interno, ou produção? | calibra o que é obrigatório |
| 2 | Natureza: web app / API / CLI / mobile / lib | liga ou desliga áreas inteiras |
| 3 | Stack: já decidida, ou derivo do domínio? | muda tooling e estrutura |
| 4 | Quem toca: só você, ou time? | peso de `CONTRIBUTING`, CI, revisão |

A **1** é a mais importante e a mais esquecida. Se só puder fazer uma, faça essa.

Nestas quatro, ofereça opções concretas — o dev marca em quinze segundos.

## 2B. Caminho personalizado — rodadas curtas, com freio

Mesmo ponto de partida, mesmas quatro acima primeiro. A diferença é o que vem depois.

**Só vira pergunta o que satisfaz as duas condições:**

1. Muda o **conjunto de arquivos** ou o **ponto de imposição** de alguma regra
2. **Não** dá pra derivar do domínio somado ao horizonte

Todo o resto continua vindo do default e aparece no documento como *"assumido, não
perguntado"*. Se você está prestes a perguntar algo que a régua já responde igual em
99% dos projetos, não pergunte — escreva a suposição.

Perguntas que costumam passar no teste: onde o dado de cada cliente mora (linha, schema
ou banco); se a regra X é imposta pelo banco ou por revisão; se CI entra agora; se o
histórico é derivado ou guardado; qual é a feature de referência.

Perguntas que **não** passam: nome de pasta, estilo de aspas, qual runner de teste.

Pare quando a próxima pergunta não mudar nenhum dos cinco documentos. Diga que parou:

> "Fechei o que muda o desenho. O resto eu assumi — está tudo na seção de suposições."

## 3. O horizonte corta a lista do domínio

Passo obrigatório nos dois caminhos. As duas calibragens são independentes e **podem se
contradizer**: o domínio pede trilha append-only, o horizonte "protótipo descartável"
pede quase nada. Sem corte explícito você obedece as duas e entrega fundação de produto
para código que será jogado fora.

| Horizonte | Sobra das exigências do domínio |
|---|---|
| Protótipo descartável | **nenhuma por padrão** — só a que o dev confirmar |
| Produto interno | as que encostam no modelo de dados. As demais, adiadas |
| Produção | a lista inteira |

**Duas coisas o horizonte nunca corta**, porque o custo de retrofitá-las cresce com o
tamanho do código e não com a ambição do projeto:

- **A estrutura de teste**, incluindo o teste da feature de referência (área 5 da régua)
- **O ator na assinatura de quem grava**, quando o projeto guarda dado de valor

Se alguma outra exigência parecer boa demais para cortar, **diga em voz alta e deixe o
dev decidir**:

> "Você marcou protótipo descartável, então por regra eu cortaria o histórico
> append-only. Mas ele muda o modelo de dados e é o mais caro de acrescentar depois.
> Mantenho, ou corto e a gente aceita perder o histórico se isso virar produto?"

Se o dev mandar manter, registre no plano que a exigência **contraria o horizonte
declarado**, com a justificativa. Quem ler depois entende por que um protótipo tem
trigger de banco.

## 4. Montar os três baldes

Junte as exigências do domínio (já cortadas) com a régua de `checklist-fundacao.md`,
e classifique **cada item** em um balde:

- **Obrigatório** — com onde é imposto e critério de pronto verificável por comando
- **Opcional** — com o sinal que o tornaria necessário
- **Adiado de propósito** — com o gatilho de revisita, e o detector quando a máquina
  puder checar a divergência
- **Não se aplica** — escrito, nunca omitido

As **fases** continuam existindo, como ordem de execução para a `obra`:

- **Fase 1 — esqueleto.** Repo, tooling, config, estrutura de teste com o teste que
  exercita a stack de verdade. Zero feature
- **Fase 2 — o eixo.** Estrutura de pastas, regra de dependência, forma de erro, tokens,
  as exigências P0 do domínio, e a **feature de referência com o teste dela**
- **Fase 3 — fechar a fundação.** Só o que a completa: os primitivos que a feature de
  referência já exigiu, o seed, e a documentação final

**Nada de "mais uma feature" entra em fase nenhuma.** Feature seguinte é trabalho
normal, feito com o `CLAUDE.md` e o molde — passa pelo modo FEATURE quando houver
decisão a tomar, e por skill nenhuma quando não houver. Plano que lista features é plano
que não sabe onde termina.

A feature de referência é o entregável mais valioso: vira o molde que todos copiam,
humano ou IA. A mais fina que ainda atravesse todas as camadas e exercite a exigência
central do domínio.

### O critério de saída da fundação

Escreva no plano, com estas palavras:

> **A fundação está pronta quando a segunda feature sai do molde sem pergunta.**

A primeira feature — a de referência — não é fundação nem é trabalho normal: é a
**prova de que o molde funciona**. Enquanto ninguém a copiou, o molde é hipótese.

Isso dá à `obra` um ponto de parada verificável e diz ao dev o que esperar: se a segunda
feature ainda exigir decisão estrutural, a fundação não terminou — falta convenção
escrita, ou o molde não era molde.

## 5. Escrever os cinco documentos

Modelos em `assets/`. Regras que valem para todos:

- **Requisito, nunca ferramenta ou versão.** A escolha é da `obra` e vira ADR lá
- **O que ficar pendente vai escrito como pendente**, dizendo quem preenche
- **Cada regra declara quem a impõe** — inclusive "acordo", quando for o caso

Nos ADRs iniciais, escreva como decisão tomada o que a conversa decidiu ("0002 — Banco
relacional") e como pergunta em aberto o que ela não decidiu ("0004 — Autenticação: a
decidir"). Nunca invente decisão que o dev não tomou.
