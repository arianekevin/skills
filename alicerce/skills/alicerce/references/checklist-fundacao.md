# A régua — o que "bem fundado" significa

**Esta régua é o piso, não o plano.** Leia `dominio.md` antes e some as exigências de
lá. Plano que só tem esta régua é plano que não olhou pro projeto.

Cada item entra na especificação com quatro coisas:

1. **O requisito** — nunca a ferramenta. "Formatter e linter num tool só", não "Biome"
2. **O balde** — obrigatório, opcional (com o sinal que o torna necessário), ou adiado
   de propósito (com o gatilho de revisita)
3. **Onde é imposto** — banco, tipo, lint, CI, hook, ou *acordo*. Regra que não declara
   quem a impõe é desejo; escrever "imposta por: acordo" é honesto, esconder não é
4. **Critério de pronto verificável por comando** — a `obra` precisa saber que acabou
   sem perguntar. "README claro" não serve; "seguir o README do zero e a app sobe" serve

Prioridades: **P0** barato agora e caro depois · **P1** primeira semana · **P2** aditivo.

**`N/A` se escreve.** Área que não se aplica aparece dizendo isso. Ausência é
ambiguidade — e é ela que quebra o "sei o que procurar em qualquer projeto".

---

## 0. O contrato de fundação

Cinco endereços fixos, sempre presentes, com seções de título fixo. O horizonte calibra
a profundidade, nunca a existência: num protótipo, um ADR de três linhas ainda é um ADR
em `docs/adr/0001-*.md`.

| Arquivo | Seções de título fixo |
|---|---|
| `README.md` | O que é · Rodar · Índice |
| `CLAUDE.md` | Regras que não se quebram · Estrutura · Armadilhas |
| `CONTRIBUTING.md` | Definition of Done · Testes · Commits e revisão |
| `docs/PLANO-FUNDACAO.md` | Requisitos para a obra · Adiado de propósito · Não se aplica |
| `docs/adr/` | um arquivo por decisão |

Sem títulos estáveis não existe "sei onde procurar": o dev e a IA saltam pela seção.

## 1. Produto & escopo

| Item | Pri | Onde é imposto |
|---|---|---|
| Uma página: problema, usuário, **não-escopo**, critério de pronto | P0 | acordo |
| Critério de sucesso mensurável, ainda que grosseiro | P1 | acordo |

O **não-escopo** é o mais negligenciado e o que mais economiza retrabalho.

## 2. Decisões registradas (ADR)

| Item | Pri | Onde é imposto |
|---|---|---|
| As decisões que a conversa tomou, uma por arquivo | P0 | acordo |
| Template para as próximas, inclusive as que a `obra` vai tomar | P0 | acordo |

Formato: *contexto / decisão / consequências / alternativas descartadas*. Escolha de
ferramenta e versão **não** é decisão desta skill — é da `obra`, e vira ADR lá.

## 3. Repo, tooling & CI

| Item | Pri | Onde é imposto |
|---|---|---|
| Formatter e linter, num tool só se possível | P0 | lint |
| Typecheck estrito, se a linguagem tiver | P0 | typecheck |
| `.gitignore`, `.editorconfig`, segredo fora do repo | P0 | lint / revisão |
| Convenção de commit | P1 | hook ou CI |
| **CI rodando teste, lint e typecheck** | opcional | CI |

CI é **oferecido, não imposto** — mas com a consequência dita em voz alta: sem ele,
toda diretriz de "não sai sem X" é acordo, não garantia. Ofereça uma vez, aceite a
resposta, e registre no `CONTRIBUTING.md` qual é o caso.

## 4. Convenções & estrutura

| Item | Pri | Onde é imposto |
|---|---|---|
| Um eixo de organização declarado, sem mistura | P0 | revisão |
| Regra de dependência entre camadas | P0 | teste de arquitetura, ou acordo |
| **Feature de referência nomeada** — o molde que todos copiam | P0 | acordo |

Preferir pasta **por domínio/feature** a pasta por tipo técnico. A feature de referência
é o entregável mais valioso: escolha a mais fina que ainda atravesse todas as camadas
**e exercite a exigência central do domínio**.

## 5. Testes — o item que sobrevive a qualquer horizonte

Nasce **antes da primeira linha de código de produto**, e não é cortado nem em protótipo
descartável. Duas razões, e a segunda é a que importa:

- **Custo fixo.** O primeiro teste custa desproporcionalmente — runner, config, primeira
  fixture, ligação com CI. Do segundo em diante é barato. No dia 100 a conta é a mesma,
  só que agora concorre com entrega. Daí a "preguiça", que não é preguiça
- **Código escrito sem teste não é testável.** Regra que alcança global, I/O no meio da
  lógica, dependência instanciada por quem usa. O retrofit não é escrever teste, é
  desmontar código — e o que sai mocka o mundo e não prova nada

| Item | Pri | Onde é imposto |
|---|---|---|
| Runner e convenção: onde o teste mora, como se chama | P0 | acordo |
| **Um teste que exercita a stack de verdade**, não `1+1` | P0 | CI ou acordo |
| **A feature de referência nasce com o teste dela** | P0 | revisão |
| Critério de teste útil, escrito no `CONTRIBUTING.md` | P0 | revisão |

O critério, textual: **desfaça a mudança; se nenhum teste fica vermelho, o teste não
existe.** Regra que só conta testes produz `expect(1+1)`.

O teste da feature de referência é o **molde**: todo mundo copia aquela pasta. Se ele
for raso, todas as features seguintes serão rasas e ninguém vai saber por quê.

## 6. Design system *(condicional: só com interface)*

Especifique a **estrutura**, nunca o inventário. Estruturar o que é caro de retrofitar;
o que é fácil de acrescentar nasce quando tiver dono.

| Item | Pri | Onde é imposto |
|---|---|---|
| Escala de tokens com nomes decididos e valores provisórios | P0 | lint / revisão |
| **Tokens semânticos** (`--fundo`, `--texto`), não literais (`--cinza-100`) | P0 | revisão |
| Os quatro estados: carregando, vazio, erro, sem permissão | P0 | revisão |
| Alvo de toque como token, não exceção avulsa | P0 | revisão |
| **Nenhuma cor literal dentro de componente** | P0 | lint |
| Primitivos e padrões | P1 | — |

O caro não são os valores dos tokens — é a **disciplina de referência**. Se a escala
existe no dia 1, o componente nº 1 usa; se não existe, ele escreve `12px` e quarenta
componentes depois não há escala pra migrar de volta. Trocar valor depois é barato.

Semântico vs. literal é a diferença entre tema escuro ser troca de valores ou reescrita.

**Não especifique inventário de componente** ("vamos precisar de Card, Modal, Tabs").
Isso é adivinhar o produto: saem vinte, seis errados e oito nunca usados.

Sem interface, escreva: **"não se aplica — projeto sem interface"**.

## 7. Tour de feature *(condicional: só com interface)*

**Toda feature nasce com tour.** O que se especifica aqui é a estrutura — nunca a
biblioteca e nunca o texto dos passos, que só existe quando a feature existir.

| Item | Pri | Onde é imposto |
|---|---|---|
| **Âncora estável no componente** — identificador próprio do tour, independente de classe, estilo e hierarquia | P0 | lint ou revisão |
| Tour definido como **dado, num lugar só** — nunca espalhado dentro dos componentes | P0 | estrutura |
| **Versão no tour**: feature mudou, o tour reapresenta em vez de mentir | P0 | modelo de dados |
| **Registro de quem já viu**, por usuário e por versão | P0 | modelo de dados |
| Gatilho declarado: primeira visita, sinalizador, ou manual | P1 | — |
| Lugar para **rever** um tour já visto | P1 | — |
| "Feature nova sai com tour" no Definition of Done | P0 | revisão ou CI |

**A âncora é a metade cara**, e é o mesmo formato do ator na assinatura: o tour aponta
para um elemento, e se o componente não carrega um identificador **próprio do tour**, a
única alternativa é ancorar em classe de CSS, posição ou texto — que quebram
silenciosamente no primeiro refactor, e quem descobre é o usuário. Pôr âncora depois é
passar por todo componente do sistema de uma vez.

**O registro de quem viu é tabela**, então nasce com o schema ou não nasce: acrescentado
depois, não há dado histórico — ou todo mundo revê tudo, ou ninguém vê nada.

Sem interface, escreva **"não se aplica — projeto sem interface"**. A obrigação
equivalente ali é comportamento documentado, que já está na área 8.

## 8. Documentação viva

Coberta pelo contrato (área 0). O que a régua acrescenta:

| Item | Pri | Onde é imposto |
|---|---|---|
| README que roda o projeto em ≤3 comandos | P0 | seguir do zero e funcionar |
| `## Armadilhas` no `CLAUDE.md`, alimentada durante a obra | P0 | acordo |
| Traço de uma requisição ponta a ponta | P1 | acordo |

O traço — "entra aqui, valida ali, grava lá, erro sobe pro handler único" — é o que
permite uma IA entender o projeto numa passada quando ele passar de alguns milhares de
linhas. Estrutura diz onde as coisas moram; o traço diz por onde elas passam.

## 9. Dados & configuração

| Item | Pri | Onde é imposto |
|---|---|---|
| `.env.example` versionado, `.env` ignorado | P0 | lint |
| Um único ponto que lê e valida config | P1 | revisão |
| Migrations versionadas desde a tabela 1 | P0 | CI ou acordo |
| Seed de dado realista | P1 | acordo |

**Adiar migration é legítimo; adiar em silêncio não é.** Se o projeto aplicar schema
direto, exija um detector: schema divergente falha alto no boot, em vez de virar erro
distante da causa três dias depois.

Seed realista é o que torna o design system testável — sem ele, tudo é desenhado com
"Lorem ipsum" e quebra com dado real.

## 10. Operação & segurança

| Item | Pri | Onde é imposto |
|---|---|---|
| Forma única de erro, sem `catch` genérico espalhado | P0 | revisão / lint |
| Log estruturado com nível | P0 | revisão |
| Modelo de auth/permissão **decidido** (implementação depois) | P0 | ADR |
| Nenhum segredo no repo | P0 | lint / CI |
| Healthcheck | P1 | — |
| Licença, `CODEOWNERS` | P2 | — |

Permissão enxertada tarde vaza por todo lado — por isso o **modelo** é P0 mesmo quando
a implementação é P2.

---

## Adiar de propósito

| Adiado | Revisitar quando |
|---|---|
| Microserviços | o deploy conjunto virar gargalo entre times |
| i18n | existir compromisso real com um segundo idioma |
| Cache | houver medição mostrando o gargalo |
| Feature flags | houver mais de um ambiente com público real |
| Abstração "caso troquemos de banco" | a troca estiver de fato na mesa |
| Monorepo | existir o segundo pacote de verdade |

Listar o adiado transforma "esquecemos" em "decidimos". E **todo adiado que a máquina
poderia checar vem com o detector junto** — é o que impede o adiamento de virar silêncio.
