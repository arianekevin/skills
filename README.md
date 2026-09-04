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

---

## alicerce

O documento que deveria existir antes da primeira linha de código — e que quase nunca existe.
A skill detecta sozinha em qual dos dois casos você está:

```
/alicerce
```

**Projeto novo.** Faz no máximo cinco perguntas, em uma rodada só, com opções para marcar.
A que mais importa é o **horizonte**: protótipo descartável, produto interno ou produção — é ela que
calibra o que é essencial. Protótipo com fundação de produção é desperdício; produto com fundação de
protótipo é dívida. Sai um `docs/PLANO-FUNDACAO.md` dividido em três ondas, cabendo em 1–2 dias.

**Projeto existente.** Lê o repositório e uma feature real ponta a ponta, marca a régua de oito áreas
com ✅ ⚠️ ❌ —, e escreve um `docs/DIAGNOSTICO-FUNDACAO.md` com plano priorizado. O achado mais útil
raramente é o ❌: é o ⚠️ — o CI que só roda lint, o README cujos comandos não rodam mais, o token de
design com cor hardcoded em metade dos componentes. Por isso a régua manda **verificar na prática**,
nunca pela presença do arquivo.

**A régua (`references/checklist-fundacao.md`):** produto e não-escopo · decisões registradas (ADR) ·
repo, tooling e CI · convenções e estrutura · design system · documentação viva · dados e
configuração · operação e segurança. Cada item traz prioridade e o sinal de detecção no repo.

**O que ela garante:**

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
