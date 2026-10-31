# Executar uma fase

Uma fase por vez. Não comece a próxima com a anterior sem tabela de verificação.

## Antes de começar

Levante o ambiente **sem alterá-lo**:

```bash
node -v; python3 -V; java -version 2>&1 | head -1   # o que existir
docker --version 2>/dev/null || echo "sem docker"
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '{print $1, $9}' | sort -u | head -20
```

A última linha importa: **descubra as portas ocupadas antes de escolher as suas.** A
máquina tem outros projetos, e tomar a porta de um deles é estrago que o dev só percebe
depois, quando o outro projeto não sobe.

## Regras de processo

- **Guarde o PID** de tudo que subir, e encerre por ele
- **Nunca** `pkill -f <nome>`, `killall`, nem `docker stop` em container que não é seu
- **Fixe a porta** com a opção estrita da ferramenta, para falhar alto em vez de migrar
  em silêncio — porta que muda sozinha vira README errado
- Serviço que você subiu para testar, você derruba antes de terminar

## Ordem dentro da fase

1. Faça o item
2. **Rode o critério de pronto** que o plano definiu para ele
3. Se passou, registre na tabela de verificação com o comando e o resultado
4. Se não passou, conserte ou registre como desvio — nunca siga em silêncio

Não empilhe cinco itens e teste no fim: quando quebrar, você não sabe qual foi.

## A tabela de verificação

No `docs/PLANO-FUNDACAO.md`, por fase. Cada linha traz **o comando que provou**:

| Item | Comando | Resultado |
|---|---|---|
| Testes | `npm test` | 1/1 passando |
| Typecheck | `npm run typecheck` | limpo |
| Banco de pé e persistindo | `docker compose ps` + reinício | healthy, dado mantido |

"Funcionando" não é resultado. O que não foi rodado entra como **não verificado**,
nunca como feito. Marcar como feito o que você não provou é a única falha desta skill
que não tem conserto: destrói a confiança em todas as outras linhas.

## Desvios

Toda vez que a realidade contrariar o plano — versão que não existe, biblioteca que
mudou de forma, porta ocupada, ferramenta que se recusa —, anote na tabela de desvios:

| Fase | O plano exigia | O que aconteceu | O que ficou no lugar |
|---|---|---|---|

Isso é o que mantém o plano vivo. E é a matéria-prima da seção **Armadilhas** do
`CLAUDE.md`: desvio que vai custar tempo de outra pessoa vira armadilha escrita.

## Briga com ferramenta

Duas tentativas. Se a segunda não resolveu, **adote o padrão da ferramenta**, registre o
desvio e siga.

Um sinal de que é hora de parar: você está lendo o schema da configuração para descobrir
qual chave aceita o que você quer. Isso é dívida de fase 1 que não paga nada — o objetivo
da fase é destravar a fase 2, não ter a configuração perfeita.

## Fase 2 é onde a fundação acontece

A feature de referência é o entregável mais valioso da obra inteira, porque **é o molde
que tudo copia depois**. Duas coisas nela não são negociáveis:

- **O teste dela é o padrão dos próximos.** Se for raso, todas as features seguintes
  serão rasas e ninguém vai saber por quê. Ele tem que falhar se a feature quebrar —
  desfaça a regra principal e confirme que fica vermelho
- **Ela exercita a exigência central do domínio**, não só o caminho feliz

Ao terminar a fase 2, nomeie-a no `CLAUDE.md`: *"copie o molde de `<caminho>`"*.

## Encerrar

Antes de dizer que acabou:

```bash
git status --short          # nada inesperado, nem .env, nem dist, nem node_modules
```

E responda a pergunta de saída: *se outra pessoa fosse construir a próxima feature
copiando o molde, precisaria decidir algo que não está escrito?* Se sim, o que falta é
`CLAUDE.md`, não código.
