---
name: obra
description: "Levanta a fundação de um projeto a partir do que a skill alicerce especificou. Use quando o dev pedir para executar o plano de fundação, quando mencionar 'executar a fase 1', 'levantar o projeto', 'implementar o plano', 'montar o esqueleto', 'obra', ou quando existir um docs/PLANO-FUNDACAO.md esperando execução. Ela decide ferramenta e versão — o plano não decide isso —, registra cada escolha em ADR, verifica cada fase com comando, e para quando o molde está provado. NÃO especifica fundação: se não houver plano, quem escreve é a alicerce."
---

# Obra — levantar a fundação

Lê `docs/PLANO-FUNDACAO.md`, executa as fases e para quando **o molde está provado**.

A `alicerce` especifica o requisito; você escolhe a ferramenta. Essa divisão é o motivo
de o plano não citar versão: quem não executa não tem como conferir, e plano com versão
nasce velho. **A escolha é sua, e ela vira ADR.**

## Cancela

**Sem plano, sem obra.** Se não existir `docs/PLANO-FUNDACAO.md`:

> "Não há plano de fundação aqui. Quem escreve é a `alicerce` — ela faz as perguntas e
> especifica o que é obrigatório, opcional e adiado. Rodo ela primeiro?"

Não improvise a especificação. Levantar fundação sem contrato é exatamente como se
constrói o que ninguém consegue explicar depois.

## Regras invioláveis

1. **Você decide ferramenta, nunca requisito.** Requisito que não está no plano não
   entra: pergunte, ou volte para a `alicerce`. Escopo que cresce sozinho é o modo mais
   comum de a fundação virar projeto.
2. **Não encoste em nada fora do projeto.** A máquina tem outros projetos de pé. Mate
   pelo PID que você guardou, **nunca por padrão de nome** — `pkill -f vite` derruba o
   servidor de outro projeto e você nem fica sabendo qual era. Confira a porta antes e
   **fixe** a sua; não pare container que não foi você quem subiu.
3. **Ferramenta que resiste duas vezes tem o padrão dela adotado.** Se a segunda
   tentativa de configurar não resolveu, pare de brigar: aceite o default, registre como
   desvio e siga. Tooling de fase 1 não pode virar o projeto.
4. **Verifique a própria escrita.** Edição por âncora falha em silêncio quando o arquivo
   mudou desde que você o leu — um formatter rodou, um rename aconteceu. Confirme que
   aplicou antes de seguir.
5. **Não commite sem pedido**, e nunca com `git add -A` às cegas. Sem `push` nunca.

## Padrões comuns

Leia **`PADROES.md`** (ao lado deste arquivo) antes de agir.

## Fluxo

### 1. Ler o contrato

**Leia do disco, sempre** — inclusive quando a `alicerce` acabou de rodar nesta mesma
conversa e você "já sabe" o que ela escreveu. O contrato é o arquivo, não a memória da
conversa: o dev pode ter corrigido o plano depois de ler, e a versão do disco é a que
vale.

Leia o plano inteiro, e a seção **`## Requisitos para a obra`** com atenção: cada item
traz fase, requisito, **onde é imposto** e **critério de pronto verificável por comando**.
Esse critério é seu ponto de parada de cada item — não invente outro.

Leia também: as exigências do domínio, o que foi **adiado de propósito** (não implemente
adiado), o que é **`N/A`**, e as suposições — se alguma estiver errada, é mais barato
descobrir agora.

### 2. Escolher as ferramentas

Antes da fase 1, resolva as escolhas que o plano deixou abertas. Para cada uma, leia
`references/decisoes.md`: como escolher, e como registrar o ADR com o que estava
disponível **na data**.

Verifique versão e compatibilidade **antes** de fixar — não de memória. E prefira o que
já é padrão da casa: leia dois ou três projetos vizinhos antes de trazer coisa nova.

### 3. Executar fase por fase

Siga `references/execucao.md`. Uma fase por vez, e cada uma fecha com a tabela de
verificação preenchida no plano.

### 4. Parar no critério de saída

O plano diz: **a fundação está pronta quando a segunda feature sai do molde sem
pergunta.** Você não escreve a segunda feature — sua entrega é a primeira, a de
referência, que é a **prova de que o molde funciona**.

Ao terminar a fase 3, faça a pergunta de saída honestamente:

> "Se outra pessoa fosse construir a próxima feature copiando `{caminho do molde}`, ela
> precisaria decidir alguma coisa que não está escrita?"

Se a resposta for sim, **o que falta é convenção escrita, não código**: complete o
`CLAUDE.md` antes de dizer que acabou.

## O que você preenche nos documentos

A `alicerce` deixou pendências marcadas. Fechá-las é parte da obra:

| Documento | O que você completa |
|---|---|
| `docs/PLANO-FUNDACAO.md` | verificação por fase e tabela de desvios |
| `README.md` | a seção **Rodar** — os comandos reais, testados do zero |
| `CLAUDE.md` | **Comandos**, **Armadilhas já encontradas aqui**, nome da feature de referência, traço de uma requisição |
| `docs/adr/` | um ADR por escolha de ferramenta ou versão |

A seção de armadilhas é a mais valiosa e a mais esquecida: cada uma custou tempo seu uma
vez, e escrever ali é o que impede a segunda.

## Saída honesta

Se um requisito não puder ser cumprido — dependência que não existe, ambiente que não
sobe, critério de pronto que não passa —, **pare e diga**. Não marque como feito, não
afrouxe o critério, não troque o comando por um mais fácil.

Entregue: até onde chegou, o que falta nomeado, e o que você tentou. O plano tem a tabela
de desvios para isso, e "não verificado" é uma resposta legítima; "feito" sem comando que
prove não é.

## Referências

- `references/execucao.md` — como executar uma fase e fechá-la com verificação
- `references/decisoes.md` — como escolher ferramenta e versão, e escrever o ADR
