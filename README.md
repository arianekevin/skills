# skills

Skills para o [Claude Code](https://claude.com/claude-code). Cada uma é um plugin independente —
instale só o que faz sentido na máquina.

| Plugin | O que faz | Escopo |
|---|---|---|
| **alicerce** | Especifica o passo 0 de um projeto novo, audita a fundação de um já existente, ou desenha uma feature dentro dele — e, com o seu ok, levanta a obra até o molde provado | genérico |
| **ciclo** | Loop iterativo com objetivo, indicador de sucesso e orçamento de voltas | genérico |
| **modo-noturno** | Toca sozinho o trabalho combinado da sessão enquanto você dorme; decide o pequeno e guarda o grande para a manhã. De dia, guarda o que fica para a noite | genérico |
| **fechar-sessao** | Registra onde a sessão parou — feito, combinado, adiado, próximo passo — para a próxima retomar | genérico |
| **finalizar-tarefa** | Aponta o que ainda está aberto, pede o sim e aposenta o doc de pendências da tarefa | genérico |
| **bug-diagnostico** | Investigação de bug até a causa raiz, sem gerar correção | NectarCRM (Struts + AngularJS) |
| **bug-guardrail** | Cancela que não abre até causa raiz, cenários de teste e escopo existirem | NectarCRM (Struts + AngularJS) |
| **revisar-pr-bitbucket** | Revisa PRs do Bitbucket em três perguntas — resolve, quebra, abre brecha — e aplica: comentário + request changes, ou aprovação | genérico (Bitbucket + YouTrack) |
| **montar-versao** | Monta a versão principal ou um hotfix só com os commits escolhidos, põe a tag e dá push nela | NectarCRM (padrões trocáveis por variável) |

## Instalação

```
/plugin marketplace add arianekevin/skills
/plugin install alicerce@skills
/plugin install ciclo@skills
/plugin install modo-noturno@skills
/plugin install fechar-sessao@skills
/plugin install finalizar-tarefa@skills
/plugin install bug-diagnostico@skills
/plugin install bug-guardrail@skills
/plugin install revisar-pr-bitbucket@skills
/plugin install montar-versao@skills
```

## Padrões comuns

As skills compartilham um [`PADROES.md`](PADROES.md) — as regras transversais, escritas uma vez:

1. **Pergunta** — escolha para marcar quando as respostas são enumeráveis; pergunta aberta quando a
   decisão é só do dev e não há alternativas a oferecer. O critério não é "sempre dar opções", é nunca
   fazer o dev digitar o que podia ter sido uma escolha.
2. **Procedência** — identificador que não foi verificado na fonte não é afirmado, e ausência não é
   prova até se saber onde a busca aconteceu.
3. **Escrita fora do repositório** — ler é o uso previsto; comentar em ticket, dar push ou fazer
   deploy exige pedido explícito naquela sessão, e a autorização não se estende à próxima vez.
4. **Saída honesta** — toda skill tem uma saída que não é sucesso, tão legítima quanto a de sucesso,
   carregando até onde chegou, o que falta e como obter. E a régua nunca se afrouxa para caber num
   resultado.

O arquivo da raiz é a fonte única. Cada plugin é instalado isoladamente, então a cópia precisa viajar
junto: `scripts/sync-padroes.sh` replica o arquivo para dentro de todos. **Edite a raiz e rode o
script** — nunca as cópias. O mesmo vale para `compartilhado/identificar-doc.md`, que `fechar-sessao`,
`finalizar-tarefa` e `modo-noturno` usam.

---

## alicerce

A especificação que deveria existir antes da primeira linha de código — e, depois do seu ok, a obra
que a levanta. São duas fases com uma pausa no meio: especificar (só documentos) e levantar (lendo o
plano do disco, escolhendo ferramenta e versão, um ADR por escolha, verificação por comando em cada
fase, até a feature de referência provar o molde). Absorveu o antigo plugin `obra`.

```
/alicerce quero fazer um software financeiro com IA e integrações com grandes bancos
```

Antes de tudo ela quer saber **o que é o projeto**, em texto livre, nunca em múltipla escolha. É a
cancela: sem essa frase, não escreve nada. Um software financeiro com integração bancária e um site
pessoal compartilham talvez 40% da fundação, e a diferença é justamente o que importa.

**Dois caminhos, mesmo documento no fim.** O *genérico* faz quatro perguntas e a régua preenche o
resto. O *personalizado* abre rodadas curtas — mas só pergunta o que muda o conjunto de arquivos ou o
ponto de imposição de alguma regra, e que não dá pra derivar do domínio somado ao horizonte. O modo
muda quanto o dev decide, não a cara do resultado.

**Coisa nova dentro de projeto que já existe** tem modo próprio, e é o que mais previne apodrecimento.
Projeto não apodrece por uma decisão ruim — apodrece por **convenção paralela**: duas formas de tratar
erro, dois estilos de teste, nenhuma declarada, e ninguém consegue apontar o dia em que virou duas.
O documento da feature tem três listas: o que ela **herda**, as **lacunas** (cada uma com decisão
escrita — resolve local, vira convenção do projeto, ou a feature muda de desenho) e o que ela **não
inventa**. Se a lacuna vira convenção, sobe para o `CLAUDE.md` do hospedeiro; senão são duas
convenções para sempre. E se a coisa tem deploy e ciclo de vida próprios, ela não é feature: é
projeto novo no mesmo repositório, e o modo é outro.

**Projeto existente** entra em auditoria: infere o domínio e confirma, lê uma feature real ponta a
ponta, e a verificação que mais rende é descobrir, para cada regra que o projeto diz ter, quem a impõe
de fato — foi assim que apareceu uma trigger que bloqueava `UPDATE` e `DELETE` e deixava `TRUNCATE`
passar.

**O que ela garante:**

- **Requisito, nunca ferramenta.** "Formatter e linter num tool só, rodando em CI" é do plano; "Biome
  2.5" é da obra, e vira ADR lá. Plano que cita versão nasce velho — e erra, porque quem não executa
  não tem como conferir.
- **Cada regra declara quem a impõe** — banco, tipo, lint, CI, hook ou *acordo*. Regra que não declara
  é desejo, e escrever "imposta por: acordo" é honesto; esconder não é.
- **Contrato de fundação fixo:** cinco arquivos em caminhos fixos com seções de título fixo, sempre
  presentes. O horizonte calibra a profundidade, nunca a existência — num protótipo, um ADR de três
  linhas ainda é um ADR onde se espera encontrá-lo.
- **`N/A` se escreve.** Área que não se aplica aparece dizendo isso. Ausência é ambiguidade, e é ela
  que quebra o "sei o que procurar em qualquer projeto".
- **O horizonte corta a lista do domínio** — sem esse corte você recebe fundação de produto para
  código que vai ser jogado fora. Duas coisas ele nunca corta: a estrutura de teste e o ator na
  assinatura de quem grava.
- **Testes nascem antes da primeira linha de código de produto.** Não porque testar é virtuoso: o
  custo do primeiro teste é fixo e desproporcional, e código escrito sem teste não é testável. No dia
  100 você não escreve teste, você desmonta código pra conseguir escrever.
- **Toda feature sai com tour, e a âncora é a metade cara.** O tour aponta para um elemento; sem um
  identificador próprio no componente, sobra ancorar em classe de CSS ou posição, que quebram no
  primeiro refactor e quem descobre é o usuário. Pôr âncora depois é passar por todo componente de
  uma vez — mesmo formato do ator na assinatura.
- **Design system é estrutura, não inventário.** Escala de tokens com nomes semânticos, os quatro
  estados, alvo de toque como token, nenhuma cor literal em componente. Nada de prever vinte
  componentes: seis saem errados e oito nunca são usados.
- **Adiar é decisão, com gatilho** — e adiado que a máquina poderia checar vem com o detector junto,
  para não virar silêncio.

As famílias de domínio trazem a procedência marcada: 🔬 quando vieram de código e de dor relatada por
quem viveu, 📚 quando são conhecimento geral não conferido. A diferença de qualidade entre as duas é
grande, e quem lê precisa saber o quanto confiar em cada linha.

Ao terminar a especificação ela **oferece** a obra e espera — não arranca sozinha. A pausa não é cerimônia: o plano
sai com uma seção de suposições porque corrigir lendo é mais barato que ter respondido, e é o único
momento em que a correção ainda custa uma linha. Numa execução real o dev leu o resumo e trocou o
projeto de desktop-first para mobile-first na mensagem seguinte; encadeamento automático teria
levantado a fase inteira errada.

**Limites:** na especificação, não escreve código, não instala nada, não sobe serviço. Na obra, não
decide requisito, não encosta em processo, porta ou container que não subiu, não commita sem pedido e
nunca dá push.

## ciclo

Um loop iterativo que tem **objetivo**, **indicador de sucesso** e **orçamento de voltas** — e que
para quando o indicador bate, quando o orçamento acaba, ou quando o progresso estanca. Nunca quando o
modelo acha que ficou bom.

Não confundir com o `/loop` embutido do Claude Code, que reexecuta um prompt em intervalo de tempo.
Este itera rumo a uma meta.

```
/ciclo
/ciclo fazer TicketAuthTest passar, 5 voltas
/ciclo melhorar a tela de usuários para um gestor, 10 voltas, foco em UX
```

O que faltar dos três insumos, a skill pergunta — **pesquisando o repositório antes**, e entregando
opções pré-preenchidas com candidatos reais para marcar. Você não digita para o loop arrancar.

**O que ela garante:**

- **Baseline antes da volta 1.** Se o indicador já passa, para ali e diz. Sem inventar trabalho.
- **Uma hipótese escrita antes de cada mudança.** Sem hipótese, não é iteração — é tentativa.
- **Uma mudança por volta.** Se passar, dá para saber o que funcionou.
- **Assinatura de falha.** Progresso é a mensagem de erro *mudar*. Mesma assinatura duas voltas
  seguidas → para, porque acabou a hipótese.
- **Indicador composto nunca encadeia com `&&`.** Todos os membros rodam sempre, e um membro que não
  pôde rodar é registrado como `n/d`, nunca como aprovado.
- **Loop subjetivo tem muletas mecânicas.** Quando o critério é de julgamento (UX, redação,
  arquitetura), a parada vira "duas voltas sem fechar critério" e uma guarda de regressão roda a cada
  volta — sem ser confundida com o indicador.
- **A régua não se afrouxa.** Proibido marcar teste como skip, relaxar asserção ou trocar o comando
  por um mais fácil. Se o indicador estiver errado, a skill para e avisa.

**Limites:** não commita sem pedido (e nunca com `git add -A`), nunca dá `git push`, não usa
`git checkout` para desfazer em arquivo com trabalho não commitado, não edita migration já aplicada,
e não sobe a aplicação.

---

## modo-noturno

Você vai dormir no meio de um trabalho. Ela continua **o que já está combinado na sessão** — conversa,
doc de pendências, plano — sem interromper, e só para quando não sobra nada que dê para fazer sozinha.

```
modo noturno
vou dormir, toca aí
```

**A régua da decisão:** se errar, você desfaz de manhã em poucos minutos sem perder nada? Então ela
decide, pelo padrão do projeto, e anota em "decidi sozinha". Se não — destrutivo, sai da máquina,
arquitetura, regra de produto, segurança, custo, ou mudar o combinado —, ela **congela** e guarda a
pergunta com opções e recomendação.

**Congelado não para a noite:** quando é seguro, ela implementa a opção recomendada numa branch à
parte (`noturno/<data>-<slug>`, em worktree), e de manhã você só aprova ou recusa.

**Relatório nos dois lugares:** no doc de pendências da tarefa e no chat, perguntas primeiro. As
perguntas voltam como escolha para marcar quando você acordar.

**De dia, a lista da noite:** "anota pra rodar à noite" vira um item na seção `## Para a noite` do
doc de pendências — com precedente ou causa raiz conferidos e um comando de pronto medido. A noite
pega dali. (Substitui o antigo par `pauta`/`turno`; itens em `docs/melhorias/pronto/` continuam sendo
lidos.)

---

## fechar-sessao

Para a sessão que termina com trabalho pela metade. Escreve o que a próxima precisa para retomar sem
nada desta conversa: onde paramos, o que foi feito, combinado (com o porquê) e adiado (com o gatilho
de volta), o próximo passo, e o estado do ambiente — não commitado, não empurrado, branches locais.

```
vamos fechar essa sessão
```

**Um doc por tarefa**, em `docs/pendencias/<tarefa>.md`, com cabeçalho `tarefa`, `branch`, `escopo`.
Duas tarefas no mesmo repo não disputam o mesmo arquivo.

**O cuidado principal é não escrever no doc errado.** Antes de tocar num doc existente, ela decide se
ele **pertence** a esta tarefa pelos sinais: a tarefa foi nomeada, a branch bate, os arquivos mexidos
caem no escopo, o que a sessão fez era o próximo passo registrado. Dois sinais, é dele; nenhum, cria
outro; um só, ou dois candidatos, pergunta.

**Repo com doc de continuidade próprio** — o `CLAUDE.md` manda manter um, como um `CONTINUIDADE.md` —
segue a regra do repo e não cria pendências paralelas. Para não depender de interpretar o texto, o
`CLAUDE.md` pode declarar: `Doc de pendências: docs/CONTINUIDADE.md`.

**Local ou junto do projeto, escolhido uma vez por repo.** Na primeira sessão fechada num repo, ela
pergunta: o doc fica só na máquina, ou é commitado e sobe com o resto do trabalho? A resposta fica em
`git config --local pendencias.modo` e vale dali em diante; pedido explícito diferente vale só para
aquela vez. Em modo local, `docs/pendencias/` vai para o `.git/info/exclude`. O doc de continuidade
que o repo exige segue a regra do repo.

## finalizar-tarefa

O par da `fechar-sessao`, para quando a tarefa acabou de verdade.

```
vamos finalizar essa tarefa
```

Acha o doc da tarefa com o mesmo critério — mais estrito, porque o resultado é apagar — e aponta o que
ainda está aberto: próximo passo não feito, adiados, push pendente, branch local. Código da tarefa não
commitado **bloqueia**: não finaliza com trabalho solto.

Não depende de alguém dizer "finalizar": também entra quando a pessoa pergunta se acabou ("fizemos
tudo?") ou quando a sessão cumpre o último item do doc — e a `fechar-sessao` passa para ela quando o
doc fica sem nada a fazer. Se sobrou algo, só responde o que falta.

**Pede um sim explícito**, mesmo com tudo verde. Confirmado, remove o doc. Se o doc era commitado,
pergunta também se commita a remoção — é o commit que guarda os adiados no `git log`, e a skill diz
isso. Doc só local é apagado sem commit, e os adiados vão na resposta final. Doc de continuidade do
repo nunca é apagado: o bloco da tarefa muda para a seção de fechados dele.

## bug-diagnostico

Assistente de investigação: ajuda a entender **por que** o bug acontece, e não corrige. A primeira
ação diante de uma stack trace é buscar a assinatura técnica no histórico — exceção + entidade +
método, não nome de tela — antes de qualquer hipótese.

Existe porque a causa principal de correção mal feita é pular o diagnóstico. Quando o dev cola um
erro e pede "resolve isso", a tendência é tratar o sintoma.

**Procedência.** Nome de tabela, coluna, entidade ou tag de versão que não foi verificado na fonte não
é citado — "existe uma tabela de X, cujo nome não localizei" é frase honesta; nome inventado com cara
de certeza faz o dev perder a viagem. E ausência não é prova: o CRM é multi-tenant com Flyway manual
por tenant, então "essa tabela não existe" pode ser base errada.

**Duas saídas, não uma.** `DIAGNOSTICADO` quando a causa raiz está de pé, e `INCONCLUSIVO` quando
falta evidência que a IA não consegue obter — com o motivo, o dado que falta nomeado, e a query pronta
pra rodar. Sem essa segunda saída, a única forma de terminar é fechar como diagnosticado, e aí
aparecem causas raiz plausíveis e erradas. Sem acesso à base, o fluxo degrada pro processo que o dev
já faz hoje: a IA escreve a query, ele roda e cola.

**Versão como controle.** Diagnostica sempre contra a mais recente; se nada aparecer nela, confere se
a anterior carregava o bug — é o que separa "já corrigido na release X" de "não consegui encontrar".

**Perguntas com alternativas para marcar**, com candidatos reais achados no código, nunca campo
aberto. E lê o YouTrack, mas nunca escreve nele sem pedido.

---

## bug-guardrail

Controlador de processo para corrigir bug com IA. Três cancelas antes de qualquer linha de código:
causa raiz em uma frase, cenários de teste (principal + edge case), e escopo com limites explícitos.
Só então planeja, implementa, apresenta para revisão, gera testes e documenta para o QA.

Não gera código antes das cancelas — nem sob pressa. Não faz commit. Se o dev não tem a causa raiz,
redireciona para a `bug-diagnostico`.

---

## revisar-pr-bitbucket

Revisão de PR com um objetivo só: não deixar passar coisa absurda. Três perguntas, nada além —
**resolve** o ticket do YouTrack em todos os caminhos que levam a ele, **quebra** algo dentro ou fora
do escopo (banco incluído: listagem sem paginação, transação aberta enquanto chama serviço externo,
migration com lock em tabela grande) e **abre brecha** de segurança. Estilo e "melhor forma de fazer"
ficam de fora.

Aceita link ou filtro do YouTrack, link da lista de PRs do Bitbucket, ids de ticket, PR ou branch. Acha o PR de cada ticket, separa o que
não tem PR (commit direto), branch empilhada e branch agregadora, e divide em subagentes quando o
volume pede. Achado grave é conferido no código antes de sair, e antes de um ❌ ou ⚠️ ela lê os
comentários do PR e procura outro PR aberto que cubra o problema — se cobre, o achado vira
"sobe junto com #X". Também cobra o dado já quebrado no banco, não só o que vier depois do deploy.

**Aplica no Bitbucket.** PR com ajuste recebe um comentário curto por achado — problema, evidência com
`arquivo:linha`, sugestão que não quebra a correção — e **request changes**; PR ok é **aprovado**. Nunca
faz merge nem decline. Com "só avalia", para antes e mostra o que comentaria. Revisão que não fechou
sai **INCONCLUSIVO** e o PR fica sem ação.

**Contexto do projeto fora do repositório.** O que faz a revisão achar o que importa — portas
paralelas, o que cada gate de permissão checa, regras de domínio que não são achado — fica em
`~/.claude/revisar-pr-bitbucket/contexto/<repo>.md`, na máquina do dev. Não é publicado e não some
quando o plugin atualiza.

**Precisa de:** `BITBUCKET_EMAIL` + `BITBUCKET_API_TOKEN` (API token do Atlassian com
`read:pullrequest:bitbucket` e `write:pullrequest:bitbucket`), `YOUTRACK_API_TOKEN`, e o clone do repo.

---

## montar-versao

Versão e hotfix sem levar a alpha inteira. Tudo entra na alpha primeiro; daí:

- **Versão principal** `vYY.T.NNN` (T = trimestre, NNN recomeça a cada trimestre): commit de bump
  do pom em cima da ponta da alpha, com a tag. Dá push na tag e no bump na alpha, juntos (atômico).
- **Hotfix** `vYY.T.NNN.H`: parte da versão ou hotfix mais recente (ou de uma principal escolhida),
  cria `hotfix/<versão>` num worktree e aplica por cherry-pick só os commits pedidos, na ordem em que
  entraram na alpha. Não mexe no pom. Dá push na branch e na tag.

Os commits vêm de ticket, PR ou SHA — inclusive as correções feitas no PR depois da revisão. Commit
que não está na alpha é recusado; o que a base já tem (mesmo SHA ou mesmo patch) é pulado. Conflito
desfaz tudo e aponta os commits da alpha que mexem nos mesmos arquivos, candidatos a dependência.
`--plano` mostra o que faria sem criar nada.

- **Serviço que sobe junto** (`montar.sh servico <tag-do-crm>`): a tag é sempre a do CRM, mesmo
  pulando números na sequência do serviço. Vai na ponta da alpha do serviço, sem bump.

**Precisa de:** clone com `origin` e permissão de push de tag. Padrões do NectarCRM trocáveis por
`ALPHA`, `POM` e `ARTIFACT`.

---

## Licença

MIT
