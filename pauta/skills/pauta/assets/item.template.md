---
id: <slug-curto-e-estavel>          # vira o nome do arquivo e entra na mensagem de commit
tipo: <melhoria | bug>              # decide o ritual que o turno aplica
titulo: <uma linha, no indicativo>
criado: <AAAA-MM-DD>
objetivo: >
  <o estado final, uma frase, no indicativo. "Todo texto explicativo de formulário é uma
  tooltip do componente Tooltip.vue" — não "melhorar os textos">
precedente:                         # tipo: melhoria
  padrao: <caminho:linha do componente/função que define o padrão-alvo>
  exemplo: <caminho:linha de um lugar onde o padrão JÁ está aplicado>
causa_raiz:                         # tipo: bug — no lugar de precedente
  frase: <a causa em uma frase, não o sintoma>
  onde: <caminho:linha>
  assinatura: |                     # a falha de hoje, colada; o turno compara contra ela
    <mensagem de erro / saída errada, exatamente como aparece>
  cenarios:                         # o turno escreve o teste a partir daqui, na volta 1
    - principal: <entrada → resultado esperado>
    - borda: <entrada → resultado esperado>
criterio:
  - <comando que vai a zero ou sai 0>        # ex.: grep -rn 'class="hint"' src/ | wc -l  → 0
  - <comando mecânico do projeto>            # ex.: pnpm type-check
  - <comando mecânico do projeto>            # ex.: pnpm test:run
baseline:                                     # medido HOJE, pela pauta, antes de guardar o item
  - <comando>: <resultado atual>             # ex.: grep ... | wc -l: 34
  - <comando>: <código de saída>             # ex.: pnpm type-check: 0
escopo:
  pode:
    - <glob>
  nao_mexe:
    - <glob>
tamanho: <n arquivos que o critério pega hoje>
orcamento: <n> voltas
---

## Por que

<duas ou três linhas. O que dói hoje, não o que fica bonito. Quem lê isto às duas da manhã
não tem o contexto da conversa em que o item nasceu.>

## Como fazer

<o padrão, descrito pelo precedente, não inventado aqui. "Substituir cada <p class="hint">
pelo <Tooltip> como em UserList.vue:48, preservando o texto exatamente como está.">

## O que este item NÃO é

<o limite. "Não é reescrever os textos — o conteúdo de cada um vai inalterado para a tooltip.
Não é mexer em tooltip que já existe.">

---
---
---

<!--
EXEMPLO PREENCHIDO — apague este bloco ao usar o molde.

---
id: tooltips-explicativas-settings
tipo: melhoria
titulo: Textos explicativos de formulário viram tooltips em Configurações
criado: 2026-09-23
objetivo: >
  Todo texto explicativo abaixo de campo, em src/views/settings, é uma tooltip do
  componente Tooltip.vue, com o texto preservado palavra por palavra.
precedente:
  padrao: src/components/ui/Tooltip.vue:1
  exemplo: src/views/users/UserList.vue:48
criterio:
  - grep -rn 'class="hint"' src/views/settings/ | wc -l  → 0
  - pnpm type-check
  - pnpm test:run
baseline:
  - grep: 34 ocorrências em 11 arquivos
  - pnpm type-check: 0
  - pnpm test:run: 0
escopo:
  pode:
    - src/views/settings/**
  nao_mexe:
    - src/api/**
    - src/components/ui/Tooltip.vue
tamanho: 11 arquivos
orcamento: 4 voltas
---

## Por que

O texto de ajuda fica embaixo do campo e empurra o formulário; em 360px a tela de
integrações vira rolagem pura. A tooltip já resolveu isso em Usuários.

## Como fazer

Cada <p class="hint">…</p> vira o slot de ajuda do <Tooltip>, exatamente como em
UserList.vue:48. O texto vai inalterado — copiar e colar, sem reescrever.

## O que este item NÃO é

Não é revisar a redação dos textos: a redação é decisão de produto. Não é mexer no
Tooltip.vue. Campo sem texto de ajuda continua sem.
-->

<!--
EXEMPLO PREENCHIDO — tipo: bug. Apague este bloco ao usar o molde.

---
id: filtro-data-ignora-fuso
tipo: bug
titulo: O filtro de período perde o último dia quando o fuso é negativo
criado: 2026-09-23
objetivo: >
  O filtro de período em Relatórios inclui o dia final inteiro, independentemente
  do fuso do navegador.
causa_raiz:
  frase: >
    O fim do período é montado com new Date(fim) e enviado em UTC, então em fuso
    negativo o dia final vira 23:00 do dia anterior.
  onde: src/views/reports/useDateRange.ts:37
  assinatura: |
    período 01/09–30/09 devolve 29 dias; o registro de 30/09 10:00 não aparece
  cenarios:
    - principal: fuso -03, período 01/09–30/09 → registro de 30/09 10:00 aparece
    - borda: fuso +02, período 01/09–30/09 → nenhum registro de 01/10 aparece
criterio:
  - pnpm test:run -t useDateRange      # escrito na volta 1; falha antes, passa depois
  - pnpm type-check
  - pnpm test:run
baseline:
  - pnpm test:run -t useDateRange: n/d (teste ainda não existe)
  - pnpm type-check: 0
  - pnpm test:run: 0
escopo:
  pode:
    - src/views/reports/useDateRange.ts
    - src/views/reports/__tests__/**
  nao_mexe:
    - src/api/**
tamanho: 1 arquivo + teste
orcamento: 3 voltas
---

## Por que

Relatório de fechamento de mês sai com um dia a menos e ninguém percebe até a
conferência. Apareceu duas vezes este mês.

## Como fazer

Volta 1 é o teste: reproduzir os dois cenários e provar que falham com a assinatura
acima. Só então corrigir em useDateRange.ts:37, normalizando o fim do período para o
último instante do dia no fuso local antes de serializar.

## O que este item NÃO é

Não é padronizar datas no resto do app, nem trocar a biblioteca de data. Não é mexer
no que a API recebe — o contrato fica igual.
-->
