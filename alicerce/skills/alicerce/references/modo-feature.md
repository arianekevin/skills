# Modo FEATURE — coisa nova dentro de projeto que já existe

Objetivo: `docs/features/<slug>.md` — o que a feature **herda**, o que ela precisa e
não existe, e o que ela **não vai inventar**.

Não é fundação de projeto (modo NOVO) nem diagnóstico do projeto inteiro (modo
AUDITORIA). A fundação já existe; o que precisa de decisão é a da feature.

## Por que este modo existe

Projeto não apodrece por uma decisão ruim. Apodrece por **convenção paralela**: duas
formas de tratar erro, dois jeitos de guardar estado, dois estilos de teste — nenhuma
declarada, cada uma defensável isoladamente, e ninguém consegue apontar o dia em que
virou duas.

Feature nova é onde isso nasce, porque quem escreve tem pressa e o projeto não reclama.
Este modo é uma folha de papel que faz o projeto reclamar.

## 1. Ler a fundação do hospedeiro

```bash
ls CLAUDE.md CONTRIBUTING.md docs/PLANO-FUNDACAO.md docs/adr docs/features 2>/dev/null
```

**Se não existir nada disso**, o projeto não tem fundação escrita. Diga e ofereça a
auditoria antes:

> "Este projeto não tem fundação documentada, então eu não teria contra o que dizer que
> a feature 'herda'. Rodo a auditoria primeiro? É meia hora e serve pras próximas
> features também."

Se o dev quiser seguir mesmo assim, siga — mas derive a convenção **lendo a feature de
referência**, e registre que ela foi inferida do código, não lida de um documento.

Se existir, leia o `CLAUDE.md` e **a feature de referência que ele nomeia**. É o molde,
e a maior parte deste modo é conformidade com ele.

## 2. A feature, em texto livre

A mesma cancela do Passo 0, agora no escopo da feature: uma ou duas frases do que ela
faz e pra quem. Sem isso não dá pra saber o que ela exige.

E uma pergunta que decide muito:

> "Ela é do mesmo domínio do projeto, ou traz domínio novo?"

Feature de cobrança dentro de um CRM traz a família financeira inteira junto — decimal,
idempotência, trilha de quem mexeu. O hospedeiro pode não ter nada disso, e aí a feature
tem exigência que o projeto não tem. Esse é o caso que mais dá errado quando ninguém
percebe a tempo.

## 3. Os três baldes deste modo

Diferentes dos outros dois modos, porque a pergunta aqui é outra.

### Herda
O que a feature usa como está, sem discussão: estrutura de pastas, regra de dependência,
forma de erro, tokens, convenção e formato de teste, tour, log. Liste explicitamente —
"herda tudo" não serve, porque é justamente onde alguém não herda sem perceber.

### Lacuna
O que ela precisa e o projeto não tem. **Cada lacuna exige uma decisão, escrita:**

| Saída | Quando |
|---|---|
| **(a) resolve local** | serve só a esta feature e não vira precedente. Registre por que não generaliza |
| **(b) vira convenção do projeto** | serve a todos. Então **vai para o `CLAUDE.md` do hospedeiro** e vale daqui pra frente — senão são duas convenções |
| **(c) a feature muda de desenho** | a lacuna era acidental, e existe um jeito de fazer que usa o que já tem |

A saída (b) é a única que evita apodrecimento, e é a mais esquecida: se a feature
inventa um jeito melhor e ninguém promove, o projeto passa a ter o jeito novo e o velho
para sempre.

### Não inventa
O que ela **poderia** fazer diferente e não vai. Escrito, mesmo parecendo óbvio — é esta
lista que impede a segunda convenção, e ela custa três linhas.

## 4. O que a feature nasce tendo

Herdado da régua e não negociável, qualquer que seja o tamanho:

- **Teste, no formato do molde** — o teste da feature de referência é o padrão, não uma
  sugestão
- **Tour, com âncora** nos componentes que ele aponta
- **Os quatro estados**, se tem tela
- **O ator até quem grava**, se ela escreve dado

## 5. Quando isto não é uma feature

Se ela tem deploy próprio, banco próprio ou ciclo de vida independente, **não é feature:
é projeto novo morando no mesmo repositório**. Diga isso e vá para o modo NOVO — a
diferença não é tamanho, é se ela tem fundação própria ou usa a do hospedeiro.

O sinal mais confiável: se a resposta a "de quem é o `CLAUDE.md` que vale aqui?" for
"o dela", é projeto.

## 6. Escrever

`docs/features/<slug>.md`, a partir de `assets/FEATURE.template.md`, indexado no
`README.md` do projeto. Se alguma lacuna caiu na saída (b), **edite também o
`CLAUDE.md`** do hospedeiro — é o único caso em que este modo toca em documento que não
é dele.
