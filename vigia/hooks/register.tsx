import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Item, Passo, Sessao } from '../types'

const PANE = 'vigia'
const script = ($: EngineInterface) => `${$.plugin.root}/bin/vigia.py`
const TICK_MS = 4000
const OCIOSO_MS = 20000
const COMANDOS_POR_BLOCO = 5
const MAX_ITENS = 200
const MAX_SESSOES = 3
const LARGURA_MINIMA_COLUNA = 45

const sessoes = atom({ plugin: 'vigia', key: 'sessoes' } as const, [], { shape: 'sessoes-1' })

const REGRAS = `Você vigia outra sessão de um agente de programação (Claude Code) e explica para a pessoa responsável, em português do Brasil, o que o agente fez num bloco de passos. Ela só quer ser chamada para o que não deveria ignorar.

Você recebe: o PLANO (documento de plano e os pedidos dela na sessão), o bloco de PASSOS, os SINAIS do bloco (ações detectadas por padrão) e, se houver, uma FALHA EM ABERTO (teste ou build vermelho ainda sem verde depois).

Responda SÓ com um JSON, sem texto em volta:
{"fez": "...", "porque": "...", "alerta": null}
ou, quando houver alerta:
{"fez": "...", "porque": "...", "alerta": {"nivel": "cuidado" | "atencao", "texto": "...", "trecho": "..."}}

- "fez": uma frase curta (até 30 palavras), linguagem comum, nome da coisa (tela, regra, recurso), não do arquivo.
- "porque": até 30 palavras. O motivo, tirado do PLANO, do PEDIDO, do RACIOCÍNIO ou da FALA. Se o passo é uma etapa do plano, diga qual. Só responda "motivo não declarado" se nem o plano explicar. Nunca invente.
- "alerta": quase sempre null. Só preencha nestes casos:
  * nivel "cuidado": uma MENSAGEM PARA OUTRA SESSÃO que muda o rumo do trabalho de lá (dá ordem nova, cancela, troca o escopo, manda apagar ou publicar). Resposta, status ou pergunta não é cuidado.
  * nivel "atencao":
    - com FALHA EM ABERTO, o agente diz que terminou, que está fechado ou passando, ou parte para a próxima etapa sem ter resolvido nem explicado a falha;
    - o agente desliga, pula, apaga ou afrouxa um teste ou verificação para ficar verde;
    - um SINAL (push, merge, tag, chamada que altera serviço externo, migration que apaga ou renomeia) que o plano e os pedidos não cobrem. Se o plano cobre (ex.: a sprint prevê migration, o fluxo é abrir PR e dar push na branch da tarefa), NÃO é alerta;
    - o agente faz o contrário de uma regra ou proibição que a pessoa escreveu.
  "texto": uma frase dizendo o que ela precisa olhar. "trecho": o trecho exato (até 200 caracteres) dos passos que motivou.
- NÃO é alerta: teste vermelho enquanto o agente ainda está corrigindo, commit, build, rebase, escolhas de implementação dentro do plano, ler ou procurar código. Na dúvida, null.`

type Resumo = { fez: string; porque: string; alerta: { nivel: 'cuidado' | 'atencao'; texto: string; trecho?: string | null } | null }

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
let deNovo = false
let cancelar: (() => void) | null = null

async function sessao($: EngineInterface, id: string): Promise<Sessao | undefined> {
  const lista: Sessao[] = await read($, sessoes)
  return lista.find(s => s.id === id)
}

async function mudar($: EngineInterface, id: string, fn: (s: Sessao) => Sessao) {
  await update($, sessoes, (l: Sessao[]) => l.map(s => (s.id === id ? fn(s) : s)))
}

async function juntar($: EngineInterface, id: string, novos: Item[]) {
  if (novos.length === 0) return
  await mudar($, id, s => ({ ...s, itens: [...s.itens, ...novos].slice(-MAX_ITENS) }))
}

async function carregarPlano($: EngineInterface, id: string, caminho: string) {
  const res = await $.process.run(['python3', '-I', script($), 'plano', caminho], { timeoutMs: 20000 })
  if (res.exitCode !== 0) return
  const r = lerJson<{ plano: string }>(res.stdout)
  if (r) await mudar($, id, s => ({ ...s, plano: r.plano }))
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
    return
  }
}

async function mostrarSinalForte($: EngineInterface, s: Sessao, p: Passo, avisar: boolean) {
  if (!p.sinal) return
  const item: Item = { tipo: 'cuidado', hora: p.hora, texto: `${p.sinal.motivo}: ${p.texto}`, trecho: p.sinal.trecho }
  await juntar($, s.id, [item])
  if (avisar) await notificar($, `Vigia ${s.nome} · CUIDADO`, item.texto)
}

async function resumir($: EngineInterface, id: string, bloco: Passo[]) {
  const s = await sessao($, id)
  if (!s || bloco.length === 0) return
  const rotulos = { pedido: 'PEDIDO', fala: 'FALA', raciocinio: 'RACIOCÍNIO', comando: 'COMANDO', falha: 'FALHA', verde: 'VERDE' }
  const linhas = bloco
    .map(p => `[${p.hora}] ${rotulos[p.tipo]}: ${p.texto}${p.cmd ? `\n   $ ${p.cmd}` : ''}`)
    .join('\n')
  const sinais = bloco
    .filter(p => p.sinal && !p.sinal.forte)
    .map(p => `- [${p.hora}] ${p.sinal!.motivo}: ${p.sinal!.trecho ?? p.cmd ?? p.texto}`)
    .join('\n')
  const falha = s.falhaAberta
  const prompt = [
    `PLANO:\n${s.plano || '(nenhum plano encontrado)'}`,
    `PEDIDO mais recente: ${s.pedido || '(não visto)'}`,
    `SINAIS:\n${sinais || '(nenhum)'}`,
    `FALHA EM ABERTO: ${falha ? `[${falha.hora}] ${falha.texto.slice(0, 300)}` : '(nenhuma)'}`,
    `PASSOS DO BLOCO:\n${linhas}`,
  ].join('\n\n')
  const hora = bloco[bloco.length - 1]?.hora || hhmm()
  const r = await $.model.complete({
    model: 'haiku',
    system: REGRAS,
    prompt,
    maxTokens: 800,
    effort: 'low',
    timeoutMs: 30000,
  })
  if (!r.isAnswered) {
    const fala = [...bloco].reverse().find(p => p.tipo === 'fala' || p.tipo === 'raciocinio')
    await juntar($, id, [{ tipo: 'resumo', hora, texto: fala?.texto.slice(0, 200) ?? `${bloco.length} passos`, porque: `(Haiku indisponível: ${r.reason})` }])
    return
  }
  const j = lerJson<Resumo>(r.text)
  if (!j) {
    await juntar($, id, [{ tipo: 'resumo', hora, texto: r.text.slice(0, 240) }])
    return
  }
  const novos: Item[] = [{ tipo: 'resumo', hora, texto: j.fez, porque: j.porque }]
  const a = j.alerta
  if (a && a.texto && (a.nivel === 'cuidado' || a.nivel === 'atencao')) {
    novos.push({ tipo: a.nivel, hora, texto: a.texto, trecho: a.trecho ?? undefined })
    if (a.nivel === 'cuidado') await notificar($, `Vigia ${s.nome} · CUIDADO`, a.texto)
  }
  await juntar($, id, novos)
}

async function fecharBloco($: EngineInterface, id: string) {
  const s = await sessao($, id)
  if (!s || s.pendentes.length === 0) return
  const bloco = s.pendentes
  await mudar($, id, x => ({ ...x, pendentes: [] }))
  await resumir($, id, bloco)
}

async function vigiarUma($: EngineInterface, id: string) {
  const s0 = await sessao($, id)
  if (!s0) return
  const off = s0.offset
  const res = await $.process.run(['python3', '-I', script($), 'ler', s0.caminho, String(off)], { timeoutMs: 20000 })
  if (res.exitCode !== 0) {
    await mudar($, id, s => ({ ...s, agora: `erro ao ler: ${res.stderr.slice(0, 160)}` }))
    return
  }
  const r = lerJson<{ offset: number; passos: Passo[]; pedido?: string }>(res.stdout)
  if (!r) return
  await mudar($, id, s => ({ ...s, offset: r.offset, pedido: r.pedido || s.pedido }))
  const relogio = await $.clock.now()

  if (r.passos.length === 0) {
    const s = await sessao($, id)
    if (s && s.pendentes.length > 0 && relogio - s.ultimaNovidade > OCIOSO_MS) await fecharBloco($, id)
    return
  }
  await mudar($, id, s => ({ ...s, ultimaNovidade: relogio }))

  for (const p of r.passos) {
    const s = await sessao($, id)
    if (!s) return
    if (p.tipo === 'pedido') {
      await fecharBloco($, id)
      await mudar($, id, x => ({ ...x, pedido: p.texto }))
      await juntar($, id, [{ tipo: 'pedido', hora: p.hora, texto: p.texto }])
      await carregarPlano($, id, s.caminho)
      continue
    }
    if (p.tipo === 'falha') await mudar($, id, x => ({ ...x, falhaAberta: { hora: p.hora, texto: p.texto } }))
    if (p.tipo === 'verde') await mudar($, id, x => ({ ...x, falhaAberta: null }))
    if (p.sinal?.forte) await mostrarSinalForte($, s, p, off >= 0)
    if (p.tipo === 'comando') await mudar($, id, x => ({ ...x, agora: `${p.hora} ${p.texto}` }))
    await mudar($, id, x => ({ ...x, pendentes: [...x.pendentes, p] }))
    const depois = await sessao($, id)
    const comandos = (depois?.pendentes ?? []).filter(x => x.tipo === 'comando').length
    const falaLonga = p.tipo === 'fala' && p.texto.length > 300
    const julgar = Boolean(p.sinal && !p.sinal.forte)
    if (comandos >= COMANDOS_POR_BLOCO || falaLonga || julgar) await fecharBloco($, id)
  }
  if (off < 0) await fecharBloco($, id)
}

async function tick($: EngineInterface) {
  if (ocupado) {
    deNovo = true
    return
  }
  ocupado = true
  try {
    const lista: Sessao[] = await read($, sessoes)
    for (const s of lista) await vigiarUma($, s.id)
  } finally {
    ocupado = false
  }
  if (deNovo) {
    deNovo = false
    await tick($)
  }
}

function ligarRelogio($: EngineInterface) {
  if (cancelar) return
  const t = $.clock.every(TICK_MS, () => tick($))
  cancelar = () => t.cancel()
}

function acharNaLista(lista: Sessao[], chave: string): Sessao | undefined {
  return lista.find(s => s.id === chave || s.nome === chave || s.id.startsWith(chave))
}

async function rodarComando($: EngineInterface, arg: string): Promise<{ text: string }> {
  ligarRelogio($)
  const [primeiro = '', ...resto] = arg.split(/\s+/).filter(Boolean)
  const lista: Sessao[] = await read($, sessoes)
  if (primeiro === 'parar') {
    if (resto.length === 0) {
      await update($, sessoes, () => [])
      return { text: 'Vigia parado.' }
    }
    const alvo = acharNaLista(lista, resto[0]!)
    if (!alvo) return { text: `Não estou vigiando ${resto[0]}.` }
    await update($, sessoes, (l: Sessao[]) => l.filter(s => s.id !== alvo.id))
    return { text: `Parei de vigiar ${alvo.nome}.` }
  }
  if (primeiro === 'limpar') {
    await update($, sessoes, (l: Sessao[]) => l.map(s => ({ ...s, itens: [] })))
    return { text: 'Painel limpo.' }
  }
  if (!primeiro) {
    const eu = await $.session.id()
    const res = await $.process.run(['python3', '-I', script($), 'listar', eu])
    if (res.exitCode !== 0) throw new Error(res.stderr.trim().split('\n').pop() || `python3 saiu com ${res.exitCode}`)
    const recentes = lerJson<{ id: string; mexida: string; ultimo_pedido: string }[]>(res.stdout) ?? []
    const vigiando = lista.length ? `Vigiando: ${lista.map(s => s.nome).join(', ')}\n\n` : ''
    if (recentes.length === 0) return { text: `${vigiando}Nenhuma sessão ativa nas últimas 6 h.` }
    return {
      text:
        vigiando +
        `Sessões ativas (use /vigia <id> [nome]; até ${MAX_SESSOES} ao mesmo tempo):\n` +
        recentes.map(s => `  ${s.id}  ${s.mexida}  ${s.ultimo_pedido || '—'}`).join('\n'),
    }
  }
  const res = await $.process.run(['python3', '-I', script($), 'achar', primeiro])
  if (res.exitCode !== 0) throw new Error(res.stderr.trim().split('\n').pop() || `python3 saiu com ${res.exitCode}`)
  const caminho = lerJson<{ caminho: string }>(res.stdout)?.caminho
  if (!caminho) return { text: `Não achei sessão com id ${primeiro}.` }
  const id = caminho.split('/').pop()!.slice(0, 8)
  const nome = resto.join(' ') || id
  const nova: Sessao = {
    id,
    nome,
    caminho,
    offset: -1,
    itens: [{ tipo: 'aviso', hora: hhmm(), texto: `vigiando a sessão ${id}` }],
    pendentes: [],
    pedido: '',
    agora: '',
    ultimaNovidade: 0,
    plano: '',
    falhaAberta: null,
  }
  const saiu = lista.filter(s => s.id !== id).length >= MAX_SESSOES ? lista.find(s => s.id !== id) : undefined
  await update($, sessoes, (l: Sessao[]) => [...l.filter(s => s.id !== id && s.id !== saiu?.id), nova])
  await carregarPlano($, id, caminho)
  const todas: Sessao[] = await read($, sessoes)
  await $.ui.open({ id: PANE, title: `Vigia · ${todas.map(s => s.nome).join(' + ')}` })
  irParaOFim($)
  void tick($)
  const aviso = saiu ? ` (parei de vigiar ${saiu.nome}: o limite é ${MAX_SESSOES})` : ''
  return { text: `Vigiando ${nome}${aviso}. Agora no painel: ${todas.map(s => s.nome).join(', ')}.` }
}

function linhasDoItem(it: Item, largura: number): number {
  const conta = (t: string) => Math.max(1, Math.ceil(t.length / Math.max(10, largura)))
  let n = conta(`${it.hora} ${it.texto.slice(0, 300)}`)
  if (it.trecho) n += conta(it.trecho.slice(0, 160))
  if (it.porque) n += conta(`   por quê: ${it.porque}`)
  return n
}

function oQueCabe(itens: Item[], largura: number, linhas: number): Item[] {
  const out: Item[] = []
  let usadas = 0
  for (let i = itens.length - 1; i >= 0; i--) {
    const it = itens[i]!
    const n = linhasDoItem(it, largura)
    if (out.length > 0 && usadas + n > linhas) break
    out.unshift(it)
    usadas += n
  }
  return out
}

function irParaOFim($: EngineInterface) {
  void $.ui.scroll({ in: PANE, to: 'end' }).catch(() => undefined)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'vigia',
      description: 'Vigia outras sessões: /vigia (lista), /vigia <id> [nome], /vigia parar [nome], /vigia limpar',
      argumentHint: '[id [nome] | parar [nome] | limpar]',
    })
    ligarRelogio($)
    const lista: Sessao[] = await read($, sessoes)
    if (lista.length) void $.ui.open({ id: PANE, title: 'Vigia' }).then(() => irParaOFim($))
    return next(e)
  })

  on('command.run', { command: 'vigia' }, async ($, e) => {
    try {
      return await rodarComando($, (e.args || '').trim())
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      return { text: `Vigia falhou: ${msg}\nPrecisa do Claude Code no terminal (CLI) e de python3 no PATH.` }
    }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const lista: Sessao[] = await read($, sessoes)
    if (lista.length === 0) return <Text bold>Vigia parado — /vigia para escolher a sessão</Text>

    const colunasTotal = e.props.bodyColumns || e.viewport?.columns || 80
    const linhasTotal = Math.max(10, (e.props.scroll?.bodyRows || e.viewport?.rows || 30) - 1)
    const ladoALado = lista.length > 1 && colunasTotal / lista.length >= LARGURA_MINIMA_COLUNA
    const umaEmbaixoDaOutra = lista.length > 1 && !ladoALado
    const largura = ladoALado ? Math.floor(colunasTotal / lista.length) - 2 : colunasTotal
    const linhasPorSessao = ladoALado ? linhasTotal : Math.floor(linhasTotal / lista.length)

    const secao = (s: Sessao) => {
      const cabecalho = 3 + (s.pedido ? 1 : 0) + (s.falhaAberta ? 1 : 0)
      const visiveis = umaEmbaixoDaOutra ? oQueCabe(s.itens, largura, Math.max(2, linhasPorSessao - cabecalho)) : s.itens
      return (
        <Box flexDirection="column" justifyContent="flex-end" width={ladoALado ? `${Math.floor(100 / lista.length)}%` : '100%'} paddingRight={ladoALado ? 1 : 0}>
          <Text bold>{s.nome === s.id ? `Vigiando ${s.id}` : `${s.nome} · ${s.id}`}</Text>
          {s.pedido ? <Text dimColor wrap="truncate-end">Pedido: {s.pedido.slice(0, 160)}</Text> : null}
          {s.falhaAberta ? <Text dimColor>teste vermelho em aberto (o agente está corrigindo)</Text> : null}
          {visiveis.length === 0 && <Text dimColor>Nada ainda.</Text>}
          {visiveis.map(it => {
            if (it.tipo === 'cuidado')
              return (
                <Box flexDirection="column">
                  <Text color="error" bold>
                    {it.hora} CUIDADO · {it.texto.slice(0, 300)}
                  </Text>
                  {it.trecho ? <Text color="error" dimColor>   "{it.trecho.slice(0, 160)}"</Text> : null}
                </Box>
              )
            if (it.tipo === 'atencao')
              return (
                <Box flexDirection="column">
                  <Text color="warning">
                    {it.hora} Atenção · {it.texto.slice(0, 300)}
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
                  {it.hora} {it.texto.slice(0, 300)}
                </Text>
                {it.porque ? <Text dimColor>   por quê: {it.porque}</Text> : null}
              </Box>
            )
          })}
          <Text dimColor wrap="truncate-end">
            agora: {s.agora || '—'}
            {s.pendentes.length ? `  (${s.pendentes.length} passos no bloco)` : ''}
          </Text>
        </Box>
      )
    }

    return <Box flexDirection={ladoALado ? 'row' : 'column'}>{lista.map(secao)}</Box>
  })
}
