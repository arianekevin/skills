# O ritual de cada item

Idêntico para todos os itens, sem atalho, mesmo no item de dois arquivos. O ritual é o que permite
ao dev confiar nos commits de manhã sem reler cada um: se um item deu certo, ele passou por aqui; se
não passou por aqui, ele não deu certo.

Uma linha na conversa por item, enquanto roda. O detalhe vai para o relatório.

---

## 1. Ler o item do disco

Sempre do arquivo, mesmo que você o tenha lido há dez minutos. A conversa pode ter sido resumida; o
arquivo não muda sozinho.

Do frontmatter saem, diretamente, os insumos do `/ciclo`: `objetivo`, `criterio` (o indicador),
`orcamento` (as voltas), `escopo.pode` e `escopo.nao_mexe`.

## 2. Conferir a âncora do item

O passo é o mesmo para os dois tipos: **o item afirma algo sobre o código, e você confere na fonte
antes de trabalhar.** Afirmação que não se sustenta é item bloqueado, nunca item para improvisar —
mova para `docs/melhorias/bloqueado/`, escreva a linha do que falta, siga para o próximo.

**`tipo: melhoria` → o precedente.** O item aponta `precedente.padrao` e `precedente.exemplo` com
caminho e linha. Confira que ainda existem e que dizem o que o item diz; um refactor da semana
passada pode ter movido o componente. Sem precedente, o que você produziria de madrugada é um padrão
novo que ninguém escolheu.

**`tipo: bug` → a causa raiz.** O item traz `causa_raiz.frase` e `causa_raiz.onde`. Vá até o
caminho e a linha e **leia o código**: ele precisa explicar a frase. Se o trecho não estiver mais
lá, ou não sustentar a causa, o item está bloqueado — não diagnostique por conta própria de
madrugada. Diagnóstico é trabalho com o dev na sala, e a `bug-diagnostico` existe para isso.

Confira também, aqui, o corte de risco: item de bug que toca dado, cobrança, permissão,
autenticação, contrato de API, ou que não tem reprodução determinística, **não roda à noite** mesmo
tendo chegado a `pronto/`. Bloqueado, com o motivo.

## 3. Baseline do critério

Rode **cada membro do critério separadamente**. Nunca encadeie com `&&`: a corrente curto-circuita
no primeiro que falha e você fica cego nos demais. Guarde o resultado de cada um.

Dois desfechos que encerram o item aqui mesmo:

- **O critério já passa** (a contagem já está em zero — alguém arrumou durante a semana). O item
  está **feito sem trabalho**: mova para `docs/melhorias/feito/`, registre no relatório que já
  estava satisfeito, **não commite nada**. É o desfecho mais barato, e acontece. Em item de bug isso
  só vale se o teste de regressão já existir e passar; se ele ainda não existe, o desfecho
  equivalente é o portão do passo 3b.
- **Um membro do critério nem roda** (comando não existe, falta serviço de pé). Item **parado**:
  registre o comando e a saída, não tente contornar, não invente substituto. Um critério que não
  roda não é uma régua.

  **A exceção é o teste de regressão de um item `tipo: bug`**, que o próprio item declara como
  `n/d (teste ainda não existe)` no baseline — ele é escrito por você no passo 3b, e é a única coisa
  que pode faltar no baseline. Qualquer outro membro ausente continua sendo parada.

## 3b. Item de bug: a volta 1 é o teste que falha

Só para `tipo: bug`, e antes de qualquer correção. Escreva o teste dos `cenarios` — o principal e o
de borda — e rode.

O teste precisa **falhar com a assinatura que está no item** (`causa_raiz.assinatura`). Esse é o
portão, e ele é mecânico:

- falhou com a assinatura esperada → a reprodução está de pé, siga para a correção;
- **passou de cara** → o bug não está onde o item diz, ou já foi corrigido. Item **parado**: commite
  o teste sozinho, se ele for legítimo, e registre. Não saia procurando o bug verdadeiro;
- **falhou por outro motivo** (erro de compilação no teste, dependência faltando, outra mensagem) →
  reprodução errada. Item **parado**, com as duas assinaturas coladas no relatório: a esperada e a
  obtida. É a informação mais útil que a noite pode produzir sobre esse bug.

Sem esse portão, a correção de madrugada não tem como provar que consertou o bug do item, e não
outra coisa. Um teste escrito depois do fix passa por construção.

## 4. Executar pela `ciclo`

Monte a spec com os campos do item — ela já está fechada, então a `ciclo` não deve fazer pergunta
nenhuma. Passe explicitamente:

- **objetivo**: o campo `objetivo`, palavra por palavra;
- **indicador**: os comandos de `criterio`, cada um rodado sempre, sem `&&`;
- **escopo**: `escopo.pode` e `escopo.nao_mexe`, e mais nada;
- **orçamento**: as voltas do item;
- **como fazer**: a seção *Como fazer* e a seção *O que este item NÃO é* — essa segunda é a que
  impede o loop de "melhorar um pouco mais" fora do que foi combinado.

Em item de `tipo: bug`, o fluxo é o da **`bug-guardrail`** — as cancelas dela (causa raiz, cenários,
escopo) já foram conferidas nos passos 2 e 3b, e a correção mira a causa que está escrita, não o
sintoma que o teste mostra. Correção que faz o teste passar sem tocar em `causa_raiz.onde` merece
desconfiança: registre isso no relatório, porque de manhã é exatamente o commit que ele vai querer
olhar primeiro.

Valem as paradas da própria `ciclo`: mesma assinatura de falha duas voltas seguidas, orçamento
esgotado, correção que exigiria sair do escopo. Nenhuma delas vira pedido de mais voltas — aqui não
há a quem pedir. Item que estourou o orçamento é item falho, e amanhã o dev decide.

## 5. Revisar o próprio diff

Rode a **`bug-reviewer`** sobre o diff do item antes de qualquer commit. É o único olho que esse
código vai ter até de manhã.

Achado grave — comportamento alterado, caso não coberto, texto de usuário modificado sem o item
pedir — **reverte o item**. Não tente consertar o achado numa volta extra: você já está fora do
orçamento e sem supervisão. Anote o achado no relatório; ele vale mais que o commit.

## 6. Guarda de regressão

Rode **todos** os comandos mecânicos do projeto — `type-check`, `test`, `lint`, `build` —, inclusive
os que não estão no critério do item, e inclusive os que você acabou de rodar na volta final da
`ciclo`. Cada um separado, resultado registrado.

A guarda não é o critério: o critério diz se o item ficou pronto, a guarda diz se o resto continua
de pé. Guarda vermelha reverte o item mesmo com o critério verde. Não existe "avanço parcial" numa
noite sem supervisão.

## 7. Conferir o escopo

```
git status --porcelain
```

Todo caminho listado tem que casar com `escopo.pode`. Um arquivo fora, mesmo que a mudança nele
pareça óbvia e correta, é **escopo estourado** — reverta o item inteiro e registre. O dev combinou
um recorte; entregar mais que o combinado, sem ele por perto, é a forma mais fácil de torrar a
confiança nesta skill.

## 8. Commitar, ou reverter

**Reverter** é seguro aqui — e só aqui — porque a cancela 2 garantiu a árvore limpa no início da
noite e cada item começa de um commit da própria branch. Não há trabalho não commitado do dev para
levar junto:

```
git restore --source=HEAD --staged --worktree -- <globs do escopo>
```

Depois de reverter, confirme com `git status --porcelain` que a árvore voltou a ficar vazia. Reversão
que não foi conferida contamina o próximo item, e aí a noite inteira vira uma coisa só.

**Commitar**, quando critério verde, revisão limpa, guarda verde e escopo respeitado:

```
git add -- <globs do escopo>        # nunca -A, nunca .
git commit
```

A mensagem segue a convenção do repositório onde você está — leia `git log --oneline -20` antes de
inventar formato; idioma e prefixo saem de lá, não daqui. O corpo carrega o que a manhã precisa:

```
<assunto na convenção do repo>

Item: <id>          docs/melhorias/feito/<id>.md
Critério: <comando> → <resultado> (antes: <baseline>)
Guarda: type-check=0  test=0  lint=0
Voltas: 2 de 4

Turno: <AAAA-MM-DD>
```

O trailer `Turno:` existe para ele filtrar a noite inteira com um `git log --grep`.

## 9. Fechar o item no disco

No mesmo momento — não no fim da noite:

- **mova o arquivo** para a pasta do estado final: `feito/`, `bloqueado/` (faltou algo que só ele
  resolve) ou de volta para `pronto/` (falhou, mas continua válido para outra noite);
- **anexe ao arquivo** uma seção `## Execução <AAAA-MM-DD>` com o desfecho, o commit (ou o motivo da
  reversão), o resultado de cada membro do critério e as voltas gastas;
- **escreva a linha do item no relatório**.

Item que volta para `pronto/` depois de falhar leva junto o que já foi tentado. Sem isso, a noite
seguinte repete a mesma hipótese — e é assim que uma pauta vira uma esteira de trabalho inútil.
