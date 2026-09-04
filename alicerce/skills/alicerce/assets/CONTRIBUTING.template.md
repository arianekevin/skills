# Como se trabalha aqui

_Escrito pela skill `alicerce` na fundação do projeto. Vale para pessoas e para IA._

## Definition of Done

Uma mudança está pronta quando **todas** as linhas abaixo valem. A coluna da direita diz
quem impõe cada uma — e `acordo` significa que nada além da disciplina segura essa
regra. Isso é uma escolha declarada, não um esquecimento.

| Regra | Imposta por |
|---|---|
| {ex.: testes escritos e todos verdes} | {CI / hook / revisão / acordo} |
| {ex.: lint e formato limpos} | {} |
| {ex.: typecheck limpo} | {} |
| {ex.: documentação atualizada quando o comportamento mudou} | {} |
| {ex.: feature nova sai com tour — passos, âncoras e versão} | {} |

{Se CI não existe, escrever aqui: "Não há CI neste projeto. As regras acima são acordo —
nada as segura automaticamente. Ligar CI é o que as transforma em garantia."}

## Testes

**Onde moram:** {}
**Como se chamam:** {}

**O critério de teste útil:** desfaça a mudança que o teste cobre — se nenhum teste fica
vermelho, o teste não existe. Regra que só conta testes produz `expect(1+1)`.

**O molde é o teste da feature de referência** ({caminho}). Toda feature nova copia
aquela pasta; se o teste dela for raso, todos os seguintes serão rasos.

{Em projeto que já existia: "Não vamos escrever teste para o que já está aqui. **Toda
mudança nova sai com teste** — é o que se adota daqui pra frente."}

## Tour

**Toda feature nova sai com tour.** Feature entregue sem tour não está pronta.

**Onde os tours moram:** {}
**Âncora:** {o identificador próprio do tour que os componentes carregam} — nunca
ancore em classe de CSS, posição ou texto: quebram no primeiro refactor e quem descobre
é o usuário.
**Versão:** mudou o comportamento da feature, sobe a versão do tour — ele reapresenta em
vez de ensinar o que não existe mais.

{Se não houver interface: "Não se aplica — projeto sem interface. A obrigação
equivalente é comportamento documentado."}

## Commits e revisão

**Commits:** {convenção}
**Branches:** {}
**Revisão:** {o que o revisor precisa conseguir responder}

## Antes de propor mudança estrutural

Leia `docs/PLANO-FUNDACAO.md`: lá está o que é escopo, o que foi **adiado de propósito**
e com qual gatilho revisitar. Muita coisa que parece faltar está faltando de propósito.
