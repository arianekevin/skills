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

## 2. Calibrar pelo horizonte

| Horizonte | O que vira P0 |
|---|---|
| Protótipo descartável | README + tokens + `.gitignore`. Só. Nada de CI, ADR ou migration |
| Produto interno | os P0 da régua, sem CD nem observabilidade fina |
| Produção | régua P0 inteira + healthcheck + modelo de permissão |

Não empurre fundação de produção num protótipo. É o erro simétrico de não ter
fundação nenhuma, e custa igual.

## 3. Montar o plano

Percorra `checklist-fundacao.md`, marcando cada item como **entra / N/A / adiado**.
Depois agrupe em três ondas por dependência:

- **Onda 1 — esqueleto (algumas horas).** Repo, tooling, CI verde, `.env.example`,
  README mínimo, ADRs iniciais. Nada de feature. Termina com CI verde no commit 1.
- **Onda 2 — o eixo (meio dia).** Estrutura de pastas, convenções, tokens de design,
  migration inicial, forma de erro e log. Termina com **uma feature de referência**
  ponta a ponta — fina, mas atravessando todas as camadas.
- **Onda 3 — o resto.** Primitivos de UI, seed, CONTRIBUTING, CHANGELOG.

A feature de referência da Onda 2 é o entregável mais valioso do plano inteiro:
ela vira o template que todo o resto copia, humano ou IA. Escolha a mais fina que
ainda atravesse todas as camadas (ex.: um cadastro com um campo).

## 4. Escrever

Preencha `assets/PLANO-FUNDACAO.template.md` em `docs/PLANO-FUNDACAO.md`.
Gere também `docs/adr/0000-template.md` a partir de `assets/adr-0000.template.md` —
é o único arquivo além do plano que esta skill cria.

Cada item do plano precisa de: **o que fazer**, **por que agora** (uma linha),
e **como saber que está pronto**. Item sem critério de pronto vira item eterno.

Escreva os ADRs iniciais como **títulos com a decisão já tomada** quando ela for
óbvia pelas respostas ("0001 — Usar Postgres"), e como pergunta em aberto quando não
for ("0004 — Modelo de autenticação: a decidir"). Não invente decisão que o dev
não tomou.
