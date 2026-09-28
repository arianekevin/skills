# Padrões comuns às skills

Regras que valem para **todas** as skills deste repositório. Cada `SKILL.md` aponta
para cá em vez de repetir — se uma regra muda, muda em um lugar só.

Fonte única: este arquivo, na raiz. As cópias dentro de cada plugin são geradas por
`scripts/sync-padroes.sh` — não edite as cópias.

---

## 1. Pergunta: escolha quando houver opções, aberta quando não houver

O critério não é "sempre dar alternativas". É **nunca fazer o dev digitar o que podia
ter sido uma escolha**.

- **Tem opções enumeráveis?** Entregue como escolha para marcar. E as opções saem de
  investigação **sua**, não de categoria genérica: em vez de "qual módulo?", os três
  candidatos reais que você achou no código, com o caminho do arquivo.
- **É genuinamente aberta** — uma decisão que só o dev pode tomar, sem alternativas a
  oferecer? Pergunta aberta mesmo. Forçar múltipla escolha aqui é pior: inventa opções
  que não existem e enviesa a resposta.

Exemplos de aberta legítima: "qual a causa raiz?", "qual o escopo da correção?",
"o que é esse projeto?". Ninguém pode enumerar isso por ele.

Exemplos de fechada obrigatória: qual arquivo, qual branch, qual das hipóteses,
qual ticket, qual das três estratégias, sim/não.

Na dúvida, o teste é: **eu conseguiria listar as respostas plausíveis?** Se sim, liste.

## 2. Procedência: o que você não verificou, você não afirma

Vale para todo identificador concreto — nome de tabela, coluna, entidade, endpoint,
chave de configuração, tag de versão, nome de arquivo, assinatura de método.

Confirme na fonte antes de escrever o nome numa hipótese ou conclusão. Se não
conseguir confirmar, **declare a lacuna**: "existe uma tabela de X, cujo nome eu não
localizei" é uma frase honesta. Nome inventado com cara de certeza é pior que lacuna
declarada — o dev vai atrás e perde a viagem.

**E ausência não é prova.** "Não encontrei" só vira argumento depois de estabelecer
onde você procurou e se aquele era o lugar certo. Ambiente errado, branch errada,
tenant sem migration aplicada — todos produzem "não existe" falso.

**Vale também para a sua própria escrita.** Edição por âncora de texto falha **em
silêncio** quando o arquivo mudou desde que você o leu — um formatter rodou, um rename
aconteceu, outra edição sua passou antes. Depois de escrever, confirme que aplicou: um
`grep` no trecho novo, ou o comando que agora precisa passar. Seguir supondo que pegou
é a mesma falha de procedência, virada para dentro — e ela se repete, porque a
suposição errada continua valendo na edição seguinte.

## 3. Escrita fora do repositório: só com pedido explícito

Ler é o uso previsto. **Escrever exige pedido do dev naquela sessão**, e vale para:
comentar ou mudar estado de ticket no YouTrack, `git push`, deploy, mensagem em canal,
chamada que altera dado em ambiente compartilhado.

Autorização não se estende: aprovar um push não aprova o próximo, e aprovar um
comentário em ticket não aprova mexer no estado dele.

**E não encoste em processo, porta ou container que não é seu.** A máquina do dev tem
outros projetos rodando. Encerre pelo **PID que você mesmo guardou**, nunca por padrão
de nome — `pkill -f vite` derruba o servidor de desenvolvimento de outro projeto, e
você nem fica sabendo qual era. Antes de subir serviço, confira se a porta está livre
e **fixe** a sua; antes de parar um container, confirme que foi você quem o subiu.

## 4. Saída honesta: declare o travamento em vez de fechar

Toda skill precisa de pelo menos uma saída que não seja sucesso, e ela precisa ser
tão legítima quanto a de sucesso. Quando a única forma de terminar é concluindo,
a conclusão vem sem evidência — e uma causa raiz plausível e errada custa mais caro
que um "não sei" honesto.

A saída travada carrega sempre três coisas:

1. **Até onde chegou** — o que ficou estabelecido com evidência, e o que caiu
2. **O que falta**, nomeado com precisão
3. **Como obter** — a query pronta, o log a olhar, a pessoa a perguntar

E a régua não se afrouxa para caber num resultado: não marque teste como skip, não
relaxe asserção, não troque o critério por um mais fácil. Se o critério estiver
errado, pare e diga.
