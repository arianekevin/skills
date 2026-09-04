# Plano de Fundação — {NOME DO PROJETO}

_Gerado em {DATA}. Documento vivo: atualize conforme as ondas forem concluídas._

## O projeto

**O que é:** {as frases do dev, o mais próximo possível do que ele disse}
**Pra quem:** {usuário}
**Natureza:** {web app / API / CLI / mobile / lib}
**Horizonte:** {protótipo descartável / produto interno / produção}
**Quem toca:** {solo / time de N}

### Não-escopo
- {o que este projeto explicitamente NÃO faz}

### Critério de pronto (v1)
- {como saber que a v1 está de pé}

### O que este domínio exige

_Derivado de `references/dominio.md`. São as exigências que a régua genérica não tem —
e normalmente as mais caras de deixar pra depois, porque encostam no modelo de dados._

**Família(s):** {ex.: financeiro/regulado + IA no núcleo + integração com terceiros}

| Exigência | Por que ESTE projeto precisa | Onda |
|---|---|---|
| | | |

**Da combinação:** {o que a interseção dos domínios cria e nenhum deles sozinho pediria}

### Suposições assumidas
- {o que não foi perguntado e foi assumido — corrija aqui se estiver errado}

---

## Decisões iniciais (ADR)

| # | Decisão | Justificada pelo domínio | Status |
|---|---|---|---|
| 0001 | {ex.: Stack} | {ex.: decimal nativo, lida com dinheiro} | decidida / a decidir |
| 0002 | {ex.: Banco — Postgres} | | |
| 0003 | {ex.: Autenticação} | | |

Registrar em `docs/adr/`, formato em `docs/adr/0000-template.md`.

---

## Onda 1 — esqueleto  ⏱️ {estimativa}

_Objetivo: CI verde no primeiro commit. Zero feature._

| # | O que fazer | Por que agora | Pronto quando |
|---|---|---|---|
| 1 | | | |

## Onda 2 — o eixo  ⏱️ {estimativa}

_Objetivo: uma feature de referência ponta a ponta, atravessando todas as camadas._

| # | O que fazer | Por que agora | Pronto quando |
|---|---|---|---|
| 1 | | | |

**Feature de referência escolhida:** {qual, por que atravessa todas as camadas, e qual
exigência central do domínio ela exercita}

## Onda 3 — o resto  ⏱️ {estimativa}

| # | O que fazer | Por que agora | Pronto quando |
|---|---|---|---|
| 1 | | | |

---

## Convenções

**Estrutura:** {eixo escolhido + esboço de `src/`}
**Regra de dependência:** {ex.: domínio não importa infra}
**Commits:** {ex.: Conventional Commits}
**Branches:** {ex.: trunk-based, PR obrigatório}

---

## Adiado de propósito

| Item | Revisitar quando |
|---|---|
| | |

---

## Não se aplica

{áreas da régua marcadas N/A e por quê}
