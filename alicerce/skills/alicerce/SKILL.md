---
name: alicerce
description: "Início de projeto, do passo 0 ao molde provado. Primeiro especifica a fundação em documentos (plano, convenções, regras de trabalho), sem código; depois do ok do dev, levanta a obra: escolhe ferramenta e versão, registra cada escolha em ADR, executa fase por fase com verificação por comando e para quando a feature de referência prova o molde. Use quando o dev for começar um projeto novo, quiser saber o que falta de fundação num projeto que já existe, for especificar uma coisa nova grande dentro de um projeto, ou pedir para 'executar o plano de fundação', 'levantar o projeto', 'montar o esqueleto', 'obra', ou quando existir um docs/PLANO-FUNDACAO.md esperando execução. Não é para escrever um ADR avulso nem para trabalho de design system de interface."
---

# Alicerce — do passo 0 ao molde provado

Produz o **passo 0** de um projeto como **documento**: o que é obrigatório, o que é
opcional, o que foi adiado de propósito, e onde cada regra é imposta.

Existe porque a ordem das decisões de fundação segue **custo de reversão**. Migration
versionada, forma de erro, tokens de design, modelo de permissão, ator na assinatura de
quem grava, costura de teste — são baratos no dia 1 e caros no dia 90. Escolher errado
a ordem é o que transforma protótipo em dívida.

Duas fases, sempre nesta ordem e com uma pausa entre elas:

1. **Especificar** (passos 0 a 5) — escreve o contrato em documentos. Nenhum código.
2. **Obra** (passo 6) — levanta a fundação lendo o contrato **do disco**, só depois do ok do dev.

O contrato precisa ser preciso sobre o **requisito** e mudo sobre a **ferramenta**: a ferramenta se
escolhe na obra, com versão conferida na data, e vira ADR.

**Entrada direta na obra:** se já existe `docs/PLANO-FUNDACAO.md` e o dev pediu para levantar, vá
direto ao passo 6.

## Regras invioláveis

1. **Na especificação, não implementa nada.** Nenhum arquivo de código, nenhum
   `npm install`, nenhum serviço no ar. Implementar é só na obra, depois do ok.
2. **O plano não nomeia ferramenta nem versão.** "Formatter e linter num tool só, rodando em
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

| Arquivo | Você escreve na especificação | Você completa na obra |
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

Feche oferecendo a obra, **sem arrancar sozinha**:

> "A fundação está especificada. Dá uma olhada nas suposições no topo do plano — corrigir
> agora custa uma linha, depois custa retrabalho. Quando estiver de acordo, eu levanto."

Se o dev aceitar, siga para o **passo 6**. Se ele corrigir alguma coisa antes,
reescreva o trecho afetado do plano e ofereça de novo. Nos modos AUDITORIA e FEATURE,
a obra é a mesma: executa o plano ou o doc da feature que você escreveu.

A pausa aqui não é cerimônia: é o único momento em que corrigir uma suposição errada
ainda é barato. Numa execução real, o dev leu o resumo e trocou o projeto de
desktop-first para mobile-first na mensagem seguinte — encadear automático teria
levantado a fase inteira errada.

## Passo 6 — a obra: levantar a fundação

Executa as fases do plano e para quando **o molde está provado**. Aqui você escolhe a
ferramenta — **e a escolha vira ADR**.

**Sem plano, sem obra.** Se não existir `docs/PLANO-FUNDACAO.md` (ou o doc da feature),
volte ao passo 0. Levantar fundação sem contrato é como se constrói o que ninguém
consegue explicar depois.

### Regras da obra

1. **Você decide ferramenta, nunca requisito.** Requisito que não está no plano não
   entra: pergunte, ou volte e reescreva o plano. Escopo que cresce sozinho é o modo
   mais comum de a fundação virar projeto.
2. **Não encoste em nada fora do projeto.** Mate pelo PID que você guardou, **nunca por
   padrão de nome** — `pkill -f vite` derruba o servidor de outro projeto. Confira a
   porta antes e **fixe** a sua; não pare container que não foi você quem subiu.
3. **Ferramenta que resiste duas vezes tem o padrão dela adotado.** Aceite o default,
   registre como desvio e siga. Tooling de fase 1 não pode virar o projeto.
4. **Verifique a própria escrita.** Edição por âncora falha em silêncio quando o arquivo
   mudou desde que você o leu. Confirme que aplicou antes de seguir.
5. **Não commite sem pedido**, e nunca com `git add -A` às cegas. Sem `push` nunca.

### Fluxo

1. **Ler o contrato do disco** — mesmo que você o tenha escrito nesta conversa: o dev
   pode ter corrigido depois de ler. A seção `## Requisitos para a obra` traz, por item,
   fase, requisito, onde é imposto e **critério de pronto por comando** — é o seu ponto
   de parada; não invente outro. Não implemente o **adiado**, nem o `N/A`.
2. **Escolher as ferramentas** que o plano deixou abertas, com
   `references/obra-decisoes.md`: versão e compatibilidade conferidas na data, não de
   memória; prefira o que o dono do projeto já usa. Um ADR por escolha.
3. **Executar fase por fase** com `references/obra-execucao.md`. Cada fase fecha com a
   tabela de verificação preenchida no plano.
4. **Parar no critério de saída:** a fundação está pronta quando a segunda feature sai
   do molde sem pergunta. Você entrega a primeira, a de referência. Ao fim, pergunte
   honestamente: *"Quem copiasse `{caminho do molde}` precisaria decidir algo que não
   está escrito?"* Se sim, o que falta é convenção no `CLAUDE.md`, não código.

### O que você completa nos documentos

| Documento | O que você completa |
|---|---|
| `docs/PLANO-FUNDACAO.md` | verificação por fase e tabela de desvios |
| `README.md` | a seção **Rodar** — os comandos reais, testados do zero |
| `CLAUDE.md` | **Comandos**, **Armadilhas já encontradas aqui**, nome da feature de referência |
| `docs/adr/` | um ADR por escolha de ferramenta ou versão |

A seção de armadilhas é a mais valiosa e a mais esquecida: cada uma custou tempo uma
vez, e escrever ali é o que impede a segunda.

### Saída honesta da obra

Requisito que não pode ser cumprido — dependência que não existe, ambiente que não sobe,
critério que não passa —: **pare e diga**. Não marque como feito, não afrouxe o
critério. Entregue até onde chegou, o que falta e o que tentou; "não verificado" é
resposta legítima, "feito" sem comando que prove não é.

## Adaptação ao contexto

Antes de propor qualquer convenção, veja o que o dev já adota. As instruções globais
dele (`~/.claude/CLAUDE.md`) já estão no seu contexto; os vizinhos, não:

```bash
ls ../*/.editorconfig ../*/.github/workflows 2>/dev/null | head
```

Os vizinhos só valem como precedente se forem do mesmo dono do projeto — pasta ao lado
não é casa comum. Pergunte de quem é o projeto antes de importar convenção de vizinho;
confirmado o mesmo dono, convenção existente vence escolha ótima.

## Referências

- `references/dominio.md` — o que cada domínio exige, e o filtro do que é dor de fundação
- `references/checklist-fundacao.md` — a régua: o contrato, as áreas, o que é obrigatório
- `references/modo-novo.md` — os dois caminhos e como montar a especificação
- `references/modo-auditoria.md` — como levantar o que existe e priorizar as lacunas
- `references/modo-feature.md` — coisa nova dentro de projeto que já existe
- `references/obra-execucao.md` — como executar uma fase e fechá-la com verificação
- `references/obra-decisoes.md` — como escolher ferramenta e versão, e escrever o ADR
- `assets/` — modelos dos cinco documentos
