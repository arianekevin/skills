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
- **Design system é estrutura, não inventário.** Escala de tokens com nomes semânticos, os quatro
  estados, alvo de toque como token, nenhuma cor literal em componente. Nada de prever vinte
  componentes: seis saem errados e oito nunca são usados.
- **Adiar é decisão, com gatilho** — e adiado que a máquina poderia checar vem com o detector junto,
  para não virar silêncio.

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
