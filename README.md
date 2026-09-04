# skills

Skills para o [Claude Code](https://claude.com/claude-code). Cada uma é um plugin independente —
instale só o que faz sentido na máquina.

| Plugin | O que faz | Escopo |
|---|---|---|
| **alicerce** | Planeja o passo 0 de um projeto novo, ou audita a fundação de um já existente | genérico |
| **ciclo** | Loop iterativo com objetivo, indicador de sucesso e orçamento de voltas | genérico |
| **bug-diagnostico** | Investigação de bug até a causa raiz, sem gerar correção | NectarCRM (Struts + AngularJS) |
| **bug-guardrail** | Cancela que não abre até causa raiz, cenários de teste e escopo existirem | NectarCRM (Struts + AngularJS) |

## Instalação

```
/plugin marketplace add arianekevin/skills
/plugin install alicerce@skills
/plugin install ciclo@skills
/plugin install bug-diagnostico@skills
/plugin install bug-guardrail@skills
```

## Padrões comuns

As quatro skills compartilham um [`PADROES.md`](PADROES.md) — as regras transversais, escritas uma vez:

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
junto: `scripts/sync-padroes.sh` replica o arquivo para dentro dos quatro. **Edite a raiz e rode o
script** — nunca as cópias.

---

## alicerce

O documento que deveria existir antes da primeira linha de código — e que quase nunca existe.
A skill detecta sozinha em qual dos dois casos você está:

```
/alicerce
```

Antes de qualquer coisa, ela quer saber **o que é o projeto** — em texto livre, nunca em múltipla
escolha. É a cancela: sem essa frase, não escreve plano. Um software financeiro com integração
bancária e um site pessoal compartilham talvez 40% da fundação, e a diferença é justamente o que
importa.

```
/alicerce quero fazer um software financeiro com IA e integrações com grandes bancos
```

Dessa frase ela deriva as **exigências do domínio** — decimal em vez de float, trilha de auditoria
imutável, idempotência em toda operação que move dinheiro, camada de tradução por banco, avaliação
rotulada para a parte de IA. Nada disso está numa lista de boas práticas genérica, e tudo isso encosta
no modelo de dados, que é o retrofit mais caro que existe.

**Projeto novo.** Com o domínio na mão, faz no máximo quatro perguntas de calibragem, em uma rodada
só, com opções para marcar — e não pergunta o que o domínio já respondeu. A que mais importa é o
**horizonte**: protótipo descartável, produto interno ou produção. Protótipo com fundação de produção
é desperdício; produto com fundação de protótipo é dívida. Sai um `docs/PLANO-FUNDACAO.md` em três
ondas, cabendo em 1–2 dias.

**Projeto existente.** Infere o domínio do código e confirma em uma linha, lê o repositório e uma
feature real ponta a ponta, marca a régua de oito áreas com ✅ ⚠️ ❌ —, e escreve um
`docs/DIAGNOSTICO-FUNDACAO.md` com plano priorizado. Sistema financeiro guardando dinheiro em float é
o tipo de achado que só aparece porque ela olhou o domínio primeiro. O achado mais útil
raramente é o ❌: é o ⚠️ — o CI que só roda lint, o README cujos comandos não rodam mais, o token de
design com cor hardcoded em metade dos componentes. Por isso a régua manda **verificar na prática**,
nunca pela presença do arquivo.

**A régua (`references/checklist-fundacao.md`)** é o piso comum: produto e não-escopo · decisões
registradas (ADR) · repo, tooling e CI · convenções e estrutura · design system · documentação viva ·
dados e configuração · operação e segurança. Cada item traz prioridade e o sinal de detecção no repo.
Sobre ela se somam as exigências de `references/dominio.md` — famílias de domínio (regulado,
integração pesada, IA no núcleo, consumidor, B2B multi-tenant, dados) e o que a combinação de duas
cria que nenhuma delas pediria sozinha.

**O que ela garante:**

- **A stack é justificada pelo domínio, não por gosto.** "Decimal nativo porque lida com dinheiro",
  não "porque é uma linguagem moderna".
- **A feature de referência exercita o domínio.** Num financeiro com integração bancária, "importar um
  extrato e conciliar uma linha" vale dez vezes mais que "cadastro de usuário" — prova a camada de
  tradução, a idempotência, o decimal e a auditoria de uma vez.
- **A ordem segue custo de reversão, não estética.** Migration versionada, forma de erro, tokens e
  modelo de permissão são baratos no dia 1 e caros no dia 90 — por isso vêm antes.
- **Design system em camadas, nessa ordem.** Tokens → primitivos → padrões. Componente bonito sem
  escala de espaçamento por trás é sinal de que começaram pelo fim.
- **"Adiado de propósito" é seção obrigatória**, com o gatilho de revisita. Microserviços, i18n,
  cache, feature flags. Transforma "esquecemos" em "decidimos".
- **"Adotar daqui pra frente".** Na auditoria, nomeia a lacuna que não vale corrigir retroativamente —
  projeto de três anos não reescreve histórico de migration, adota o padrão para código novo.
- **Adota a convenção da casa.** Lê o `CLAUDE.md` e projetos vizinhos antes de propor qualquer padrão.
  Consistência entre projetos vale mais que a escolha ótima em um.
- **Diagnóstico, não julgamento.** Relata a consequência da lacuna, não adjetivo. Projeto em produção
  sem ADR não é projeto ruim — é projeto que priorizou entrega.

**Limites:** não implementa nada. Escreve o plano e pergunta se você quer executar a Onda 1 — a
execução é um pedido seu, item por item. Os únicos arquivos que cria são o documento e o template
de ADR.

---

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

## Licença

MIT
