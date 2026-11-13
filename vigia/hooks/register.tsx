import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Alvo, Item, Passo } from '../types'

// Vigia: acompanha outra sessão do Claude Code pelo histórico (.jsonl) dela.
// O script lê e marca os alertas por padrão (sem IA); o Haiku resume cada bloco
// (o que fez, por quê, e CUIDADO quando é decisão séria).

const PANE = 'vigia'
const script = ($: EngineInterface) => `${$.plugin.root}/bin/vigia.py`
const TICK_MS = 4000
const OCIOSO_MS = 20000 // sem passo novo por 20 s fecha o bloco
const COMANDOS_POR_BLOCO = 5
const MAX_ITENS = 200

const alvo = atom({ plugin: 'vigia', key: 'alvo' } as const, null, { shape: 'alvo-1' })
const offset = atom({ plugin: 'vigia', key: 'offset' } as const, -1, { shape: 'offset-1' })
const itens = atom({ plugin: 'vigia', key: 'itens' } as const, [], { shape: 'itens-1' })
const pendentes = atom({ plugin: 'vigia', key: 'pendentes' } as const, [], { shape: 'pendentes-1' })
const pedido = atom({ plugin: 'vigia', key: 'pedido' } as const, '', { shape: 'pedido-1' })
const agora = atom({ plugin: 'vigia', key: 'agora' } as const, '', { shape: 'agora-1' })
const ultimaNovidade = atom({ plugin: 'vigia', key: 'ultimaNovidade' } as const, 0, { shape: 'un-1' })

const REGRAS = `Você vigia outra sessão de um agente de programação (Claude Code) e explica para quem é responsável pelo projeto, em português do Brasil, o que o agente fez num bloco de passos.

Responda SÓ com um JSON, sem texto em volta:
{"fez": "...", "porque": "...", "cuidado": null, "trecho": null}

- "fez": uma frase curta, linguagem comum, nome da coisa (tela, regra, recurso), não do arquivo. Sem jargão desnecessário.
- "porque": o motivo, tirado do PEDIDO dessa pessoa, do RACIOCÍNIO ou da FALA do agente. Cite ou parafraseie de perto. Se nenhum motivo estiver escrito, responda exatamente "motivo não declarado". Nunca invente motivo.
- "cuidado": preencha SÓ quando houver decisão séria que merece que ela pare e olhar:
  * o agente escolheu sozinho um caminho de arquitetura ou de regra de negócio que o pedido não pediu;
  * foi além do escopo do pedido ou mudou comportamento que já existia;
  * mandou dado de cliente para um serviço de IA externo, ou contrariou uma regra que ela deu.
  Uma frase dizendo qual é a decisão. Caso contrário, null. Na dúvida entre séria e normal, prefira marcar.
- "trecho": quando "cuidado" vier preenchido, o trecho exato (até 200 caracteres) dos passos que motivou. Senão null.

Commit, push, build e teste NÃO são assunto seu: outro sistema já alerta sobre isso.`

type Resumo = { fez: string; porque: string; cuidado: string | null; trecho: string | null }

function hhmm(): string {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function lerJson<T>(texto: string): T | null {
  try {
    return JSON.parse(texto) as T
  } catch {
    const i = texto.indexOf('{')
    const j = texto.lastIndexOf('}')
    if (i >= 0 && j > i) {
      try {
        return JSON.parse(texto.slice(i, j + 1)) as T
      } catch {
        return null
      }
    }
    return null
  }
}

let ocupado = false
let cancelar: (() => void) | null = null

async function juntar($: EngineInterface, novos: Item[]) {
  if (novos.length === 0) return
  await update($, itens, (l: Item[]) => [...l, ...novos].slice(-MAX_ITENS))
}

async function notificar($: EngineInterface, titulo: string, texto: string) {
  $.ui.toast(`${titulo}: ${texto}`)
  const limpo = (s: string) => s.replace(/["\\]/g, "'").slice(0, 220)
  try {
    await $.process.run([
      'osascript',
      '-e',
      `display notification "${limpo(texto)}" with title "${limpo(titulo)}" sound name "Basso"`,
    ])
  } catch {
    // sem notificação do Mac, fica o toast e o painel
  }
}

async function resumir($: EngineInterface, bloco: Passo[]) {
  if (bloco.length === 0) return
  const ped = await read($, pedido)
  const linhas = bloco
    .map(p => {
      const rot = { pedido: 'PEDIDO', fala: 'FALA', raciocinio: 'RACIOCÍNIO', comando: 'COMANDO', falha: 'FALHA' }[p.tipo]
      return `[${p.hora}] ${rot}: ${p.texto}${p.cmd ? `\n   $ ${p.cmd}` : ''}`
    })
    .join('\n')
  const prompt = `PEDIDO mais recente da pessoa: ${ped || '(não visto)'}\n\nPASSOS DO BLOCO:\n${linhas}`
  const hora = bloco[bloco.length - 1]?.hora || hhmm()
  const r = await $.model.complete({
    model: 'haiku',
    system: REGRAS,
    prompt,
    maxTokens: 400,
    effort: 'low',
    timeoutMs: 30000,
  })
  if (!r.isAnswered) {
    // sem resumo, mostra o que o próprio agente escreveu
    const fala = [...bloco].reverse().find(p => p.tipo === 'fala' || p.tipo === 'raciocinio')
    await juntar($, [{ tipo: 'resumo', hora, texto: fala?.texto.slice(0, 200) ?? `${bloco.length} passos`, porque: `(Haiku indisponível: ${r.reason})` }])
    return
  }
  const j = lerJson<Resumo>(r.text)
  if (!j) {
    await juntar($, [{ tipo: 'resumo', hora, texto: r.text.slice(0, 240) }])
    return
  }
  const novos: Item[] = [{ tipo: 'resumo', hora, texto: j.fez, porque: j.porque }]
  if (j.cuidado) {
    novos.push({ tipo: 'cuidado', hora, texto: j.cuidado, trecho: j.trecho ?? undefined, porque: 'decisão (Haiku)' })
    await notificar($, 'Vigia · CUIDADO', j.cuidado)
  }
  await juntar($, novos)
}

async function fecharBloco($: EngineInterface) {
  const bloco = await read($, pendentes)
  if (bloco.length === 0) return
  await update($, pendentes, () => [])
  await resumir($, bloco)
}

async function tick($: EngineInterface) {
  if (ocupado) return
  const a: Alvo | null = await read($, alvo)
  if (!a) return
  ocupado = true
  try {
    const off = await read($, offset)
    const res = await $.process.run(['python3', '-I', script($), 'ler', a.caminho, String(off)], { timeoutMs: 20000 })
    if (res.exitCode !== 0) {
      await update($, agora, () => `erro ao ler: ${res.stderr.slice(0, 160)}`)
      return
    }
    const r = lerJson<{ offset: number; passos: Passo[]; pedido?: string }>(res.stdout)
    if (!r) return
    await update($, offset, () => r.offset)
    if (r.pedido) await update($, pedido, () => r.pedido as string)
    const relogio = await $.clock.now()

    if (r.passos.length === 0) {
      const pend = await read($, pendentes)
      if (pend.length > 0 && relogio - (await read($, ultimaNovidade)) > OCIOSO_MS) await fecharBloco($)
      return
    }
    await update($, ultimaNovidade, () => relogio)

    for (const p of r.passos) {
      if (p.tipo === 'pedido') {
        await fecharBloco($)
        await update($, pedido, () => p.texto)
        await juntar($, [{ tipo: 'pedido', hora: p.hora, texto: p.texto }])
        continue
      }
      if (p.alerta) {
        const item: Item = {
          tipo: p.alerta.nivel === 'cuidado' ? 'cuidado' : 'atencao',
          hora: p.hora,
          texto: `${p.alerta.motivo}: ${p.texto}`,
          trecho: p.alerta.trecho ?? (p.tipo === 'falha' ? p.texto.slice(0, 200) : undefined),
        }
        if (p.tipo === 'falha') item.texto = 'falha ou teste vermelho'
        await juntar($, [item])
        if (p.alerta.nivel === 'cuidado' && off >= 0) await notificar($, 'Vigia · CUIDADO', item.texto)
      }
      if (p.tipo === 'comando') await update($, agora, () => `${p.hora} ${p.texto}`)
      await update($, pendentes, (l: Passo[]) => [...l, p])
      const pend: Passo[] = await read($, pendentes)
      const comandos = pend.filter(x => x.tipo === 'comando').length
      const falaLonga = p.tipo === 'fala' && p.texto.length > 300
      if (comandos >= COMANDOS_POR_BLOCO || falaLonga) await fecharBloco($)
    }
    if (off < 0) await fecharBloco($) // primeira leitura: um resumo de "onde ela está"
  } finally {
    ocupado = false
  }
}

function ligarRelogio($: EngineInterface) {
  if (cancelar) return
  const t = $.clock.every(TICK_MS, () => tick($))
  cancelar = () => t.cancel()
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'vigia',
      description: 'Vigia outra sessão: /vigia (lista), /vigia <id>, /vigia parar, /vigia limpar',
      argumentHint: '[id | parar | limpar]',
    })
    ligarRelogio($)
    if (await read($, alvo)) void $.ui.open({ id: PANE, title: 'Vigia' })
    return next(e)
  })

  on('command.run', { command: 'vigia' }, async ($, e) => {
    ligarRelogio($)
    const arg = (e.args || '').trim()
    if (arg === 'parar') {
      await update($, alvo, () => null)
      await update($, pendentes, () => [])
      return { text: 'Vigia parado.' }
    }
    if (arg === 'limpar') {
      await update($, itens, () => [])
      return { text: 'Painel limpo.' }
    }
    if (!arg) {
      const eu = await $.session.id()
      const res = await $.process.run(['python3', '-I', script($), 'listar', eu])
      const lista = lerJson<{ id: string; mexida: string; ultimo_pedido: string }[]>(res.stdout) ?? []
      if (lista.length === 0) return { text: 'Nenhuma sessão ativa nas últimas 6 h.' }
      return {
        text:
          'Sessões ativas (use /vigia <id>):\n' +
          lista.map(s => `  ${s.id}  ${s.mexida}  ${s.ultimo_pedido || '—'}`).join('\n'),
      }
    }
    const res = await $.process.run(['python3', '-I', script($), 'achar', arg])
    const caminho = lerJson<{ caminho: string }>(res.stdout)?.caminho
    if (!caminho) return { text: `Não achei sessão com id ${arg}.` }
    const id = caminho.split('/').pop()!.slice(0, 8)
    await update($, alvo, () => ({ caminho, id }))
    await update($, offset, () => -1)
    await update($, pendentes, () => [])
    await update($, pedido, () => '')
    await update($, agora, () => '')
    await juntar($, [{ tipo: 'aviso', hora: hhmm(), texto: `vigiando a sessão ${id}` }])
    await $.ui.open({ id: PANE, title: `Vigia · ${id}` })
    void tick($)
    return { text: `Vigiando ${id}. O painel resume cada bloco; CUIDADO vira notificação no Mac.` }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const a: Alvo | null = await read($, alvo)
    const lista: Item[] = await read($, itens)
    const ped: string = await read($, pedido)
    const ag: string = await read($, agora)
    const pend: Passo[] = await read($, pendentes)
    const linhas = Math.max(4, (e.viewport?.rows ?? 30) - 7)
    const visiveis = lista.slice(-Math.max(3, Math.floor(linhas / 2)))

    return (
      <Box flexDirection="column">
        <Text bold>{a ? `Vigiando ${a.id}` : 'Vigia parado — /vigia para escolher a sessão'}</Text>
        {ped ? <Text dimColor>Pedido: {ped.slice(0, 160)}</Text> : null}
        <Text dimColor> </Text>
        {visiveis.length === 0 && <Text dimColor>Nada ainda.</Text>}
        {visiveis.map(it => {
          if (it.tipo === 'cuidado')
            return (
              <Box flexDirection="column">
                <Text color="error" bold>
                  {it.hora} CUIDADO · {it.texto}
                </Text>
                {it.trecho ? <Text color="error" dimColor>   "{it.trecho}"</Text> : null}
              </Box>
            )
          if (it.tipo === 'atencao')
            return (
              <Box flexDirection="column">
                <Text color="warning">
                  {it.hora} Atenção · {it.texto}
                </Text>
                {it.trecho ? <Text dimColor>   {it.trecho.slice(0, 160)}</Text> : null}
              </Box>
            )
          if (it.tipo === 'pedido')
            return (
              <Text color="suggestion">
                {it.hora} Você pediu: {it.texto.slice(0, 200)}
              </Text>
            )
          if (it.tipo === 'aviso') return <Text dimColor>{it.hora} {it.texto}</Text>
          return (
            <Box flexDirection="column">
              <Text>
                {it.hora} {it.texto}
              </Text>
              {it.porque ? <Text dimColor>   por quê: {it.porque}</Text> : null}
            </Box>
          )
        })}
        <Text dimColor> </Text>
        {a ? (
          <Text dimColor>
            agora: {ag || '—'}
            {pend.length ? `  (${pend.length} passos no bloco)` : ''}
          </Text>
        ) : null}
      </Box>
    )
  })
}
