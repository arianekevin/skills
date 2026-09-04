# Modo AUDITORIA — o que existe contra o que deveria existir

Objetivo: `docs/DIAGNOSTICO-FUNDACAO.md`, com as lacunas priorizadas e um plano que a
`obra` — ou o dev — consiga executar. Você não corrige nada aqui.

## 1. Levantar o terreno

```bash
ls -A
git log --oneline | wc -l ; git log -1 --format=%cr
ls README.md CLAUDE.md CONTRIBUTING.md docs/PLANO-FUNDACAO.md docs/adr 2>/dev/null
ls .github/workflows .gitlab-ci.yml 2>/dev/null
cat .gitignore 2>/dev/null | head
```

Identifique a stack e a forma de `src/`, leia o `README` e **uma feature representativa
ponta a ponta**. Uma feature real diz mais sobre as convenções vigentes que qualquer
documento — inclusive quando o contradiz.

Não leia o repositório inteiro. Em repositório grande, delegue o levantamento ao agente
`Explore` com a régua em mãos e trabalhe sobre o retorno.

## 2. Nomear o domínio, e confirmar

Diga em uma frase o que o projeto **é**, inferido do README, das entidades e das
dependências. Confirme em uma linha antes de julgar qualquer coisa:

> "Entendi como {um X que faz Y para Z}. Corrijo alguma coisa antes de eu avaliar?"

Com o domínio, leia `dominio.md` e derive as exigências. Elas entram como **área 0**,
avaliadas junto das outras. É aqui que a auditoria fica útil: um sistema financeiro
guardando dinheiro em float é um achado grave que **nenhuma régua genérica encontraria**
— não existe item "não use float" numa lista de boas práticas.

## 3. Marcar a régua

| Marca | Significado |
|---|---|
| ✅ | existe e funciona |
| ⚠️ | existe, mas parcial, desatualizado ou não seguido na prática |
| ❌ | ausente |
| — | não se aplica (e isso vai **escrito**) |

⚠️ é a marca mais informativa, e a mais comum em projeto real: CI que só roda lint,
README cujos comandos não rodam mais, tokens definidos com cor literal em metade dos
componentes, `CONTRIBUTING` descrevendo uma estrutura que o código abandonou.

**Verifique na prática, não pela presença do arquivo.** O arquivo existe mas o código o
contradiz? É ⚠️, não ✅.

### A verificação que mais rende: onde a regra é imposta

Para cada regra que o projeto **diz** ter, descubra quem a impõe de fato. A tabela
denuncia sozinha:

| Regra declarada | Diz que é imposta em | Realmente é |
|---|---|---|
| | | |

Armadilhas reais, encontradas em auditoria de projeto:

- Trigger `FOR EACH ROW` bloqueia `UPDATE` e `DELETE` mas **não pega `TRUNCATE`**
- Visão com junção interna **esconde** a linha órfã em vez de denunciá-la — o registro
  existe na tabela e some da tela, sem erro
- Invariante garantido só pela transação do app: qualquer escrita fora dele o quebra
- Regra que existe só na documentação, sem lint, teste ou constraint atrás

Teste os três caminhos em qualquer garantia de banco: `UPDATE`, `DELETE`, `TRUNCATE`.
Faça as sondas dentro de `begin; ... rollback;` — auditoria não altera dado.

**Regra que não declara onde é imposta é desejo.** Procure também as regras
**implícitas**: invariantes que o código depende e que ninguém escreveu. Costumam ser as
mais frágeis, justamente porque nunca foram enunciadas.

## 4. Priorizar

Ordene por **custo de retrofit crescente**, não por facilidade. Sobe quem:

- **Bloqueia outras** — sem estrutura de teste, nenhuma diretriz de qualidade se sustenta
- **Fica exponencialmente mais cara** — testes, tokens, a11y, migrations, ator na
  assinatura: o custo cresce com o número de arquivos que já violam o padrão
- **Já está sangrando** — bug ou retrabalho recorrente atribuível a ela
- **É exigência do domínio** — encosta no modelo de dados, não na configuração

Desce quem é aditivo e de custo constante: `CHANGELOG`, `CODEOWNERS`. Custa o mesmo
hoje ou daqui a um ano.

## 5. Os baldes

Mesmo formato do modo NOVO, mais um balde que só existe aqui:

- **Obrigatório** — com onde deve ser imposto e critério verificável
- **Opcional** — com o sinal que o tornaria necessário
- **Adiado de propósito** — com gatilho
- **Adotar daqui pra frente** — a lacuna que não vale corrigir retroativamente
- **Não se aplica** — escrito

O quarto balde é o que torna a auditoria executável. Projeto de três anos não reescreve
histórico de migration, e projeto sem teste no dia 100 não ganha teste em tudo — isso
ninguém faz. O que funciona é *"toda mudança nova sai com teste"*. Diga isso
explicitamente em vez de listar uma dívida que ninguém vai pagar.

Para cada item grande, quebre em passos ou proponha a versão mínima. "Migrar 40
componentes para tokens" não é item de plano; "criar a escala e migrar os 5 componentes
mais usados" é.

## 6. Escrever e reportar

Preencha `assets/DIAGNOSTICO.template.md`. No terminal mostre **só**: o domínio como
você o entendeu, o placar por área, os três primeiros itens e o que caiu em "adotar
daqui pra frente".

## Tom

Diagnóstico, não julgamento. Projeto rodando em produção sem ADR não é projeto ruim — é
projeto que priorizou entrega. Relate a lacuna e a consequência dela; pagar ou não é
decisão do dev. Evite adjetivo, use consequência: não "o setup está fraco", e sim "sem
teste no CI, uma regressão só aparece em produção".
