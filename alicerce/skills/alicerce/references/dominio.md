# O domínio muda o plano

A régua genérica é o **piso**. O domínio decide a stack e acrescenta exigências que a
régua não tem — e essas exigências costumam ser as mais caras de retrofitar, porque
mexem no modelo de dados, não na configuração.

Regra de uso: da frase do projeto, identifique **uma família principal** (às vezes duas)
e puxe de **2 a 5 exigências**, não vinte. Fundação inchada não é fundação — é backlog.

Cada exigência derivada entra no plano com a mesma forma dos outros itens: o que fazer,
por que agora, pronto quando. E precisa dizer **por que este projeto** precisa dela.

---

## O filtro: isso é dor de fundação?

Nem toda dor da casa vira item daqui. O teste é: **se o projeto tivesse começado
diferente, essa dor existiria?**

- **Sim** → é fundação. Nasceu de decisão de dia 1 que ficou cara. Ex.: auditoria sem
  ator na assinatura, código sem costura de teste, multi-tenancy decidida tarde
- **Não** → é operação ou diagnóstico, e pertence a outra skill. Ex.: cliente rodando
  versão antiga, investigar bug sem acesso à base, dois frontends herdados

Sem o filtro, a régua incha com dor verdadeira que ela não tem como resolver — e um
plano genérico é ruído. Quando o dev contar uma dor nova, passe por aqui primeiro, e
diga em qual dos dois lados ela caiu.

Uma dor pode ainda **confirmar prioridade sem acrescentar item**: se ela já está na
régua, a contribuição é subir a prioridade e escrever o exemplo real, não criar linha
nova.

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

Por isso as linhas abaixo são sobre **gravar**. A tela de auditoria, retenção, export
para regulador, encadeamento de hash e diff por campo são software normal — construa
quando alguém pedir, com o formato que a pessoa pedir. Construir antes é adivinhar.

E repare na coluna da direita: **garantia que mora na transação do app não é garantia**.
Duas armadilhas reais, encontradas em auditoria de projeto: uma trigger `FOR EACH ROW`
não pega `TRUNCATE`, e uma visão com junção interna **esconde** a linha órfã em vez de
denunciá-la. Toda exigência que diz "imposta pelo banco" precisa ser testada nos três
caminhos — `UPDATE`, `DELETE` e `TRUNCATE`.

| Exigência | O que quebra sem ela | Onde é imposta |
|---|---|---|
| **Nunca float para dinheiro** — decimal com escala e moeda explícitas | centavo errado que só aparece no total, quando já não dá pra saber de onde veio; trocar o tipo depois é migrar todo o histórico | tipo + coluna do banco |
| **Ator disponível na camada que grava** | a auditoria não responde "quem fez"; enfiar o ator nas assinaturas depois é refactor transversal em todo serviço, job e teste | assinatura de função — não compila sem |
| **Nada de `UPDATE`/`DELETE` destrutivo nas entidades centrais** — append-only, ou log genérico escrito num **único** ponto | não se reconstrói o passado que não foi gravado | banco (constraint ou trigger), **cobrindo também `TRUNCATE`** |
| **ADR: saldo derivado de lançamentos, não armazenado mutável** | log e saldo discordam e ninguém sabe qual mente | modelo de dados: a coluna mutável não existe |
| **Idempotência em toda operação que move dinheiro** | retry vira cobrança dupla | chave única no banco |
| **Todo registro central nasce com seu evento** | linha sem evento some da visão derivada, em silêncio | banco — não a transação do app |
| Classificação de dado pessoal + mascaramento em log | log com dado sensível já vazou quando você descobre | revisão / lint |
| Ambiente de homologação com credenciais separadas | teste toca dado real | config |

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

---

## Acrescentando uma dor nova

O melhor conteúdo deste arquivo veio do dev contando o **mecanismo** da falha, não a
categoria. "Auditoria é importante" não gera item nenhum; *"é armazenar e não mostrar, e
vira gambiarra no fim do projeto"* gera três, porque tem um item de dia 1 escondido
dentro.

Ao ouvir uma dor nova, pergunte pelo mecanismo — como quebra na prática — e depois
passe pelo filtro do topo deste arquivo. Só então escreva a linha, sempre com as duas
colunas: **o que quebra sem ela** e **onde é imposta**.
