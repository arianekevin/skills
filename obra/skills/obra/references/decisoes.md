# Escolher ferramenta e registrar a decisão

O plano diz **o requisito**; a escolha é sua. Isso não é liberdade, é responsabilidade:
cada escolha vira um ADR, e o ADR é o que impede a próxima pessoa de reabrir a discussão
sem saber o que já foi pesado.

## A ordem de preferência

1. **O que já é padrão da casa.** Leia dois ou três projetos vizinhos antes de trazer
   coisa nova. Consistência entre projetos vale mais que a escolha ótima em um — o dev
   que troca de repo não deveria trocar de vocabulário
2. **O que a stack já traz.** Dependência a menos é manutenção a menos
3. **O que atende o requisito com menos peças.** Formatter e linter num tool só ganha de
   dois que brigam
4. Só então, o que é popular

```bash
ls ../*/package.json ../*/pom.xml 2>/dev/null | head
cat ~/.claude/CLAUDE.md 2>/dev/null | head -40
```

## Verifique antes de fixar

**Nunca fixe versão de memória.** Confira o que existe hoje e se as peças combinam entre
si — a versão mais nova de uma frequentemente não tem rodagem com a outra.

```bash
npm view <pacote> version
npm view <pacote> peerDependencies --json
```

Escolher a versão mais nova por padrão é um erro caro em fundação: a fase 1 não é lugar
de descobrir que a ferramenta de tipos ainda não acompanha o compilador novo. **Prefira
a mais recente que tenha rodagem com o resto**, e escreva no ADR por que não foi a
última.

## O ADR

Um por escolha que outra pessoa poderia questionar. Formato em `docs/adr/0000-template.md`.

O que ele precisa ter, além do óbvio:

- **A data e o que estava disponível nela.** "Escolhido X 5.9, sendo 7.0 a mais nova, porque
  a ferramenta Y ainda não rodava com ela em {data}" — isso transforma o ADR em algo que
  envelhece bem: quem ler daqui a um ano sabe que a razão pode ter caducado
- **O que fica difícil depois.** É a parte que ninguém escreve e todo mundo queria ter lido
- **As alternativas descartadas**, com uma linha de por quê. Sem isso, alguém vai propor
  a mesma alternativa em três meses

Não escreva ADR para o que não tem alternativa razoável. ADR de "usamos git" é ruído, e
ruído faz ninguém ler os que importam.

## O que NÃO é sua decisão

Requisito. Se você se pegar decidindo **se** algo deve existir — em vez de **com o quê**
fazer —, isso é da `alicerce`. Exemplos que voltam para ela:

- "acho que precisa de CI" quando o plano não pediu
- "aproveitei e coloquei autenticação" quando estava adiado
- "mudei a estrutura de pastas porque ficava melhor assim"

Adiado de propósito **tem gatilho escrito**. Implementar adiado sem que o gatilho tenha
acontecido é desfazer uma decisão que alguém tomou com contexto que você não tem.

Se durante a obra ficar claro que o plano errou, **pare e diga** — com o que você
descobriu. Corrigir o plano é barato; descobrir três meses depois que a obra não seguiu
o plano, não.
