---
name: alicerce
description: "Fundação de projeto — especifica o 'passo 0' e documenta, sem implementar nada. Use esta skill quando o dev for começar um projeto novo, quando perguntar 'por onde eu começo', 'como estruturar esse projeto', 'o que preciso ter antes de codar', ou quando mencionar 'setup inicial', 'estrutura de projeto', 'design system', 'ADR', 'padrão de projeto', 'documentação do projeto', 'boilerplate', 'scaffolding', 'fundação'. Também use quando o projeto já existe e o dev quiser saber o que falta de fundação — 'o que falta aqui', 'auditar o projeto', 'está bem estruturado?'. Detecta sozinha se é projeto novo ou existente e produz documentos: o plano, as convenções e as regras de trabalho. NÃO escreve código, não instala nada, não sobe serviço — quem implementa é a skill obra, lendo o que esta aqui especificou."
---

# Alicerce — especificação de fundação

Produz o **passo 0** de um projeto como **documento**: o que é obrigatório, o que é
opcional, o que foi adiado de propósito, e onde cada regra é imposta.

Existe porque a ordem das decisões de fundação segue **custo de reversão**. Migration
versionada, forma de erro, tokens de design, modelo de permissão, ator na assinatura de
quem grava, costura de teste — são baratos no dia 1 e caros no dia 90. Escolher errado
a ordem é o que transforma protótipo em dívida.

O documento que ela escreve é o contrato que a skill **`obra`** executa. Por isso ele
precisa ser preciso sobre o **requisito** e mudo sobre a **ferramenta**.

## Regras invioláveis

1. **Não implementa nada.** Nenhum arquivo de código, nenhum `npm install`, nenhum
   serviço no ar, nenhum comando que altere o projeto. Ela escreve documentos. Se o dev
   pedir para executar, diga que quem faz isso é a `obra`, lendo este plano.
2. **Não nomeia ferramenta nem versão.** "Formatter e linter num tool só, rodando em
   CI" é requisito; "Biome 2.5" é escolha de quem implementa, e vira ADR na hora. Plano
   que cita versão nasce velho — e erra, porque quem não executa não tem como conferir.
3. **O domínio vem antes de tudo, em texto livre.** Nunca ofereça múltipla escolha para
   "o que é o projeto". Só depois disso vêm as perguntas fechadas.
4. **`N/A` se escreve.** Área que não se aplica aparece no documento dizendo isso.
   Ausência é ambiguidade; `N/A` declarado é informação.
5. **Adiar é decisão legítima** — com o gatilho de revisita escrito.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: pergunta com escolha quando houver opções e aberta quando não
houver, procedência dos identificadores, escrita fora do repositório só com pedido
explícito, e saída honesta em vez de fechamento sem evidência.

## Passo 0 — o que é o projeto (cancela)

**Não escreva nada sem uma frase do que o projeto é.** Um software financeiro com
integração bancária e um site pessoal compartilham talvez 40% da fundação — o que é
obrigatório, e o que sequer existe na régua, mudam por completo.

Se o dev já disse na invocação, você já tem. **Não pergunte de novo.** Se não disse:

> "Me conta em uma ou duas frases o que é esse projeto e pra quem — quanto mais
> concreto, melhor o plano. Ex.: 'software financeiro com IA que concilia extratos via
> integração com grandes bancos, pra time de controladoria'."

Com a frase, leia `references/dominio.md` e derive as exigências deste domínio.

## Passo 1 — detectar o modo

```bash
ls -A | head -30
git log --oneline -1 2>/dev/null | head -1
ls package.json pom.xml build.gradle requirements.txt pyproject.toml go.mod Cargo.toml composer.json 2>/dev/null
```

- **NOVO** — diretório vazio, sem manifesto, ou o dev disse que vai começar
- **Projeto existe** — aí são dois modos, e a diferença é de intenção, não de disco.
  Pergunte:

  > "Quer que eu audite a fundação do projeto inteiro, ou especifique uma coisa nova
  > dentro dele?"

  - **AUDITORIA** — o projeto inteiro contra a régua
  - **FEATURE** — coisa nova dentro do projeto: o que herda, o que falta, o que não
    inventa

Na dúvida sobre o primeiro corte: *"Isso é começo de projeto ou é pra evoluir o que já
existe?"*

## Passo 2 — escolher a profundidade (só no modo NOVO)

Dois caminhos, **mesmo formato de documento no fim**. O modo muda quanto o dev decide,
não a cara do resultado.

| | Genérico | Personalizado |
|---|---|---|
| Perguntas | 4, uma rodada | rodadas curtas, só o que não dá pra derivar |
| Quem decide | a régua, com defaults | o dev, item a item |
| Bom quando | protótipo, projeto conhecido, pressa | domínio regulado, decisão estrutural em aberto |

Ofereça os dois **com recomendação**, baseada na frase do projeto:

> "Isso é domínio regulado com integração — recomendo o personalizado, porque as
> decisões de dado aqui são caras de reverter. Ou vamos de genérico e você corrige
> lendo?"

## Passo 3 — executar o modo

- **NOVO** → `references/modo-novo.md`
- **AUDITORIA** → `references/modo-auditoria.md`
- **FEATURE** → `references/modo-feature.md`

O modo FEATURE não usa o contrato de cinco documentos: a fundação já existe, e ele
escreve um só, `docs/features/<slug>.md`.

Ambos usam `references/checklist-fundacao.md` (a régua) **depois** de `dominio.md`.
A régua é o piso comum; o domínio é o que se soma. Plano que só tem a régua é plano que
não olhou pro projeto.

## Passo 4 — escrever o contrato de fundação

Cinco endereços fixos, **sempre presentes**, com seções de título fixo. O horizonte
calibra a profundidade do conteúdo, **nunca a existência do arquivo** — se ele puder
sumir, o dev não sabe o que procurar em outro projeto.

| Arquivo | Você escreve | A `obra` completa |
|---|---|---|
| `docs/PLANO-FUNDACAO.md` | tudo, incluindo `## Requisitos para a obra` | desvios e verificação por onda |
| `CONTRIBUTING.md` | tudo: definition of done, com quem impõe cada regra | — |
| `CLAUDE.md` | convenções, regra de dependência, regras invioláveis | armadilhas, nome da feature de referência |
| `README.md` | o que é, e o índice dos outros quatro | a seção "Rodar" |
| `docs/adr/` | as decisões que a conversa tomou + o template | as decisões que a execução tomar |

Modelos em `assets/`. O que ficar pendente vai **escrito como pendente**, dizendo quem
preenche — nunca em branco e nunca inventado.

## Passo 5 — entregar

Mostre no terminal **só**: os itens obrigatórios, o que foi adiado, os `N/A`, e as
suposições que você assumiu. O documento tem o resto.

Feche assim, sem oferecer execução:

> "A fundação está especificada. Quem levanta é a `obra`, lendo o
> `docs/PLANO-FUNDACAO.md` — ela decide ferramenta e versão, e registra em ADR."

## Adaptação ao contexto

Antes de propor qualquer convenção, veja o que já é padrão da casa:

```bash
cat ~/.claude/CLAUDE.md 2>/dev/null | head -40
ls ../*/.editorconfig ../*/.github/workflows 2>/dev/null | head
```

Convenção existente vence escolha ótima. Consistência entre projetos vale mais.

## Referências

- `references/dominio.md` — o que cada domínio exige, e o filtro do que é dor de fundação
- `references/checklist-fundacao.md` — a régua: o contrato, as áreas, o que é obrigatório
- `references/modo-novo.md` — os dois caminhos e como montar a especificação
- `references/modo-auditoria.md` — como levantar o que existe e priorizar as lacunas
- `references/modo-feature.md` — coisa nova dentro de projeto que já existe
- `assets/` — modelos dos cinco documentos
