# O domínio muda o plano

A régua genérica é o **piso**. O domínio decide a stack e acrescenta exigências que a
régua não tem — e essas exigências costumam ser as mais caras de retrofitar, porque
mexem no modelo de dados, não na configuração.

Regra de uso: da frase do projeto, identifique **uma família principal** (às vezes duas)
e puxe de **2 a 5 exigências**, não vinte. Fundação inchada não é fundação — é backlog.

Cada exigência derivada entra no plano com a mesma forma dos outros itens: o que fazer,
por que agora, pronto quando. E precisa dizer **por que este projeto** precisa dela.

---

## Como derivar

Três perguntas sobre a frase do projeto:

1. **O que acontece se der errado?** Dinheiro perdido, dado vazado, e-mail não enviado,
   página feia. A resposta define quanto de rastreabilidade e teste é P0.
2. **Quem manda além do usuário?** Regulador, banco parceiro, auditoria, loja de app,
   ninguém. Cada um traz requisito não-negociável que não se descobre no meio.
3. **De onde vem o dado, e ele é meu?** Dado próprio, de terceiro via API, de humano,
   de modelo de IA. Dado de terceiro exige camada de tradução e fixtures desde o dia 1.

---

## Famílias

### Financeiro / regulado (fintech, banco, seguro, saúde, jurídico)

Stack: linguagem com decimal nativo e tipagem forte; banco relacional, sem discussão.

**Auditoria é armazenar, não mostrar.** Este é o item que mais vira gambiarra de fim de
projeto, e por um motivo específico: quando alguém finalmente pede auditoria, o que
falta não é a tabela — é que a função de domínio nunca soube **quem** a chamou. Aí o
ator vira variável de thread, ou `SecurityContext` alcançado do fundo da camada de
dados, ou parâmetro empurrado por trinta assinaturas. Nenhuma dessas saídas é boa, e
todas custam mais que ter decidido no dia 1.

Por isso as três primeiras linhas abaixo são sobre **gravar**. A tela de auditoria,
retenção, export para regulador, encadeamento de hash e diff por campo são software
normal — construa quando alguém pedir, com o formato que a pessoa pedir. Construir
antes é adivinhar.

| Exigência | Pri | Por que não dá pra deixar pra depois |
|---|---|---|
| **Nunca float para dinheiro** — decimal com escala e moeda explícitas | P0 | trocar o tipo depois é migrar todo o histórico |
| **Ator disponível na camada que grava** — "quem fez" atravessa a cadeia de chamada | P0 | enfiar o ator nas assinaturas depois é refactor transversal em todo serviço, job e teste |
| **Nada de `UPDATE`/`DELETE` destrutivo nas entidades centrais** — append-only, ou tabela de log genérica escrita num **único** ponto (trigger, interceptor, middleware) | P0 | não se reconstrói o passado que não foi gravado |
| **ADR: saldo é derivado de lançamentos, não armazenado mutável** | P0 | contabilidade não muta saldo, acrescenta lançamento — e a auditoria vem junto de graça |
| **Idempotência em toda operação que move dinheiro** | P0 | sem chave de idempotência, retry vira cobrança dupla |
| **Modelo de dados com estado e origem**, não só saldo | P0 | conciliação exige saber de onde cada centavo veio |
| Classificação de dado pessoal + mascaramento em log (LGPD) | P0 | log com dado sensível já vazou quando você descobre |
| Ambiente de homologação com credenciais sandbox separadas | P1 | |

### Integração pesada com terceiros (bancos, ERPs, gateways, operadoras)

| Exigência | Pri | Por que |
|---|---|---|
| **Camada de tradução por parceiro** (anticorruption layer) | P0 | o formato do banco vaza pro domínio inteiro se não houver fronteira |
| **Fixtures gravadas de resposta real** de cada parceiro | P0 | sandbox de banco cai, muda e mente; sem fixture não há teste |
| Retry com backoff + fila de mortos para chamada externa | P0 | integração externa falha por padrão, não por exceção |
| Timeout explícito em toda chamada | P0 | default de biblioteca costuma ser infinito |
| Segredo e rotação de certificado (mTLS é comum em banco) | P0 | |
| Contrato versionado + alerta quando o parceiro muda | P1 | |

Sinal de alerta no plano: "integrar com N bancos" onde cada banco tem protocolo próprio.
A Onda 2 deve integrar **um** parceiro ponta a ponta e virar o molde dos outros.

### IA no núcleo do produto

Stack: ver a skill/doc de API do provedor antes de fixar modelo e preço — nunca de memória.

| Exigência | Pri | Por que |
|---|---|---|
| **Conjunto de avaliação com exemplos rotulados** desde o dia 1 | P0 | sem eval, "melhorou o prompt" é opinião; e o conjunto só se constrói com o tempo |
| **Prompt versionado junto do código**, não em banco nem em painel | P0 | prompt solto é mudança em produção sem review |
| Registro por chamada: modelo, tokens, custo, latência | P0 | retrofit de custo é caro e a conta chega antes |
| Teto de custo e timeout por requisição | P0 | |
| **Redação de dado pessoal antes de enviar ao provedor** | P0 | especialmente cruzado com domínio regulado |
| Comportamento definido para falha e alucinação do modelo | P0 | "o modelo respondeu errado" é caminho normal, não exceção |
| ADR do provedor + camada fina de troca (só o suficiente) | P1 | |

### Consumidor / conteúdo público (site, blog, e-commerce, landing)

Stack: geração estática ou SSR; complexidade de backend costuma ser o erro aqui.

| Exigência | Pri |
|---|---|
| Deploy contínuo e domínio configurado | P0 |
| Performance como orçamento explícito (LCP, peso da página) | P0 |
| Acessibilidade nos primitivos | P0 |
| SEO: metadados, sitemap, dado estruturado | P1 |
| Analytics e consentimento de cookie | P1 |

Aqui a régua **encolhe**: sem migration, sem permissão, sem trilha de auditoria.
Aplicar fundação de fintech num site pessoal é o mesmo erro, com o sinal trocado.

### Ferramenta interna / B2B SaaS

| Exigência | Pri |
|---|---|
| **Multi-tenant decidido no dia 1** (isolamento por linha, schema ou banco) | P0 |
| Modelo de papel e permissão | P0 |
| `updated_by` + `updated_at` nas entidades centrais, com o ator já no contexto | P0 |
| Exportação de dado do cliente | P1 |
| Onboarding de novo tenant como script, não como procedimento manual | P1 |

Multi-tenancy é o retrofit mais caro que existe: encosta em toda query do sistema.

Auditoria aqui é bem mais barata que em financeiro: `updated_by` + `updated_at`
costuma bastar por anos. Mas o ator no contexto continua sendo P0 — é a metade cara,
e é a mesma nos dois domínios.

### Dados / pipeline / ETL

| Exigência | Pri |
|---|---|
| **Idempotência e reprocessamento** por janela | P0 |
| Contrato de schema + o que fazer quando ele quebra | P0 |
| Linhagem: de onde veio cada registro | P0 |
| Teste com dado real amostrado, não sintético | P1 |

---

## Combinações

Domínios se somam, e a interseção costuma criar exigência própria. "Financeiro + IA"
não é a união das duas listas: acrescenta que **decisão de modelo que afeta dinheiro
precisa ser explicável e revisável por humano** — o que muda o modelo de dados, porque
a justificativa tem que ser persistida junto da decisão.

Ao combinar, diga isso no plano explicitamente. É o tipo de item que ninguém lembra de
pedir e todo mundo cobra depois.
