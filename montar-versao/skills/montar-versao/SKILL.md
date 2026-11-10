---
name: montar-versao
description: Prepara e monta versão do nectarcrm — o preparo da próxima versão de bugfix (bump do pom na alpha, versão no campo Versão do YouTrack, tickets aptos do backend nela e ticket de versão para o Hugo), a versão principal (tag na alpha, vYY.T.NNN) ou hotfix (vYY.T.NNN.H), que parte da versão ou hotfix mais recente e leva só os commits escolhidos, não a alpha inteira. Dá push na tag (e na branch do hotfix; na principal, também no bump na alpha). Use quando pedirem "prepara a próxima bugfix", "prepara a próxima versão", "abre a versão da semana", "monta a versão", "fecha a versão", "gera a tag", "monta um hotfix", "hotfix com o WEB-1234", "leva esse fix pra produção sem a alpha".
---

# Preparar e montar versão, e hotfix (nectarcrm)

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
montar.sh preparar  [--plano]                          # próxima principal: bump + YouTrack
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

## Preparar a próxima versão de bugfix

A versão de bugfix sobe na segunda. O preparo deixa tudo pronto na semana anterior. Invocar
este modo é o pedido para o push do bump na alpha e para escrever no YouTrack: valor novo no
campo Versão, o campo Versão dos tickets e o ticket de versão.

1. `montar.sh preparar --plano` e mostre o que ele imprime:
   - número da próxima principal;
   - bump do pom;
   - tickets que entram, com o motivo de cada um: commit ou PR e em qual projeto;
   - tickets que ficam fora;
   - serviços que entram;
   - descrição do ticket de versão.
2. **Resolva o que vier `A CONFIRMAR` perguntando a quem acionou a skill** (escolha para
   marcar). Na dúvida, pergunte, não decida:
   - Projeto com ticket apto que não está em `~/.claude/montar-versao/projetos.conf`:
     pergunte se ele sobe na versão de bugfix de segunda. Registre a resposta no arquivo
     (`<slug> entra <rótulo>` ou `<slug> fora`) e rode o plano de novo.
   - Ticket que já tem versão de outra linha no campo (ex.: `vue26.4.005`): trocar apaga a
     dela. Se for trocar, use `TROCAR="IN-1 IN-2" montar.sh preparar`. Se ficar na outra
     linha, use `MANTER="IN-1 IN-2" montar.sh preparar`: o ticket sai desta versão e o
     campo não muda. Os dois podem ir juntos, cada ticket em um.
3. `montar.sh preparar` faz, nesta ordem:
   - commit `chore: bump versao para <versão>` no pom, sobre a ponta da alpha, e push
     (só fast-forward);
   - cria o valor `<versão>` no campo Versão do YouTrack (bundle compartilhado);
   - põe a versão nos tickets que entram;
   - cria no PID o ticket "Versão - DD/MM" (DD/MM = próxima segunda), com Type Rotina,
     Responsável Hugo Freitas, Projeto "Release e CI/CD", Prioridade Urgente e o campo
     Versão.

   Rodar de novo é seguro. Bump feito não se refaz, e ticket que já está na versão fica
   como está. O ticket de versão é atualizado, não duplicado.
4. **Outros ajustes.** Depois que nada está `A CONFIRMAR`, cubra o que sobe sem ticket na
   versão: commits de LAT, DEL, IN de outra linha, ticket que não está apto, commit sem
   ticket, e os serviços que entram. Para cada área, o QA recebe o que pode ter sido
   impactado. Não é o detalhe do commit. Exemplo: um LAT mexeu no filtro da listagem de
   contatos, então o item é "Listagens de contatos".
   1. Material: `REPO=<clone> python3 scripts/preparar.py --versao <versão>
      --outros-material [--manter ...] [--trocar ...] > material.json`. São os commits da
      versão, com assunto e arquivos, sem os que citam um ticket dela. Commit que cita um
      ticket da versão é testado pelo dele.
   2. Mapeie os pontos a testar. Cada ponto entra numa seção só, a do CRM mais afetada
      (Contatos, Oportunidades, Tarefas, Configurações...). Vários commits podem virar um
      ponto.

      Cada ponto é uma ação curta que o QA executa, com o perfil quando ele importa:
      "Listar contatos", "Abrir modal de tarefa", "Visualizar oportunidade com usuário
      básico". Leia o corpo do commit para achar a ação.
      - Não escreva passo a passo.
      - Não escreva área genérica ("Tabelas: permissões").
      - Não escreva o que mudou ("passa a validar...").
   3. Monte os tickets:
      - seção com mais de 8 pontos fica num ticket só dela;
      - as menores se juntam, até 8 pontos por ticket;
      - junte seções próximas: Oportunidades com Qualificação, Tarefas com Compromissos.
      Organize os tickets de forma fluida.
   4. Escreva o agrupamento num JSON:
      ```json
      {"tickets": [{"secoes": [{"nome": "Oportunidades", "itens": [
          {"testar": "Mudar etapa pelo stepper e pela barra lateral", "commits": ["4a022a5909"]}]},
        {"nome": "Qualificação", "itens": [...]}]}]}
      ```
   5. Rode `OUTROS=<json> montar.sh preparar --plano` e mostre os tickets. Depois rode o
      mesmo comando sem `--plano`.

   O script recusa:
   - commit do material sem item;
   - sha que não é da versão;
   - seção repetida;
   - ticket que junta seções e passa de 8 itens (`OUTROS_LIMITE`).

   Cada ticket nasce no WEB, em "Apto para teste", com Ambiente de Teste Alpha e o campo
   Versão. O título é "Outros ajustes - <seções>". Rodar de novo atualiza o ticket de mesmo
   título. Se o agrupamento mudou, o ticket com título que não existe mais sai como
   `SOBROU`: leve isso a quem acionou.

**Quais tickets entram.** WEB e IN em "Apto para teste" com commit no ramo de teste do
projeto que a última versão dele não tem, ou com PR aberto para esse ramo. O ramo de teste
é `alpha`, ou `homolog` quando o projeto não tem alpha (ex.: for-whats). Os projetos vêm:
- dos clones locais do workspace (irmãos do nectarcrm);
- dos links do Bitbucket citados nos próprios tickets, já que o token não lista o workspace.

Projeto sem clone só é lido pelos PRs e pela citação.

O nectarcrm sempre entra. Os outros projetos seguem o `projetos.conf`:
- `entra`: o ticket entra na versão, e o projeto ganha a linha `Imagem do serviço <rótulo>:
  <versão>` no ticket de versão. Na montagem, o projeto recebe a tag do CRM
  (`montar.sh servico`).
- `fora`: projeto que não sobe na segunda, como o reloaded, cujo Vue sobe à parte. O
  ticket só dele fica fora.

**Serviço entra pelo commit, não só pelo ticket.** Clone com commit no ramo de teste que a
última principal dele não tem entra na versão mesmo sem ticket apto: a versão leva tudo que
foi commitado. O plano lista em "Candidatos a tag" todo serviço com ramo de teste e quantos
commits cada um traz. Projeto `fora` não entra; projeto fora do `projetos.conf` com commit
cai em `A CONFIRMAR`; `SEM_SERVICO="slug ..."` tira um candidato desta versão.

**Descrição do ticket de versão.** No preparo, a Insider sai com o crm e os serviços na
versão nova. App e Vue ficam "a definir". Linha preenchida à mão nunca é sobrescrita.

## Versão principal

1. `montar.sh principal --plano` e mostre: número, ponta da alpha, quantos commits
   desde a anterior.
2. `montar.sh principal` cria, num worktree temporário, o commit
   `chore: bump versao para <versão>` no pom sobre a ponta da alpha e a tag nele.
   Dá push na tag e no bump na alpha, juntos (ver Publicar). Se o preparo já fez o bump
   (o pom da ponta já está na versão), não há commit novo: a tag vai na ponta.
3. Em seguida, o script refaz a varredura do preparo no YouTrack com `--montagem`:
   - põe na versão os tickets que ficaram aptos durante a semana;
   - preenche a linha App do ticket de versão com a versão que está no insider (a mais
     recente da principal anterior, com hotfix).

   Vue continua "a definir": não há onde ler essa tag. Se sair `A CONFIRMAR` (saída 5),
   a tag já subiu. Resolva como no preparo e rode só o YouTrack:
   `REPO=<clone> python3 scripts/preparar.py --versao <versão> --montagem`.
   `SEM_YOUTRACK=1` pula esse passo.

   A semana pode ter trazido commits novos, e aí os Outros ajustes do preparo ficam
   desatualizados. Gere o material de novo com `--montagem` e refaça o agrupamento a partir
   do anterior. Depois rode o YouTrack com `--outros <json>`. O material da montagem vai até
   a tag.
4. Serviços: sempre, em toda principal, leve a quem acionou a lista "Candidatos a tag" do
   plano, como escolha múltipla (marcados por padrão os que têm commit e não têm AVISO).
   Todo serviço com ramo de teste aparece nela, com ou sem ticket, com os commits desde a
   última versão que o ramo dele já contém. Explique cada AVISO em uma linha: tag de versão
   fora do ramo (alguém tagueou uma feature na master) ou tag desta versão que já existe.
   Monte só os escolhidos (ver abaixo). Os que ficarem fora vão em `SEM_SERVICO="slug ..."`
   na rodada do YouTrack, para a Insider do ticket de versão não listá-los.

## Serviço que sobe junto

Quando o pedido inclui um serviço (ex.: "gera a versão no crm e no sparknectarbi"):

1. Monte primeiro a principal do CRM: o `--plano` dela dá a tag.
2. No `--plano`, mostre a mesma tag para cada serviço:
   `REPO=<clone do serviço> montar.sh servico --plano <tag-do-crm>`.
3. Depois de montar o CRM, rode `montar.sh servico <tag-do-crm>` em cada serviço. A tag
   vai direto na ponta da alpha do serviço, **sem bump**: o bump é só do CRM.
4. Hotfix de serviço: `REPO=<clone do serviço> montar.sh hotfix ...` (o modo `servico`
   recusa hotfix). Sem bump de pom; a base é a tag da principal que o serviço já tem.

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

O push na alpha dispara a build; teste unitário vermelho barra o deploy dela. Se o
deploy não rodar, diga isso em vez de supor falha da skill. Nunca mergeie PR na alpha:
a skill só empurra o bump.

## Master e insider (só se pedirem)

"Joga a versão na master e na insider": fast-forward de cada uma para o commit da tag
da **última principal** (hotfix não vai), em cada projeto pedido, pulando branch que
não existe. Se não for fast-forward, pare e leve a divergência à pessoa: nunca force
por conta própria, e antes de qualquer force salve o que sairia numa branch de backup.

## Erros comuns

- Tag ou branch já existe → alguém montou antes; `git fetch --tags` e releia.
- `refname ... is ambiguous` → há branch com nome de tag; o script usa `refs/tags/`.
- Pedido de hotfix com commit que não está na alpha → recuse e explique.
- `HTTP 400 ... isn't used for the Versão field` → busca pela versão antes de o valor
  existir; o script já evita, então releia se mudou a consulta.
- Saída 5 → há projeto ou ticket a confirmar; nada foi gravado no YouTrack.
