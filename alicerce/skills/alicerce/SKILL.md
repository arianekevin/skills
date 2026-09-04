---
name: alicerce
description: "Fundação de projeto — planeja ou audita o 'passo 0'. Use esta skill quando o dev for começar um projeto novo, quando perguntar 'por onde eu começo', 'como estruturar esse projeto', 'o que preciso ter antes de codar', ou quando mencionar 'setup inicial', 'estrutura de projeto', 'design system', 'ADR', 'padrão de projeto', 'documentação do projeto', 'boilerplate', 'scaffolding'. Também use quando o projeto já existe e o dev quiser saber o que está faltando de fundação — 'o que falta aqui', 'auditar o projeto', 'está bem estruturado?'. A skill detecta sozinha se é projeto novo ou existente e produz um documento de plano. NÃO implementa nada — só planeja."
---

# Alicerce — fundação de projeto

Produz o **passo 0** de um projeto: o documento que define o que existe, o que falta,
e em que ordem construir a base (docs, ADRs, tooling, convenções, design system).

Existe porque a ordem das decisões de fundação não é estética — ela segue **custo de
reversão**. Migration versionada, tratamento de erro, tokens de design e modelo de
permissão são baratos no dia 1 e caros no dia 90. Escolher errado a ordem é o que
transforma protótipo em dívida.

## Regras invioláveis

1. **Não implementa.** Esta skill produz um documento de plano. Nenhum arquivo de
   código, nenhum `npm install`, nenhum scaffold. Se o dev quiser executar, ele pede
   depois — aí sim você executa item por item.
2. **O domínio vem antes de tudo, em texto livre.** Nunca ofereça múltipla escolha
   para "o que é o projeto" — é a única pergunta que não pode ser fechada. Só depois
   de ter a frase do projeto use `AskUserQuestion`, uma única vez, no máximo 4
   perguntas, e só para **calibragem**. O que não for perguntado, você assume e
   **registra a suposição** no documento.
3. **O plano cabe em 1–2 dias de trabalho.** Se passar disso, cortou de menos.
   Fundação que vira projeto de um mês virou cerimônia.
4. **Adiar é uma decisão legítima.** Itens caros-cedo entram; itens caros-tarde
   (microserviços, i18n, cache, feature flags) vão para uma seção "Adiado de
   propósito", com o sinal que dispara a revisita.

## Passo 0 — o que é o projeto (cancela)

**Não escreva plano nenhum sem uma frase do que o projeto é.** Um software financeiro
com integração bancária e um site pessoal compartilham talvez 40% da fundação — stack,
o que é P0, e o que sequer existe na régua genérica mudam por completo. Plano escrito
sem domínio é plano genérico, e plano genérico é ruído.

Se o dev já disse (`/alicerce quero fazer um software financeiro com IA e integração
com grandes bancos`), você já tem. **Não pergunte de novo.**

Se não disse, pergunte em texto livre, uma linha, antes de qualquer outra coisa:

> "Me conta em uma ou duas frases o que é esse projeto e pra quem — quanto mais
> concreto, melhor o plano. Ex.: 'software financeiro com IA que concilia extratos
> via integração com grandes bancos, pra time de controladoria'."

Com a frase em mãos, leia `references/dominio.md` e derive **o que este domínio
específico exige** antes de abrir a régua genérica. Esse é o passo que separa um
plano útil de uma lista de boas práticas.

No modo auditoria, o domínio se infere do código — mas ainda assim se **confirma**
em uma linha antes de julgar qualquer coisa.

## Passo 1 — detectar o modo

Rode no diretório do projeto:

```bash
ls -A | head -30
git log --oneline -1 2>/dev/null | head -1
ls package.json pom.xml build.gradle requirements.txt pyproject.toml go.mod Cargo.toml composer.json 2>/dev/null
```

- **Modo NOVO** — diretório vazio, ou só `.git`/`README`, ou sem manifesto de
  dependências, ou o dev disse explicitamente que vai começar algo.
- **Modo AUDITORIA** — existe código-fonte + manifesto, ou histórico de commits real.

Na dúvida (ex.: um protótipo solto de um arquivo), pergunte em uma linha:
> "Isso aqui é começo de projeto ou é pra evoluir o que já existe?"

## Passo 2 — executar o modo

- **NOVO** → leia `references/modo-novo.md` e siga.
- **AUDITORIA** → leia `references/modo-auditoria.md` e siga.

Ambos usam a mesma régua: `references/checklist-fundacao.md`, sempre **depois** de
`references/dominio.md`. A régua é o piso comum; o domínio é o que se soma a ela.
Um plano que só tem a régua genérica é um plano que não olhou pro projeto.

## Passo 3 — entregar

O artefato é um arquivo markdown no repo:

- Modo NOVO → `docs/PLANO-FUNDACAO.md` (template em `assets/PLANO-FUNDACAO.template.md`)
- Modo AUDITORIA → `docs/DIAGNOSTICO-FUNDACAO.md` (template em `assets/DIAGNOSTICO.template.md`)

Se `docs/` não existir, crie. Depois de escrever, mostre ao dev **só o resumo**:
o que entrou na Onda 1, o que foi adiado, e as suposições que você assumiu.
Não despeje o documento inteiro no terminal.

Pergunte ao final, em uma linha: *"Quer que eu execute a Onda 1 agora?"*

## Adaptação ao contexto

Antes de escrever o plano, verifique o que **já é padrão da casa** e não reinvente:

```bash
cat ~/.claude/CLAUDE.md 2>/dev/null | head -40
ls ../*/.editorconfig ../*/.github/workflows 2>/dev/null | head
```

Se o dev já tem convenção estabelecida em outro projeto (linter, formato de commit,
estrutura de pastas), o plano **adota a existente** em vez de propor uma nova.
Consistência entre projetos vale mais que a escolha ótima em um.

## Referências

- `references/dominio.md` — como o domínio muda a stack e cria exigências próprias
- `references/checklist-fundacao.md` — a régua: 8 áreas, o que é P0/P1/P2, como detectar
- `references/modo-novo.md` — as perguntas e como montar o plano do zero
- `references/modo-auditoria.md` — como levantar o que existe e priorizar as lacunas
- `assets/` — templates dos documentos e do ADR
