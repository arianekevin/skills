# {NOME DA FEATURE}

_Especificado em {DATA} pela skill `alicerce`, modo FEATURE. O projeto já tem fundação:
este documento diz o que esta feature **herda**, o que ela precisa e não existe, e o que
ela **não vai inventar**._

## O que é

**Faz:** {uma ou duas frases}
**Pra quem:** {}
**Domínio:** {o mesmo do projeto / traz domínio novo — qual, e o que ele exige}

**Fundação do hospedeiro:** {lida de `CLAUDE.md` / **inferida do código**, porque o
projeto não tem fundação escrita}
**Molde seguido:** {caminho da feature de referência}

---

## Herda

_Explicitamente. "Herda tudo" não serve: é justamente onde alguém não herda sem perceber._

| O quê | De onde |
|---|---|
| Estrutura de pastas | |
| Regra de dependência | |
| Forma de erro | |
| Formato e local de teste | |
| Tokens e estados de UI | |
| Tour: âncora e definição | |
| Log e contexto (ator) | |

## Lacunas

_O que a feature precisa e o projeto não tem. Cada uma com decisão escrita._

| Lacuna | Saída | Justificativa |
|---|---|---|
| | (a) resolve local / (b) vira convenção do projeto / (c) muda o desenho | |

**Promovido para o `CLAUDE.md` do projeto:** {as lacunas que caíram em (b) — se nenhuma,
escrever "nenhuma"}

Lacuna resolvida localmente sem virar convenção é dívida aceita de propósito: registre
por que não generaliza, senão a próxima feature copia sem saber que era exceção.

## Não inventa

_O que esta feature poderia fazer diferente e não vai. É esta lista que impede a segunda
convenção — e ela custa três linhas._

- {ex.: não cria segunda forma de erro; usa `ErroDeDominio`}
- {ex.: não traz biblioteca de estado nova; usa o que a feature de referência usa}

---

## O que ela nasce tendo

_Não negociável, qualquer que seja o tamanho._

| Item | Onde | Pronto quando |
|---|---|---|
| Teste no formato do molde | | |
| Tour com âncora | | |
| Os quatro estados (se tem tela) | | |
| Ator até quem grava (se escreve dado) | | |

## Fora de escopo

- {o que esta feature explicitamente não faz}
