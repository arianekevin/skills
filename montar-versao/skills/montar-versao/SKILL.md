---
name: montar-versao
description: Monta versão do nectarcrm — versão principal (tag na alpha, vYY.T.NNN) ou hotfix (vYY.T.NNN.H), que parte da versão ou hotfix mais recente e leva só os commits escolhidos, não a alpha inteira. Dá push na tag (e na branch do hotfix). Use quando pedirem "monta a versão", "fecha a versão", "gera a tag", "monta um hotfix", "hotfix com o WEB-1234", "leva esse fix pra produção sem a alpha".
---

# Montar versão e hotfix (nectarcrm)

Tudo entra na alpha primeiro. A versão principal é o commit de bump do pom em cima da
ponta da alpha, com a tag.
O hotfix é uma branch `hotfix/<versão>` que nasce da tag mais recente e recebe por
cherry-pick só os commits pedidos — que já precisam estar na alpha.

O trabalho mecânico é do script `scripts/montar.sh`, ao lado deste arquivo. Rode de
dentro do clone (ou `REPO=<clone>`). Não refaça à mão. Os padrões são do nectarcrm e
mudam por variável: `ALPHA` (origin/alpha), `POM` (br.com.colmeia.crm/pom.xml),
`ARTIFACT` (nectar-crm).

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Aqui pesa a escrita fora do
repositório: invocar esta skill é o pedido para dar push **na tag** (e na branch do
hotfix) que ela montar, e no commit de bump da principal na alpha — em mais nada.

```
montar.sh principal [--plano]                          # sempre da ponta da origin/alpha
montar.sh hotfix    [--plano] [--base vYY.T.NNN] <commit>...
montar.sh servico   [--plano] <tag-do-crm>             # no clone do serviço
```

## Numeração

- Principal: `vYY.T.NNN` — YY ano, T trimestre da data de hoje (1–4), NNN sequência
  de 3 dígitos no trimestre, recomeça em 001. É o que as tags v26.1–v26.4 seguem.
- Hotfix: `vYY.T.NNN.H` — H sequência sobre aquela principal.
- O script calcula; nunca escolha número à mão.
- Serviço que sobe junto (sparknectarbi etc.): a tag é **sempre a do CRM**, mesmo que a
  sequência do serviço pule números. Nunca calcule número próprio para o serviço.

## Versão principal

1. `montar.sh principal --plano` e mostre: número, ponta da alpha, quantos commits
   desde a anterior.
2. `montar.sh principal` cria, num worktree temporário, o commit
   `chore: bump versao para <versão>` no pom sobre a ponta da alpha e a tag nele.
   Dá push na tag e no bump na alpha, juntos (ver Publicar).

## Serviço que sobe junto

Quando o pedido inclui um serviço (ex.: "gera a versão no crm e no sparknectarbi"):

1. Monte primeiro a principal do CRM: o `--plano` dela dá a tag.
2. No `--plano`, mostre a mesma tag para cada serviço:
   `REPO=<clone do serviço> montar.sh servico --plano <tag-do-crm>`.
3. Depois de montar o CRM, rode `montar.sh servico <tag-do-crm>` em cada serviço. A tag
   vai direto na ponta da alpha do serviço, **sem bump**: o bump é só do CRM.

## Hotfix

1. **Resolver o que vai.** O pedido costuma vir em ticket (WEB-, IN-, LAT-, DEL-), PR
   ou SHA. Ticket → `git log origin/alpha --format='%h %cs %s' -i --grep='<ticket>'`
   (pegue todos os commits do ticket, não só o último). PR → os commits dele na alpha.
   **Correções feitas no PR depois de aberto também vão** — de revisor, corretor
   automático ou outro autor —, e elas podem não citar o ticket na mensagem. Confira no
   Bitbucket os commits e o `merge_commit` de cada PR mergeado: squash junta tudo num
   commit só; rebase deixa um commit por correção, e todos entram.
   Commit que não está na alpha não entra: é preciso passar pela esteira antes.
2. **Base.** Por padrão, a versão mais recente de todas (principal ou hotfix dela).
   Hotfix de uma principal mais antiga: `--base vYY.T.NNN`.
3. `montar.sh hotfix --plano ...` e mostre base, número novo, o que aplica e o que
   pula (já está na base, por SHA ou por patch igual).
4. `montar.sh hotfix ...` cria, num worktree em `.claude/worktrees/hotfix/<versão>`,
   a branch, os cherry-picks (`-x`, na ordem da alpha) e a tag, e dá push na branch e
   na tag. O hotfix não mexe no pom. Nada muda no checkout principal.
5. **Conflito (saída 3):** o script desfaz tudo e lista os arquivos e os commits da
   alpha que mexem neles e a base não tem. Leve isso à pessoa: incluir a dependência
   ou desistir do commit é decisão dela. Não resolva conflito na mão.
6. Depois, compile no worktree (`JAVA_HOME=$(/usr/libexec/java_home -v 23)
   ./mvnw -q -o compile` em `br.com.colmeia.crm`) e reporte o resultado.

## Publicar

O script dá push na tag (e, no hotfix, na branch `hotfix/<versão>`). Na principal, o
commit de bump vai **sempre junto** para a alpha, no mesmo push atômico da tag: sobem
os dois ou nenhum. Se a alpha andou nesse meio-tempo, o push é recusado e nada sobe;
rode de novo. "Sobe" no vocabulário do time é pôr num ambiente (beta etc.).

## Erros comuns

- Tag ou branch já existe → alguém montou antes; `git fetch --tags` e releia.
- `refname ... is ambiguous` → há branch com nome de tag; o script usa `refs/tags/`.
- Pedido de hotfix com commit que não está na alpha → recuse e explique.
