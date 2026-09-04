# A régua — o que "bem fundado" significa

**Esta régua é o piso, não o plano.** Ela vale para qualquer projeto, e por isso não
sabe nada sobre o seu. Leia `dominio.md` **antes** e some as exigências de lá — são
elas que costumam ser as mais caras de retrofitar, porque mexem no modelo de dados.
Plano que só tem esta régua é plano que não olhou pro projeto.

Oito áreas. Cada item tem **prioridade** e **sinal de detecção** (o que procurar no repo).

Prioridades:
- **P0** — barato agora, caro depois. Retrofit dói. Nasce com o projeto.
- **P1** — importante, mas pode entrar na primeira semana sem prejuízo.
- **P2** — melhora a vida, não bloqueia nada.

Marque **N/A** sem culpa: design system não se aplica a uma CLI; migrations não se
aplicam a um site estático. N/A honesto vale mais que checklist inflado.

---

## 1. Produto & escopo

| Item | Pri | Sinal de detecção |
|---|---|---|
| Uma página: problema, usuário, **não-escopo**, critério de pronto | P0 | `docs/PRODUTO.md`, `README` com seção de propósito |
| Critério de sucesso mensurável (mesmo que grosseiro) | P1 | idem |

O **não-escopo** é o item mais negligenciado e o que mais economiza retrabalho.
Sem ele, arquitetura e design system são chutados no vácuo.

## 2. Decisões registradas (ADR)

| Item | Pri | Sinal de detecção |
|---|---|---|
| 5–8 ADRs iniciais: stack, banco, auth, topologia (mono/serviços), hospedagem | P0 | `docs/adr/*.md` |
| Template de ADR para os próximos | P1 | `docs/adr/0000-template.md` |

Formato: *contexto / decisão / consequências / alternativas descartadas*. Curto.
É o documento que mais paga dividendo — evita reabrir decisão já fechada.

## 3. Repo, tooling & CI

| Item | Pri | Sinal de detecção |
|---|---|---|
| Formatter + linter configurados | P0 | `.prettierrc`, `eslint.config.*`, `ruff.toml`, `checkstyle.xml` |
| Typecheck (se a linguagem tem) | P0 | `tsconfig.json` com `strict: true` |
| Runner de teste + **1 teste passando** | P0 | `*.test.*`, `tests/`, `src/test/` |
| CI rodando os quatro acima, verde | P0 | `.github/workflows/*.yml`, `.gitlab-ci.yml` |
| `.gitignore` e `.editorconfig` | P0 | idem |
| Convenção de commit (Conventional Commits) | P1 | `commitlint.config.*`, `CONTRIBUTING.md` |
| Hooks de pré-commit | P2 | `.husky/`, `.pre-commit-config.yaml` |

Regra dura: **CI verde no primeiro commit**. Se não nasce junto, não entra depois.

## 4. Convenções de código & estrutura

| Item | Pri | Sinal de detecção |
|---|---|---|
| Um eixo de organização declarado, sem mistura | P0 | forma de `src/` |
| Regra de dependência entre camadas | P1 | `CONTRIBUTING.md`, `dependency-cruiser`, ArchUnit |
| Uma feature de referência que serve de template | P1 | ler a primeira feature |

Preferir pasta **por domínio/feature** (`features/cobranca/…`) a pasta por tipo
técnico (`controllers/`, `services/`). Sintoma de eixo misturado: para tocar uma
feature você abre cinco pastas de topo distintas.

## 5. Design system *(só se tem UI)*

Ordem obrigatória — pular etapa é o erro clássico:

| Item | Pri | Sinal de detecção |
|---|---|---|
| **Tokens** — cor, espaçamento, tipografia, raio, sombra, motion | P0 | `tokens.css`, `theme.ts`, `tailwind.config.*` |
| **Primitivos** consumindo só tokens (Button, Input, Card, Stack) | P1 | `components/ui/` |
| **Padrões** — formulário, tabela, layout de página | P1 | `components/patterns/` |
| **Estados** definidos: loading, vazio, erro, sem permissão | P0 | procure `Empty`, `Skeleton`, `ErrorBoundary` |
| A11y nos primitivos (foco, label, contraste, teclado) | P0 | `aria-`, `<label>`, tokens de contraste |
| Dark mode via troca de token, não via cor hardcoded | P1 | cor literal em componente = red flag |

Red flag forte: componente bonito **sem** escala de espaçamento por trás. Significa
que começaram pelos componentes. Retrofit de token em 40 componentes é caro.
Retrofit de a11y é reescrever o componente.

## 6. Documentação viva

| Item | Pri | Sinal de detecção |
|---|---|---|
| `README` que roda o projeto em ≤3 comandos | P0 | testar mentalmente os comandos |
| `CONTRIBUTING.md` — convenções + fluxo de branch | P1 | idem |
| `CHANGELOG.md` | P2 | idem |
| `CLAUDE.md` / instruções pro agente | P1 | idem |

Doc que não vive ao lado do código morre. Wiki paralela é sinal de alerta, não de
maturidade. `README` desatualizado é pior que ausente — mede-se pelos comandos:
se o comando do README não roda, a doc está morta.

## 7. Dados & configuração

| Item | Pri | Sinal de detecção |
|---|---|---|
| `.env.example` versionado, `.env` ignorado | P0 | idem |
| Um único módulo que lê e valida config | P1 | `config.ts`, `settings.py` |
| Migrations versionadas **desde a tabela 1** | P0 | `migrations/`, `flyway/`, `prisma/migrations` |
| Seed de dados realista | P1 | `seed.*`, `fixtures/` |

Seed realista é o que torna o design system testável de verdade — sem ele, todo
componente é desenhado com "Lorem ipsum" e quebra com dado real.

## 8. Operação & segurança

| Item | Pri | Sinal de detecção |
|---|---|---|
| Tratamento de erro com forma única (não `catch` genérico espalhado) | P0 | procure `catch` sem reação |
| Log estruturado, com nível | P0 | `pino`, `winston`, `structlog`, `slf4j` |
| Modelo de auth/permissão **decidido** (implementação pode vir depois) | P0 | ADR de auth |
| Nenhum segredo no repo | P0 | `git log -p \| grep -iE 'api[_-]?key\|secret\|password'` |
| Healthcheck / readiness | P1 | rota `/health` |
| Licença, `CODEOWNERS` | P2 | idem |

Observabilidade enxertada tarde é dolorosa. Permissão enxertada tarde vaza por todo
lado — por isso o **modelo** é P0 mesmo quando a implementação é P2.

---

## Adiar de propósito

Não entram na fundação, e o plano deve dizer isso explicitamente com o gatilho de
revisita:

| Adiado | Revisitar quando |
|---|---|
| Microserviços | o deploy conjunto virar gargalo entre times |
| i18n | existir compromisso real com um segundo idioma |
| Cache | houver medição mostrando o gargalo |
| Feature flags | houver mais de um ambiente com público real |
| Abstração "caso troquemos de banco" | a troca estiver de fato na mesa |
| Monorepo / workspaces | existir o segundo pacote de verdade |

Listar o adiado tem valor próprio: transforma "esquecemos" em "decidimos".
