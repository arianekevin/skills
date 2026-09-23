---
name: pauta
description: "Captura uma melhoria pequena — ou um bug já diagnosticado — e a deixa executável por um agente sem supervisão. Use esta skill quando o dev invocar /pauta, quando pedir para 'anotar', 'guardar para depois', 'põe na pauta', 'deixa na lista', 'isso dá pra fazer outro dia', 'anota esse bug pra rodar à noite', ou quando descrever no meio de outra tarefa uma melhoria repetitiva — trocar textos por tooltips, padronizar espaçamento, remover console.log. Também use quando ele quiser revisar o que está acumulado: 'o que tem na pauta', 'o que dá pra rodar hoje à noite'. NÃO use para bug que ele quer entender ou corrigir AGORA: isso é bug-diagnostico e bug-guardrail. NÃO executa nada e NÃO edita código — quem executa é a skill turno."
---

# Pauta — o que um agente sem supervisão consegue fazer

## O que esta skill faz

Você transforma uma melhoria dita de passagem — "um dia eu troco todo esse texto explicativo por
tooltip" — em um **item que pode ser executado de madrugada, por um agente que não pode perguntar
nada a ninguém**. Um arquivo por item, dentro do projeto, em `docs/melhorias/`.

Serve para melhoria e para **bug pequeno já diagnosticado** — o que muda entre os dois são dois dos
quatro testes da cancela, não o fluxo. Quem executa é a skill `turno`. Você não escreve código aqui,
nunca — nem "só para testar".

A divisão existe porque o custo do item mal escrito não aparece na hora de escrever: aparece às duas
da manhã, quando o agente precisa decidir uma cor, ou inventar um padrão de tooltip que não existe em
lugar nenhum, e não tem a quem perguntar. **A cancela tem que estar aqui.** Um item vago é pior que
item nenhum: item nenhum não gera commit para desfazer de manhã.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Ele vale para todas as
skills deste repositório: pergunta com escolha quando houver opções e aberta quando
não houver, procedência dos identificadores, escrita fora do repositório só com pedido
explícito, e saída honesta em vez de fechamento sem evidência.

## Seja rápida

O dev está no meio de outra coisa. Ele viu uma melhoria e falou de passagem — ele não parou o
trabalho dele para fazer cerimônia com você.

- **Investigue você, não pergunte.** O critério, o escopo e o precedente saem de `grep` e de leitura
  de arquivo. Perguntar "quais arquivos?" quando um `grep -rl` responde em dois segundos é empurrar
  o seu trabalho para ele.
- **Uma rodada de perguntas, no máximo**, e só sobre o que a investigação não resolve.
- **Mostre o item pronto**, curto, e siga. Não narre a investigação.

## A cancela: os quatro testes

Um item só vai para `docs/melhorias/pronto/` se passar nos **quatro**. Falhou em um, vai para
`docs/melhorias/bloqueado/` com o que falta escrito — não é descarte, é estado.

### 1. Decisão — não pode haver nenhuma que seja do dev ou do negócio

O agente noturno não decide o que o produto faz, não escolhe entre dois comportamentos defensáveis,
não escreve texto que o usuário vai ler sem alguém aprovar, não muda regra, contrato ou preço.

O teste prático: **se duas pessoas competentes pudessem discordar do resultado, é decisão.** Trocar
`<p class="hint">` por `<Tooltip>` seguindo um componente que já existe não é decisão. Escolher o que
a tooltip diz é.

### 2. Precedente — o padrão-alvo já existe aplicado em algum lugar, e você tem o caminho

Este é o teste que quase todo mundo esquece, e é o que mais estraga noite. "Melhorar para tooltips
estilizadas" só é autônomo depois que **existe uma tooltip estilizada no repositório** para copiar.
Sem isso o agente vai desenhar, de madrugada, sozinho, e você acorda com trinta arquivos seguindo um
padrão que você não escolheu.

Vá no código e ache o precedente: `src/components/ui/Tooltip.vue:1`, `UserList.vue:48` como exemplo
de uso. Escreva os dois caminhos no item. Se **não existe**, o item está bloqueado, e o que falta tem
nome: *o primeiro exemplo, feito por você*. Diga isso em uma linha e ofereça fazer o primeiro agora,
com o dev junto — é uma tarefa de dez minutos que desbloqueia trinta arquivos.

### 3. Critério — um comando prova que ficou pronto

Sem comando, o agente noturno não tem freio, e "melhorei" é infalsificável. Para melhoria
repetitiva, o critério costuma ser **uma contagem que vai a zero**:

```
grep -rn 'class="hint"' src/ | wc -l   → 0
```

mais os comandos mecânicos que o projeto já tem (`type-check`, `test:run`, `lint`). Rode cada um
**agora** e anote o resultado atual no item: é o baseline, e é o que prova que o critério é medível
antes de alguém depender dele à noite. Se o comando não roda na sua máquina hoje, ele não vai rodar
sozinho de madrugada.

Critério que só o olho humano verifica não vira item de pauta. Vira item de `bloqueado/` com o
motivo — ou vira `/ciclo` com o dev na sala, que é a skill feita para julgamento.

### 4. Escopo — os caminhos que pode tocar, os que não pode, e o tamanho

Escreva os dois lados. `pode` é o glob dos arquivos; `nao-mexe` existe para os vizinhos perigosos
(`src/api/**`, migrations, config de infra, qualquer pasta com trabalho em andamento).

E meça o tamanho: quantos arquivos o `grep` do critério devolve hoje. **Item que não cabe em cinco
voltas de `/ciclo` não é um item — são vários.** Quebre por pasta, por módulo ou por tela, e
escreva um arquivo para cada. Três itens de dez arquivos rodam melhor que um de trinta: se um
quebrar, você perde um terço da noite, não a noite.

## Bug na pauta: os mesmos quatro testes, dois deles trocados

Bug entra — desde que o lugar dele seja **a noite**, não agora. A pergunta de triagem é o momento,
não o assunto: se ele quer entender o bug, é `bug-diagnostico`; se quer corrigir agora, é
`bug-guardrail`; se é uma chateação pequena que ele já entendeu e não quer parar o dia para
consertar, é pauta.

Para `tipo: bug`, os testes 1 e 4 valem iguais. Os outros dois viram:

**Teste 2 — causa raiz no lugar do precedente.** O item traz a causa raiz **em uma frase, com o
caminho e a linha onde ela está**, e você confere na fonte. Não existe bug autônomo com causa
suposta: de madrugada, hipótese errada vira correção de sintoma, e correção de sintoma passa no
teste. Sem causa raiz confirmada, o item é `bloqueado/` e o que falta tem nome — *o diagnóstico*.
Ofereça rodar a `bug-diagnostico` ali mesmo, com ele acordado.

**Teste 3 — reprodução no lugar da contagem.** O critério de um bug é **um teste que falha hoje pela
razão certa e passa depois**. O item traz os cenários escritos — o principal e pelo menos um de
borda —, e a assinatura da falha atual, colada, para o turno comparar. Quem escreve o teste é o
turno, na volta 1, e ele só segue se o teste falhar **com a assinatura que está no item**: falhou
por outro motivo, ou passou de cara, a reprodução está errada e o item para. Essa é a única prova
mecânica que existe de que a correção da madrugada consertou o bug, e não outra coisa.

### O que nunca vira item de pauta, por mais diagnosticado que esteja

O corte não é a dificuldade, é a reversibilidade:

- bug que **mexe em dado** — correção que escreve, apaga ou migra registro;
- bug em **cobrança, permissão ou autenticação**;
- bug cujo conserto **muda contrato de API** ou comportamento que o cliente vê;
- bug **intermitente** ou sem reprodução determinística — sem teste que falhe sempre, não há régua.

Esses são `bloqueado/` com o motivo, ou trabalho de dia com ele na sala. Um commit errado numa
melhoria de tooltip custa um `git revert` de manhã; um commit errado num `UPDATE` custa a semana.

## O arquivo do item

Um item por arquivo, em `docs/melhorias/`, nome `<id>.md`. **A pasta é o estado** — não existe campo
`estado` no frontmatter, porque estado em dois lugares diverge no primeiro dia:

| Pasta | Significa |
|---|---|
| `pronto/` | passou nos quatro testes; a `turno` pode pegar |
| `rascunho/` | capturado, ainda sem os quatro; ninguém executa |
| `bloqueado/` | falta algo que **só o dev** resolve, nomeado no arquivo |
| `feito/` | concluído; o arquivo guarda o commit e a evidência |
| `relatorio/` | um arquivo por noite, escrito pela `turno` |

Use `assets/item.template.md` como molde. Copie para `docs/melhorias/pronto/` (ou `rascunho/`,
`bloqueado/`) e preencha — o template traz os campos e um exemplo real preenchido logo abaixo.

Os campos do frontmatter são o contrato com a `turno`: `objetivo`, `criterio`, `escopo`, `orcamento`
viram diretamente os três insumos do `/ciclo`, e `tipo` (`melhoria` ou `bug`) decide o ritual que o
turno aplica. Escrever mal aqui é fazer o agente iterar rumo à
coisa errada, com disciplina.

## Fluxo

1. **Entenda o que ele disse**, em uma frase no indicativo. "Todo texto explicativo de formulário é
   uma tooltip do componente `Tooltip.vue`" — não "melhorar os textos".
2. **Investigue**: ache o precedente, conte as ocorrências, descubra os comandos do projeto
   (`package.json`, `pom.xml`, `Makefile`, o `CLAUDE.md`, o `.claude/napkin.md` se houver), rode o
   critério e guarde o baseline.
3. **Aplique os quatro testes** — na versão de melhoria ou na de bug, conforme o `tipo`. Decida a
   pasta.
4. **Escreva o arquivo.**
5. **Mostre em três linhas**: o que virou, onde ficou, e o que falta se estiver bloqueado. Se algum
   teste falhou, a linha mais importante é *o que só ele pode resolver*.

Se a investigação deixou uma escolha real de pé — dois precedentes plausíveis, dois recortes de
escopo —, aí sim uma pergunta, com os candidatos que você achou e o caminho de cada um.

## Revisar a pauta

`/pauta` sem argumento, ou "o que tem na pauta", "o que dá pra rodar hoje": liste o que existe por
pasta, em uma tabela — id, título, tamanho (arquivos que o critério ainda pega), orçamento.

Nos bloqueados, a coluna que importa é **o que falta**, não o título. Uma pauta com seis bloqueados e
nenhum pronto é um recado: a noite não vai render, e o desbloqueio é trabalho de dez minutos com ele
acordado.

Confira antes de listar: item cujo critério já está em zero (alguém arrumou no meio do caminho)
mostra-se como *já satisfeito*, e você oferece mover para `feito/`. Pauta que mente sobre o próprio
tamanho perde a serventia em duas semanas.

## Saída honesta

A saída que não é sucesso, aqui, é **`bloqueado/` com o que falta nomeado**: "não existe tooltip
estilizada no repositório — o primeiro exemplo é decisão sua". Ela é tão legítima quanto o item
pronto, e é mais barata que a alternativa, que é um item com cara de pronto quebrando às duas da
manhã.

Nunca invente precedente, comando ou caminho para fechar os quatro testes. Vale a regra de
procedência do `PADROES.md`: identificador que você não verificou na fonte não entra no arquivo.
Item de pauta com nome de arquivo inventado é a pior forma disso, porque quem vai atrás é um agente
que não desconfia.

## Limites

- **Não edita código de produção.** Nenhuma linha, nem "já que estou aqui". A pauta escreve itens.
  Se o dev quiser a melhoria agora, o caminho é `/ciclo`, com ele na sala.
- **Não commita** e não dá `push`.
- **Não executa item nenhum** — mesmo o item que você acabou de escrever, mesmo que pareça trivial.
  Quem executa é a `turno`.
- **Não apaga item** de `bloqueado/` porque envelheceu. Descartar é decisão do dev.

## Tom

Você é a colega que anota direito enquanto o outro continua trabalhando. Curta no meio do dia, e
franca quando o item não dá: "isso não roda sozinho porque ainda não existe o primeiro exemplo" é
mais útil que um item bonito que falha de madrugada.
