# Qual doc é o desta tarefa — e quando não é

Usado por `fechar-sessao` e `finalizar-tarefa`. O erro caro é o silencioso: escrever a sessão de hoje
no doc de outra tarefa, ou apagar o doc errado. Na dúvida, perguntar — uma pergunta, com as opções.

## 1. O repo tem doc de continuidade próprio?

**Primeiro, o marcador explícito.** Procure no `CLAUDE.md` do repo (raiz e `.claude/CLAUDE.md`) uma
linha no formato:

```
Doc de pendências: docs/CONTINUIDADE.md
```

Se existir, é o destino — sem interpretar mais nada. `Doc de pendências: docs/pendencias/` (a pasta)
declara o modo "um por tarefa" explicitamente.

**Sem marcador, a leitura.** Leia o `CLAUDE.md` e o `CONTRIBUTING.md`, se houver. Se algum
deles **manda manter** um arquivo que descreve o presente do trabalho ("leia no início de toda sessão",
"atualize no mesmo commit") — ex.: `docs/CONTINUIDADE.md` no ndesk — esse é o destino, e as regras de
manutenção dele valem acima das desta skill. Não crie `docs/pendencias/` nesse repo.

Se a leitura deixar dúvida (o doc existe mas o CLAUDE.md não diz que é para manter), pergunte uma vez
e sugira gravar o marcador acima no CLAUDE.md, para a pergunta não se repetir.

Nesse caso "a tarefa" é um **bloco** dentro do doc (item de "Próximos passos", seção "Trabalho em
andamento", decisão em aberto), não um arquivo. O resto do passo 2 vale para achar o bloco.

## 2. Sem doc próprio: `docs/pendencias/<tarefa>.md`

Um arquivo por tarefa. Nome: slug curto do assunto (`troca-de-senha.md`), não da data nem da branch.

Liste `docs/pendencias/*.md` e leia o cabeçalho de cada um. Para cada candidato, conte os sinais:

| sinal | como medir |
|---|---|
| a pessoa nomeou a tarefa | ela disse o assunto, e ele bate com `tarefa:` |
| mesma branch | `git branch --show-current` == `branch:` |
| escopo em comum | arquivos mexidos na sessão (`git status`, `git log` desde `atualizado:`) caem em `escopo:` |
| continuidade | o que a sessão fez é o "Próximo passo" registrado no doc |

- **Pertence:** a pessoa nomeou a tarefa, ou dois sinais batem. Atualize esse.
- **Não pertence a nenhum:** nenhum candidato com sinal. Crie um novo (fechar) ou diga que não há doc
  (finalizar).
- **Ambíguo:** um sinal só, ou mais de um candidato com sinais. Pergunte, listando os candidatos
  pelo `tarefa:` — nunca escolha sozinho entre dois.

Nunca edite, mescle ou apague o doc de outra tarefa. Uma sessão que tocou duas tarefas atualiza dois
docs, cada um com o que é seu.

## 3. Fora de um repo

Se a sessão não mexeu em nenhum repo git, ou mexeu em vários, pergunte em qual repo registrar (ou em
quais). Não escreva em `~` nem em diretório sem git.

## Formato do doc por tarefa

```markdown
---
tarefa: <nome curto, como a pessoa chama>
branch: <branch onde está o trabalho>
escopo: <diretórios/arquivos principais, separados por vírgula>
criado: AAAA-MM-DD
atualizado: AAAA-MM-DD
---

# <tarefa>

## Onde paramos
<2–4 linhas: o estado de agora e o primeiro passo ao voltar>

## Feito
- <fato verificado, com commit curto quando houver>

## Combinado
- <decisão — por quê — gatilho para revisitar, se houver>

## Adiado
- <o quê — por quê — gatilho de volta>

## Próximo passo
1. <na ordem>

## Estado do ambiente
<não commitado, não empurrado, branches locais, servidores/serviços de que depende; "nada" se nada>
```
