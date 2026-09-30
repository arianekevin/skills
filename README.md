# skills

Skills para o [Claude Code](https://claude.com/claude-code). Cada uma é um plugin independente —
instale só o que faz sentido na máquina.

| Plugin | O que faz | Escopo |
|---|---|---|
| **alicerce** | Especifica o passo 0 de um projeto novo, audita a fundação de um já existente, ou desenha uma feature dentro dele | genérico |
| **obra** | Levanta a fundação a partir do plano que a alicerce escreveu | genérico |
| **ciclo** | Loop iterativo com objetivo, indicador de sucesso e orçamento de voltas | genérico |
| **pauta** | Captura a melhoria pequena do dia — ou o bug já diagnosticado — como item que um agente sem supervisão consegue executar | genérico |
| **turno** | Executa os itens prontos de madrugada, sozinho, e deixa o relatório da manhã | genérico |
| **fechar-sessao** | Registra onde a sessão parou — feito, combinado, adiado, próximo passo — para a próxima retomar | genérico |
| **finalizar-tarefa** | Aponta o que ainda está aberto, pede o sim e aposenta o doc de pendências da tarefa | genérico |
| **bug-diagnostico** | Investigação de bug até a causa raiz, sem gerar correção | NectarCRM (Struts + AngularJS) |
| **bug-guardrail** | Cancela que não abre até causa raiz, cenários de teste e escopo existirem | NectarCRM (Struts + AngularJS) |
| **revisar-pr-bitbucket** | Revisa PRs do Bitbucket em três perguntas — resolve, quebra, abre brecha — e aplica: comentário + request changes, ou aprovação | genérico (Bitbucket + YouTrack) |

## Instalação

```
/plugin marketplace add arianekevin/skills
/plugin install alicerce@skills
/plugin install obra@skills
/plugin install ciclo@skills
/plugin install pauta@skills
/plugin install turno@skills
/plugin install fechar-sessao@skills
/plugin install finalizar-tarefa@skills
/plugin install bug-diagnostico@skills
/plugin install bug-guardrail@skills
/plugin install revisar-pr-bitbucket@skills
```

## Padrões comuns

As dez skills compartilham um [`PADROES.md`](PADROES.md) — as regras transversais, escritas uma vez:

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
script** — nunca as cópias. O mesmo vale para `compartilhado/identificar-doc.md`, que só o par
`fechar-sessao`/`finalizar-tarefa` usa.

---

## alicerce

A especificação que deveria existir antes da primeira linha de código. **Ela não implementa nada** —
escreve documentos. Quem levanta o projeto é a `obra`, lendo o que a alicerce especificou.

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

Ao terminar ela **oferece** a `obra` e espera — não arranca sozinha. A pausa não é cerimônia: o plano
sai com uma seção de suposições porque corrigir lendo é mais barato que ter respondido, e é o único
momento em que a correção ainda custa uma linha. Numa execução real o dev leu o resumo e trocou o
projeto de desktop-first para mobile-first na mensagem seguinte; encadeamento automático teria
levantado a fase inteira errada.

**Limites:** não escreve código, não instala nada, não sobe serviço, não toca em porta ou container.
Todos os problemas que uma auditoria encontrou na versão anterior vinham da execução; ela não executa
mais.

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

## pauta

A melhoria que você vê de passagem — "um dia eu troco todo esse texto explicativo por tooltip" — vira
um arquivo em `docs/melhorias/`, escrito para ser executado **por um agente que não pode perguntar
nada a ninguém**.

```
/pauta trocar os textos explicativos de Configurações por tooltips
/pauta o filtro de período perde o último dia, é o fuso em useDateRange.ts:37
/pauta                      # revisa o que está acumulado
```

**Os quatro testes.** Um item só vai para `pronto/` se passar nos quatro; falhou em um, vai para
`bloqueado/` com o que falta nomeado:

1. **Decisão** — nenhuma que seja sua ou do negócio. Se duas pessoas competentes pudessem discordar
   do resultado, é decisão.
2. **Precedente** — o padrão-alvo **já existe aplicado** em algum lugar, com caminho e linha. Este é
   o teste que ninguém lembra e o que mais estraga noite: "melhorar para tooltips estilizadas" só é
   autônomo depois que existe uma tooltip estilizada para copiar. Senão o agente desenha sozinho, de
   madrugada, e você acorda com trinta arquivos num padrão que você não escolheu.
3. **Critério** — um comando prova o pronto, normalmente uma contagem que vai a zero, medida **na
   hora da captura**. Comando que não roda hoje na sua máquina não roda de madrugada.
4. **Escopo** — o que pode e o que não pode tocar, mais o tamanho. Item que não cabe em cinco voltas
   de `/ciclo` não é um item, são vários.

**A pasta é o estado** (`pronto/`, `rascunho/`, `bloqueado/`, `feito/`, `relatorio/`) — estado em dois
lugares diverge no primeiro dia. E ela é rápida de propósito: investiga sozinha com `grep`, mostra o
item pronto e sai do caminho, porque você está no meio de outra coisa.

**Bug entra também**, com dois dos quatro testes trocados: no lugar do precedente, a **causa raiz em
uma frase com caminho e linha**, conferida na fonte — bug com causa suposta vira correção de sintoma,
e correção de sintoma passa no teste. No lugar da contagem, a **reprodução**: os cenários escritos e
a assinatura da falha atual colada, para o turno escrever o teste na volta 1 e provar que ele falha
pela razão certa antes de corrigir.

A triagem é o **momento**, não o assunto: quer entender o bug agora é `bug-diagnostico`, quer
corrigir agora é `bug-guardrail`, é uma chateação pequena que já entendeu e não quer parar o dia para
consertar é pauta. E há o que nunca entra, por reversibilidade e não por dificuldade: bug que mexe em
dado, em cobrança, em permissão, em autenticação, que muda contrato de API, ou que não tem reprodução
determinística.

**Limites:** não edita uma linha de código, não commita, e não executa nem o item que acabou de
escrever.

---

## turno

O trabalho da noite. Pega os itens de `docs/melhorias/pronto/`, roda um por um numa branch só da
noite, um commit por item, e deixa o relatório para a manhã.

```
/turno
/turno roda os dois menores
```

**A inversão:** todas as outras skills perguntam com opções para marcar. Esta, depois do orçamento
aprovado, **não pergunta nada** — não há ninguém para marcar. Dúvida vira item parado e registrado,
nunca uma escolha tomada no seu lugar. Descobriu no meio que há duas formas defensáveis? O item
falhou no teste 1 da pauta: reverte, vai para `bloqueado/` com a decisão escrita, e segue.

**As cancelas, antes de qualquer coisa:** é repositório git, árvore de trabalho limpa (mexer no seu
trabalho não commitado sem você por perto é pior que não rodar — e nada de `stash`), existe item
pronto, e **a guarda de regressão está verde agora**. Se já estava vermelha, a noite não é dela: você
acordaria sem saber se foi você ou ela.

**O ritual de cada item**, sem atalho: conferência da âncora na fonte (o precedente, ou a causa raiz
do bug) → baseline do critério (se já passa, item fechado sem commit) → execução pela `ciclo`, que
recebe os três insumos já prontos do arquivo → revisão do próprio diff pela `bug-reviewer`, o único
olho que esse código terá até de manhã → guarda de regressão inteira → conferência de escopo por
`git status --porcelain` → commit por pathspec explícito, ou reversão. Escopo estourado é item falho
mesmo com o critério verde.

**Em item de bug há um portão a mais**, antes de qualquer correção: a volta 1 escreve o teste dos
cenários e ele tem que falhar **com a assinatura que está no item**. Passou de cara, ou falhou por
outro motivo, o item para — e as duas assinaturas, a esperada e a obtida, vão para o relatório. É a
informação mais útil que a noite pode produzir sobre aquele bug. Sem esse portão, o teste escrito
depois do fix passa por construção e não prova nada.

**Para a noite inteira** com três itens falhos seguidos, guarda vermelha que não volta ao verde,
orçamento esgotado, ou cancela que reaparece. Volta para a sua branch antes de terminar — encontrar
de manhã uma branch que você não reconhece é o primeiro susto que ela poupa.

**O relatório** abre com o veredito em números, põe o que falhou antes do que deu certo, cola a saída
em vez de parafrasear, lista o que ela viu e **não** fez (a noite enxerga o que ninguém enxerga de
dia), e fecha com os comandos de desfazer. Nada é publicado: sem `push`, sem PR.

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

**Não commita por padrão.** Escreve e pergunta: commitar ou manter local. Código não commitado nunca
entra junto; vai para o "estado do ambiente".

## finalizar-tarefa

O par da `fechar-sessao`, para quando a tarefa acabou de verdade.

```
vamos finalizar essa tarefa
```

Acha o doc da tarefa com o mesmo critério — mais estrito, porque o resultado é apagar — e aponta o que
ainda está aberto: próximo passo não feito, adiados, push pendente, branch local. Código da tarefa não
commitado **bloqueia**: não finaliza com trabalho solto.

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

Aceita link ou filtro do YouTrack, ids de ticket, PR ou branch. Acha o PR de cada ticket, separa o que
não tem PR (commit direto), branch empilhada e branch agregadora, e divide em subagentes quando o
volume pede. Achado grave é conferido no código antes de sair.

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

## Licença

MIT
