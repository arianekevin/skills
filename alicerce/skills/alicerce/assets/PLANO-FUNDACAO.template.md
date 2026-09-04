# Plano de Fundação — {NOME DO PROJETO}

_Especificado em {DATA} pela skill `alicerce`. Quem implementa é a `obra`, lendo a
seção **Requisitos para a obra**. Este documento não nomeia ferramenta nem versão:
essas escolhas são da obra e viram ADR em `docs/adr/`._

## O projeto

**O que é:** {as frases do dev, o mais próximo possível do que ele disse}
**Pra quem:** {usuário}
**Natureza:** {web app / API / CLI / mobile / lib}
**Horizonte:** {protótipo descartável / produto interno / produção}
**Quem toca:** {solo / time de N}
**Modo de especificação:** {genérico / personalizado}

### Não-escopo
- {o que este projeto explicitamente NÃO faz}

### Critério de pronto (v1)
- {como saber que a v1 está de pé}

### O que este domínio exige

**Família(s):** {ex.: financeiro/regulado + IA no núcleo}

| Exigência | O que quebra sem ela | Onde é imposta | Balde |
|---|---|---|---|
| | | | |

**Cortadas pelo horizonte:** {as que o domínio pedia e o horizonte descartou}
**Mantidas contra o horizonte:** {as que o dev decidiu manter mesmo contrariando a
calibragem, com a justificativa}
**Da combinação de domínios:** {o que a interseção cria e nenhum pediria sozinho}

### Suposições assumidas
_Assumido, não perguntado. Corrigir aqui é mais barato que ter respondido._
- {}

---

## Requisitos para a obra

_Esta é a seção que a skill `obra` executa. Cada item traz o requisito (nunca a
ferramenta), quem impõe a regra, e o critério de pronto verificável por comando._

### Obrigatório

| # | Fase | Requisito | Onde é imposto | Pronto quando |
|---|---|---|---|---|
| 1 | 1 | | | |

### Opcional

| # | Requisito | Passa a valer a pena quando |
|---|---|---|
| 1 | | |

### Adiado de propósito

| # | Adiado | Gatilho de revisita | Detector, se a máquina puder checar |
|---|---|---|---|
| 1 | | | |

### Não se aplica

| Área | Por quê |
|---|---|
| | |

---

## Fases

**Fase 1 — esqueleto.** {objetivo}. Zero feature.
**Fase 2 — o eixo.** {objetivo}. Termina com a feature de referência e o teste dela.
**Fase 3 — o resto.** {objetivo}.

**Feature de referência:** {qual, por que atravessa todas as camadas, e qual exigência
central do domínio ela exercita}

---

## Decisões (ADR)

| # | Decisão | Justificada por | Status |
|---|---|---|---|
| 0001 | | | decidida / a decidir pela obra |

Registrar em `docs/adr/`, formato em `docs/adr/0000-template.md`.
**Escolha de ferramenta e versão é da obra** — cada uma vira um ADR novo lá.

---

## Verificação por fase
_Preenchido pela `obra`. Cada linha traz o comando que provou. O que não foi rodado
entra como **não verificado**, nunca como feito._

### Fase 1
| Item | Comando | Resultado |
|---|---|---|

### Fase 2
| Item | Comando | Resultado |
|---|---|---|

### Fase 3
| Item | Comando | Resultado |
|---|---|---|

---

## Desvios do plano
_Preenchido pela `obra`. Onde a realidade contrariou a especificação, e o que ficou no
lugar. Documento vivo: plano que só descreve o dia 1 vira ficção na primeira semana._

| Fase | O plano exigia | O que aconteceu | O que ficou no lugar |
|---|---|---|---|
