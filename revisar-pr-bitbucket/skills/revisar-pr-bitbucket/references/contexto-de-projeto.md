# Contexto de projeto

A skill é genérica. O que faz uma revisão achar o que importa é saber **onde os bugs se escondem
naquele sistema** — e isso não vai para um repositório público.

## Onde fica

`~/.claude/revisar-pr-bitbucket/contexto/<slug-do-repo>.md`, na máquina do dev. O slug é o nome
do repo no Bitbucket (`workspace/<slug>`). Fora do plugin de propósito: atualizar o plugin não
apaga, e o conteúdo não é publicado.

Sem arquivo de contexto a revisão roda do mesmo jeito, só com o método da SKILL.md. Quando a
revisão achar algo que valeria para os próximos PRs do mesmo repo (uma porta paralela, uma regra
de domínio que derrubou um achado), sugira acrescentar uma linha ao arquivo — não escreva sem o dev pedir.

## O que vale pôr

- **Repos e branches:** onde fica o backend, o front, a branch-alvo dos PRs, como achar o repo de um commit.
- **Portas paralelas:** os vários caminhos que chegam na mesma gravação (API v1/v2, telas antigas,
  ação em massa, importação, integrações, webhooks, jobs). É onde a correção de um lado deixa o outro aberto.
- **Permissão:** o que cada anotação/gate realmente checa, configurações de conta que mudam o filtro,
  consultas que devolvem registro excluído, como o tenant é filtrado.
- **Banco:** padrões que já travaram produção (listagem sem paginação, concatenação em HQL/SQL, filtro sem índice).
- **Regras de domínio que NÃO são achado:** fatos que já derrubaram uma revisão ("fluxo X é legado", "usuário Y não opera").
- **Consumidores do contrato:** quem chama a API (front, SDK, mobile, integrações) — para avaliar mudança de status HTTP.

Frases curtas, com caminho de arquivo quando ajudar. Não é documentação do sistema: é a lista do
que a revisão deve olhar duas vezes.
