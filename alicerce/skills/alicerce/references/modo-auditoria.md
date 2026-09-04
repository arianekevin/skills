# Modo AUDITORIA — o que existe vs. o que falta

Objetivo: produzir `docs/DIAGNOSTICO-FUNDACAO.md` com lacunas priorizadas e um plano.

## 1. Levantar o terreno (antes de julgar)

```bash
ls -A
git log --oneline | wc -l ; git log -1 --format=%cr
find . -path ./node_modules -prune -o -type f -name '*.md' -print | head -20
ls .github/workflows .gitlab-ci.yml 2>/dev/null
ls docs docs/adr 2>/dev/null
cat .gitignore 2>/dev/null | head
```

Depois identifique stack e forma de `src/`, e leia o `README` e **uma** feature
representativa ponta a ponta. Uma feature real diz mais sobre as convenções vigentes
que qualquer documento — inclusive quando contradiz o documento.

**Não leia o repo inteiro.** Para repos grandes, delegue o levantamento ao agente
`Explore` com a régua em mãos e trabalhe sobre o retorno.

## 2. Marcar a régua

Percorra `checklist-fundacao.md` e classifique cada item:

| Marca | Significado |
|---|---|
| ✅ | existe e funciona |
| ⚠️ | existe, mas parcial, desatualizado ou não seguido na prática |
| ❌ | ausente |
| — | não se aplica a este projeto |

⚠️ é a marca mais informativa. Casos típicos: CI que só roda lint e não roda teste;
README cujos comandos não rodam mais; tokens definidos mas com cor hardcoded em
metade dos componentes; `CONTRIBUTING` descrevendo uma estrutura que o código
abandonou. **Verifique na prática, não pela presença do arquivo.**

Teste barato de ⚠️: o arquivo existe, mas o código o contradiz? Então é ⚠️, não ✅.

## 3. Priorizar as lacunas

Ordene por **custo de retrofit crescente ao longo do tempo**, não por facilidade.
Uma lacuna sobe de prioridade quando:

- **Bloqueia outras** — sem CI, nenhuma outra convenção se sustenta
- **Fica exponencialmente mais cara** — tokens, a11y, migrations, permissão: o custo
  cresce com o número de arquivos que já violam o padrão
- **Já está sangrando** — tem bug ou retrabalho recorrente atribuível a ela

Desce de prioridade quando é aditiva e de custo constante (CHANGELOG, CODEOWNERS):
custa o mesmo hoje ou daqui a um ano, então pode esperar.

Nomeie explicitamente as lacunas **que já não vale a pena corrigir** por completo —
um projeto de 3 anos sem migration versionada não vai reescrever o histórico; ele
adota a partir de agora. Marque como "adotar daqui pra frente".

## 4. Plano de implementação

Três ondas, cada item com esforço estimado (P ≤1h / M ≤meio dia / G >1 dia):

- **Onda 1 — o que destrava o resto.** CI, tooling, `.env.example`. Sempre P ou M.
- **Onda 2 — o que fica mais caro a cada semana.** Tokens, migration, forma de erro,
  modelo de permissão. Inclui as adoções "daqui pra frente".
- **Onda 3 — o aditivo.** Docs, ADRs retroativos dos porquês que ninguém lembra mais.

Para cada item G, quebre em passos ou proponha uma versão mínima. "Migrar 40
componentes para tokens" não é item de plano; "criar tokens + migrar os 5
componentes mais usados" é.

## 5. Escrever e reportar

Preencha `assets/DIAGNOSTICO.template.md` em `docs/DIAGNOSTICO-FUNDACAO.md`.

No terminal, mostre **só**: o placar por área, os 3 itens da Onda 1, e o que você
marcou como "não vale mais corrigir". O documento tem o resto.

## Tom

Este é um diagnóstico, não um julgamento. Projeto rodando em produção sem ADR não é
projeto ruim — é projeto que priorizou entrega. Relate a lacuna e o custo dela; a
decisão de pagar ou não é do dev. Evite adjetivo, use consequência: não "o setup está
fraco", e sim "sem teste no CI, uma regressão só aparece em produção".
