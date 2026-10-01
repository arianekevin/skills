---
name: revisar-pr-bitbucket
description: "Avalia PRs do Bitbucket para barrar o absurdo antes do merge: se corrigem o ticket do YouTrack, se quebram algo dentro ou fora do escopo (inclusive travar banco) e se abrem brecha de segurança — e aplica o resultado no Bitbucket: PR com ajuste recebe comentário + request changes, PR ok é aprovado (sem merge). Use quando o dev invocar /revisar-pr-bitbucket, mandar um link ou filtro do YouTrack, um link da lista de PRs do Bitbucket, uma lista de tickets, um número ou link de PR do Bitbucket ou uma branch, e pedir para 'avaliar os PRs', 'olhar os PRs desses tickets', 'revisar a versão', 'ver se pode mergear'. NÃO avalia estilo nem 'melhor forma de fazer'."
---

# Revisar PR no Bitbucket

Objetivo: não deixar passar coisa absurda. Três perguntas por PR, nada além:

1. **Resolve?** O problema do ticket (e das ampliações nos comentários) foi corrigido em todos os caminhos que levam a ele?
2. **Quebra algo?** Dentro ou fora do escopo: outros callers, telas antigas, integrações, jobs, contrato de API, dado legado — e **banco**: listagem sem paginação, carregar a conta inteira em memória, N+1 em importação, filtro sem índice, lock/migration em tabela grande.
3. **Abre brecha?** Bypass de permissão, IDOR, tenant cruzado, SQL/HQL injection, dado exposto, validação só no front, endpoint público.

Fora do escopo: nome, estilo, refatoração, "dava para fazer melhor". Só entra se causar um dos três acima.

### Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir. Dois têm peso aqui:

**Procedência.** Achado só com `arquivo:linha` e cenário concreto, lidos no código. Dúvida vira "(a confirmar: o que faltou olhar)".

**Escrita fora do repositório.** Invocar esta skill sobre um PR é o pedido para comentar, pedir mudança ou aprovar **aquele** PR. Não se estende a outro PR, nem a ticket do YouTrack, nem a merge — merge e decline nunca.

### Contexto do projeto

Se existir `~/.claude/revisar-pr-bitbucket/contexto/<slug-do-repo>.md`, leia antes de revisar: diz onde os bugs se escondem naquele sistema e que regras de domínio **não** são achado. Formato e motivo em `references/contexto-de-projeto.md`. Sem arquivo, siga só o método abaixo.

## Pré-requisitos

- Credencial do Bitbucket no ambiente, uma das duas: `BITBUCKET_ACCESS_TOKEN` (access token do repositório; age como um usuário-bot com o nome do token e, se definido, é o que vale) ou `BITBUCKET_EMAIL` + `BITBUCKET_API_TOKEN` (API token do Atlassian; age como o dono). Se o shell da sessão não os carregou, `source ~/.zshrc` (ou o arquivo onde o dev os pôs) no mesmo comando.
- `YOUTRACK_API_TOKEN` (e `YOUTRACK_URL`, quando a entrada não é um link do YouTrack) para ler tickets. Se o ambiente não tiver `YOUTRACK_URL`, use o que o arquivo de contexto do projeto indicar.
- Clone local do repo do PR, para ler o diff. Os scripts descobrem `workspace/slug` pelo `git remote` do diretório atual; fora dele, `--repo workspace/slug`.

Sem token do Bitbucket: peça para o dev criar em https://id.atlassian.com/manage-profile/security/api-tokens → "Create API token with scopes" → app Bitbucket → `read:pullrequest:bitbucket` + `write:pullrequest:bitbucket` (nada de admin, delete ou write:repository), validade curta, e pôr as duas variáveis no arquivo de perfil do shell pelo editor — nunca colar o token no chat. Não procure credencial em keychain ou arquivos.

## Passo 1 — Montar a lista

Entrada: link/filtro do YouTrack, link da lista de PRs do Bitbucket, ids de ticket, número/link de PR ou branch.

```bash
S=<diretório desta skill>/scripts
OUT=<scratchpad>/revisar-pr-bitbucket
python3 $S/youtrack.py --url '<link do youtrack>' --out $OUT/issues   # ou --query / --ids
cd <clone do repo> && git fetch origin --prune -q
python3 $S/bitbucket.py list --dest <branch> [--author <nome>]   # PRs abertos (entrada = lista do Bitbucket)
python3 $S/bitbucket.py find <branch> ...      # PR aberto de cada branch
python3 $S/bitbucket.py info <pr> ...          # estado, origem -> destino, autor, REVISAR/PULAR
python3 $S/bitbucket.py describe <pr>          # descrição do PR
python3 $S/bitbucket.py comments <pr>          # comentários do PR (o dev pode já ter respondido ali)
```

Link da lista de PRs do Bitbucket: leia destino (`at=`) e autor do link e use `list`. O ticket de cada PR sai do nome da branch, do título ou da descrição.

**Lista só tem PR aberto, fora de draft e sem revisão ativa.** Quando a entrada é uma lista (filtro/link do YouTrack, lista de PRs do Bitbucket, vários tickets ou branches), a lista pode estar errada — filtro velho, link copiado da aba de mergeados. `list`, `find` e `info` marcam cada PR como `REVISAR` ou `PULAR: <motivo>` (MERGED, DECLINED, `draft`, `changes_requested (X)`, `approved (Y)`); só os `REVISAR` seguem. Revisão anterior ao último commit do PR, ou a um comentário de quem não é o revisor, não conta como ativa: o PR volta como `REVISAR: commit novo depois de <revisão>` (ou `comentário novo`) e é re-revisado (ver "Re-revisão" no Passo 2). Não monte a lista com chamada própria à API: com `q`, o parâmetro `state` solto é ignorado e PR mergeado volta como aberto. PR pulado não é revisado, comentado nem remarcado — e `comment`/`request-changes`/`approve` recusam esse PR mesmo que ele escape. Vai para o fim do relatório como "pulado (mergeado / draft / request changes de X / aprovado por Y)"; se a maioria da lista cair fora, diga que a lista parece errada. PR pedido sozinho pelo número, link ou branch é revisado mesmo fechado ou já revisado — o pedido é explícito: avise o estado dele e use `--isolado` na escrita.

Para cada ticket, ache o código:
- Branch do PR → `git diff $(git merge-base origin/<destino> origin/<branch>) origin/<branch>`, com o destino real do PR.
- Sem branch: o commit citado no ticket (`git log --all --grep=<ID>`), neste e nos outros repos do projeto. Commit já dentro da branch de destino = **sem PR**: revise com `git show` e avise.
- Branches empilhadas (`git merge-base --is-ancestor origin/A origin/B`): revise cada uma pelo incremento (`git diff origin/A origin/B`) e registre a ordem de merge.
- PR de branch agregadora (`qa`, `release`…): tire os tickets das mensagens de commit, baixe com `youtrack.py --ids` e revise commit a commit, conferindo o estado final na branch. Um comentário só no PR, com uma linha por ticket.
- PR sem ticket: a pergunta 1 vira "faz o que a descrição do PR promete?".

Diga em uma linha quantos tickets, quantos com PR, quantos pulados (fechados, em draft ou com revisão ativa), quais sem PR ou empilhados.

## Passo 2 — Revisar

Nunca faça checkout, commit ou push: só `git show`, `git diff`, `git grep`, `git show origin/<branch>:<arquivo>`.

Poucos PRs pequenos (até ~4): revise direto. Mais que isso, ou um PR grande: subagentes em paralelo, 3–5 tickets (ou um recorte do PR) por agente, agrupados por tema — permissão, validação de API, webhook/integração, job/migration —, empilhadas no mesmo agente. Cada agente recebe o bloco "Como revisar", o arquivo de contexto do projeto (se houver), os ids/branches/commits, o caminho dos JSON dos tickets e o foco do grupo ("gate de permissão: ache outras portas para a mesma ação").

### Como revisar (vale para você e para os agentes)
- Leia o ticket inteiro (descrição, comentários de QA — "ampliação" — e o "como testar" do dev), a descrição e os comentários do PR.
- O fix bate com o erro real? Confira a causa declarada contra a stack, a mensagem e o schema (constraint, tipo de id, unique). Trocar `error` por `warn`, ou um catch que engole a exceção, esconde o sintoma, não corrige.
- O bug deixou dado quebrado no banco? Então o fix precisa corrigir o que já está gravado (script ou migration), não só o que vier depois do deploy — senão o cliente do ticket continua com o erro. E quem lê esse dado (desfazer, histórico, relatório) precisa continuar funcionando depois da correção.
- Siga o caminho de chamada do que mudou: quem mais chama? Há outra porta (outra versão da API, tela antiga, ação em massa, importação, integração, webhook, job) que chega na mesma gravação e continua com o bug ou passa a falhar?
- Mudança de status HTTP ou de campo de resposta: quem consome (front, SDK, mobile, API pública)?
- Catch que só loga + nova validação = dado perdido em silêncio (lead, importação, webhook).
- Nova consulta: tem paginação/limite? Roda por linha? Filtra tenant? Concatena valor da request? Segura transação aberta enquanto chama serviço externo?
- Campo novo mapeado no ORM entra no UPDATE de linha inteira dos fluxos antigos? (Um fluxo que regrava a entidade inteira desfaz o que outro gravou por SQL.)
- "Quebra" é contra o que o cliente usa hoje (produção, regra de produto), não contra um estado intermediário da branch de destino criado por outro PR ainda não liberado. Antes de chamar de regressão, confira se aquilo já funcionava (`git log` do arquivo).

Achados mais graves (❌ e brecha de segurança): confira você no código antes de reportar, mesmo quando vieram de um agente.

### Re-revisão (`REVISAR: commit novo` / `comentário novo depois de <revisão>`)
O PR já foi revisado e depois recebeu commit, comentário de quem não é o revisor, ou os dois. Parta da revisão anterior (`comments`), não do zero:
- **Commit novo:** confira no código atual se cada achado anterior foi resolvido e revise o que os commits trouxeram com o mesmo método. Rebase ou merge do destino na branch muda o commit sem mudar o PR: compare o diff do PR antes de tratar como correção.
- **Comentário novo:** é o dev respondendo, muitas vezes contestando um achado. Leia o argumento e confira no código. Se ele tem razão, o achado cai. Se o achado se mantém, responda em cima do argumento dele — o que ele disse, por que não fecha, com `arquivo:linha` —, sem colar o achado de novo.

O comentário da re-revisão traz só o que mudou; o que já está escrito no PR não é repetido:
- achado resolvido ou derrubado: não aparece;
- achado novo: formato normal do Passo 4;
- resposta a contestação: como acima;
- nada mudou nos achados (rebase, commit que não toca neles): uma linha — "Revisado de novo em `<hash curto>`: os achados acima continuam; aguardando correção."

Veredito pelo estado atual do PR, aplicado como em qualquer outro: sem achado de pé, aprova (substitui o request changes anterior do mesmo usuário); com achado de pé, comenta e marca request changes. Re-revisão que mantém achado **sempre** deixa comentário, nem que seja a linha acima: é ele que registra que o commit ou o comentário novo já foi visto — sem ele o PR volta como `REVISAR` na próxima listagem.

### Antes de fechar ❌ ou ⚠️: procure a explicação que falta
O que parece faltar pode já estar respondido ou estar em outro PR. Só para PR com ❌/⚠️ (não em todo PR):
1. Leia os comentários do PR (`comments`), se ainda não leu.
2. Rode `python3 $S/bitbucket.py related <pr> --grep <exceção ou termo-chave>`: devolve só os PRs abertos para o mesmo destino que tocam os mesmos arquivos ou citam o termo.
3. Achou candidato: leia o diff dele e teste o cenário do achado com os dois PRs somados.
   - **Fecha:** o achado vira dependência — "Sobe junto com #X; merge do #X primeiro." —, e o veredito cai (❌→⚠️, ou ✅ com a nota de dependência).
   - **Fecha em parte ou não fecha:** mantém o achado e diz o que falta mesmo com os dois.
   - **Não deu para confirmar no código:** só aí "confirmar se #X cobre isto". É a exceção.

## Passo 3 — Entregar no chat

Ordem: ❌ primeiro, depois ⚠️ agrupados (brecha que sobra, quebra, parcial), depois os ✅. Uma a três linhas por ticket. No fim: PRs pulados (mergeado, recusado, ou revisão ativa e quem marcou), tickets sem PR ou com commit direto, empilhadas (ordem de merge), conflitos esperados e dependências entre PRs (uma linha cada). Achado anterior ao PR, fora do escopo, só entra se for brecha de segurança ou quebra grave; o resto não é reportado.

Veredito:
- ❌ não resolve, ou brecha/quebra séria
- ⚠️ resolve com ressalva: parcial, porta paralela aberta, quebra menor, decisão de produto
- ✅ ok (ressalva mínima não conta)
- **INCONCLUSIVO**: a revisão não fechou — diff inacessível, agente que falhou, trecho crítico não lido. Diga até onde chegou, o que falta e como obter. PR inconclusivo não é aprovado nem recebe request changes.

## Passo 4 — Comentários

Escreva `$OUT/comentarios.md`, uma seção por PR com ❌/⚠️, cabeçalho `## <ticket ou título curto> (#<pr>)`. PR ✅ não recebe comentário.

Cada achado:
```
❌|⚠️ **<problema em uma frase>.** <evidência: arquivo:linha e cenário concreto>. <sugestão de correção que não quebra a própria correção nem outro fluxo>.
```
Curto. Sem elogio, sem resumo do PR, sem estilo. Decisão de produto → "Para produto confirmar: …". Contradição no "como testar" → ℹ️ uma linha.

## Passo 5 — Aplicar no Bitbucket

Padrão, sem perguntar:
- **Precisa de ajuste** (❌ ou ⚠️) → posta o comentário e marca **Request changes**.
- **Não precisa** (✅) → marca **Aprovado**. Só aprova: nunca merge, nunca decline.

Se o dev disser "não comenta", "só avalia" ou "não aplica", pare no Passo 4: mostre o que comentaria, sem tocar no Bitbucket. Achado que ele derrubar na conversa sai do arquivo, e o PR é reclassificado antes de aplicar.

```bash
python3 $S/bitbucket.py comment $OUT/comentarios.md       # PRs com ajuste
python3 $S/bitbucket.py request-changes <prs com ajuste>
python3 $S/bitbucket.py approve <prs ✅>
```
Releia o arquivo antes de postar (o dev pode ter editado). Confira a saída de cada chamada; ERRO em algum PR é dito com o número do PR que ficou sem ação.

Entrega final: tabela ticket | PR (link) | veredito | ação aplicada (comentado + request changes / aprovado / nada / pulado: fechado ou revisão ativa).
