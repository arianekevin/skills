# Modo NOVO — planejar o passo 0

Objetivo: em ~10 minutos de conversa, produzir `docs/PLANO-FUNDACAO.md` executável.

## 1. Perguntar (uma rodada só, máximo 5)

Use `AskUserQuestion` **uma vez**, com as perguntas abaixo. Não faça segunda rodada —
o que faltar, você assume e registra como suposição no documento.

Antes de perguntar, **elimine as que já sabe**. Se o dev já disse "app web em Next",
não pergunte a natureza nem a stack. Perguntar o que já foi dito queima confiança.

| # | Pergunta | Por que é decisiva |
|---|---|---|
| 1 | O que é o projeto e pra quem? (uma frase) | define escopo e não-escopo |
| 2 | Natureza: web app / API / CLI / mobile / lib / script | liga ou desliga áreas inteiras da régua |
| 3 | Stack — já decidida ou quer sugestão? | muda tooling, CI e estrutura |
| 4 | Quem toca: só você, ou time? | define peso de CONTRIBUTING, CI, CODEOWNERS |
| 5 | Horizonte: protótipo descartável, produto interno, ou vai pra produção? | calibra o que é P0 |

A **5** é a mais importante e a mais esquecida. Protótipo descartável com fundação de
produto é desperdício; produto com fundação de protótipo é dívida. Se só puder fazer
uma pergunta, faça essa.

Ofereça opções concretas em cada pergunta, não campo aberto. O dev responde em
15 segundos em vez de escrever um parágrafo.

## 3. Calibrar pelo horizonte

| Horizonte | O que vira P0 |
|---|---|
| Protótipo descartável | README + tokens + `.gitignore`. Só. Nada de CI, ADR ou migration |
| Produto interno | os P0 da régua, sem CD nem observabilidade fina |
| Produção | régua P0 inteira + healthcheck + modelo de permissão |

Não empurre fundação de produção num protótipo. É o erro simétrico de não ter
fundação nenhuma, e custa igual.

### O horizonte corta a lista do domínio — passo obrigatório

As duas calibragens são independentes e **podem se contradizer**: o domínio pede
trilha append-only e ator até a camada que grava; o horizonte "protótipo descartável"
pede README e nada mais. Sem um corte explícito, você obedece as duas e entrega
fundação de produto para código que vai ser jogado fora.

Antes de escrever o plano, cruze as duas listas:

| Horizonte | O que sobra das exigências do domínio |
|---|---|
| Protótipo descartável | **Nenhuma por padrão.** Só entra a que o dev confirmar |
| Produto interno | As P0 que encostam no modelo de dados. As demais, adiadas |
| Produção | A lista inteira |

Se alguma exigência do domínio parecer boa demais para cortar num protótipo — e às
vezes é, porque append-only muda o modelo de dados e retrofitar é caro —, **diga isso
em voz alta e deixe o dev decidir**:

> "Você marcou protótipo descartável, então por regra eu cortaria o histórico
> append-only. Mas ele muda o modelo de dados e é o item mais caro de acrescentar
> depois. Mantenho, ou corto e a gente aceita perder o histórico se isso virar
> produto?"

O que não pode é entregar em silêncio o oposto do que a calibragem pediu. Se o dev
mandar manter, registre no plano que a exigência **contraria o horizonte declarado**,
com a justificativa — assim, quem ler depois entende por que um protótipo tem trigger
de banco.

## 4. Montar o plano

Junte duas listas: as exigências derivadas do domínio (passo 1) e a régua genérica —
percorra `checklist-fundacao.md` marcando cada item como **entra / N/A / adiado**.
Depois agrupe em três ondas por dependência:

- **Onda 1 — esqueleto (algumas horas).** Repo, tooling, CI verde, `.env.example`,
  README mínimo, ADRs iniciais. Nada de feature. Termina com CI verde no commit 1.
- **Onda 2 — o eixo (meio dia).** Estrutura de pastas, convenções, tokens de design,
  migration inicial, forma de erro e log — **mais as exigências P0 do domínio**, que
  quase sempre caem aqui porque encostam no modelo de dados. Termina com **uma feature
  de referência** ponta a ponta, fina mas atravessando todas as camadas.
- **Onda 3 — o resto.** Primitivos de UI, seed, CONTRIBUTING, CHANGELOG.

A feature de referência da Onda 2 é o entregável mais valioso do plano inteiro:
ela vira o template que todo o resto copia, humano ou IA. Escolha a mais fina que
ainda atravesse todas as camadas — e que **exercite a exigência central do domínio**.
Num financeiro com integração bancária, "importar um extrato de um banco e conciliar
uma linha" vale dez vezes mais que "cadastro de usuário": prova a camada de tradução,
a idempotência, o decimal e a trilha de auditoria de uma vez.

## 5. Escrever

Preencha `assets/PLANO-FUNDACAO.template.md` em `docs/PLANO-FUNDACAO.md`.
Gere também `docs/adr/0000-template.md` a partir de `assets/adr-0000.template.md` —
é o único arquivo além do plano que esta skill cria.

Cada item do plano precisa de: **o que fazer**, **por que agora** (uma linha),
e **como saber que está pronto**. Item sem critério de pronto vira item eterno.
Nos itens vindos do domínio, o "por que agora" cita o domínio explicitamente.

Escreva os ADRs iniciais como **títulos com a decisão já tomada** quando ela for
óbvia pelas respostas ("0001 — Usar Postgres"), e como pergunta em aberto quando não
for ("0004 — Modelo de autenticação: a decidir"). Não invente decisão que o dev
não tomou.
