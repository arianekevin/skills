# {PROJETO} — instruções do projeto

{Uma frase do que é e pra quem.}

Antes de propor qualquer coisa estrutural, leia `docs/PLANO-FUNDACAO.md` — escopo, o que
foi **adiado de propósito** e com qual gatilho revisitar. As regras de trabalho
(definition of done, testes, commits) estão em `CONTRIBUTING.md` e **valem para você
também**.

## Comandos

_{Preenchido pela `obra`, que é quem sabe os comandos reais.}_

## Regras que não se quebram

_Cada uma é cara de retrofitar. A coluna da direita é o que separa regra de desejo._

| # | Regra | Onde é imposta |
|---|---|---|
| 1 | | |

{Uma explicação curta por regra: o que quebra sem ela.}

## Estrutura

**Eixo de organização:** {por domínio/feature, ou outro — e a forma de `src/`}
**Regra de dependência:** {ex.: domínio não importa HTTP nem banco}
**Feature de referência:** _{nomeada pela `obra` na Fase 2}_ — copie o molde dela.

## Traço de uma requisição

_{Preenchido quando existir código: entra em X, valida em Y, grava em Z, erro sobe para
o handler único em W. Estrutura diz onde as coisas moram; o traço diz por onde passam —
é o que permite entender o projeto numa passada.}_

## UI

{Se não houver interface: "Não se aplica — projeto sem interface."}

- **Tokens semânticos** (`--fundo`, `--texto`), nunca literais (`--cinza-100`)
- **Nenhuma cor literal dentro de componente**
- Alvo de toque é token, não exceção avulsa
- Toda tela que carrega dado tem os quatro estados: carregando, vazio, erro, sem permissão

## Erros

{Forma única de erro, e a regra de não capturar em cada ponto.}

## Armadilhas já encontradas aqui

_{Alimentada durante a obra e no dia a dia. Cada armadilha custou tempo de alguém uma
vez; escrever aqui é o que impede a segunda.}_

- {ainda nenhuma}
