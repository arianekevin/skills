import { expect, test } from 'claude-code/testing'

const pane = (bodyColumns: number) =>
  ({
    plugin: 'vigia',
    component: 'Pane',
    requestId: 'vigia',
    surface: 'terminal',
    viewport: { columns: bodyColumns, rows: 40 },
    props: {
      title: 'Vigia',
      isFocused: false,
      bodyColumns,
      placement: 'dock',
      scroll: { offset: 0, bodyRows: 36 },
      view: {},
    },
  }) as const

const passosDe = (nome: string) => [
  ...Array.from({ length: 30 }, (_, i) => ({ tipo: 'fala', hora: '08:00', texto: `${nome} antigo ${i} ` + 'x'.repeat(320) })),
  { tipo: 'comando', hora: '08:30', texto: `apaga pasta de ${nome}`, cmd: 'rm -rf src/velho', sinal: { forte: true, motivo: 'apaga arquivos', trecho: 'rm -rf src/velho' } },
]

function engine(on: any) {
  on('command.register', () => ({ value: { command: 'vigia' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.toast', () => ({ value: undefined }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('session.id', () => ({ value: 'eu' }))
  on('clock.every', () => {
    throw new Error('sem relógio no teste')
  })
  on('clock.now', () => ({ value: 1000 }))
  let n = 0
  on('model.complete', () => ({ value: { isAnswered: true, text: `{"fez":"resumo ${++n} ${'y'.repeat(150)}","porque":"plano","alerta":null}`, usage: {} } }))
  on('process.run', (_: unknown, e: { argv: string[] }) => {
    const [, , , acao, arg] = e.argv
    const nome = String(arg).includes('aaaa') ? 'ndesk' : 'bugfix'
    const out =
      acao === 'achar'
        ? { caminho: `/x/${arg}0000-1111.jsonl` }
        : acao === 'plano'
          ? { plano: 'plano' }
          : acao === 'ler'
            ? { offset: 10, passos: passosDe(nome) }
            : {}
    return { value: { exitCode: 0, stdout: JSON.stringify(out), stderr: '' } }
  })
}

test('duas sessões aparecem juntas e cada uma mostra o mais recente', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'vigia', args: 'aaaa ndesk', origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 200 } })
  await $.command.run({ command: 'vigia', args: 'bbbb bugfix', origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 200 } })

  for (const largura of [120, 60]) {
    const ui = await $.ui.mount(pane(largura))
    expect((await ui.find({ type: 'Text', text: /^ndesk · aaaa/ }))?.text).toBeTruthy()
    expect((await ui.find({ type: 'Text', text: /^bugfix · bbbb/ }))?.text).toBeTruthy()
    expect((await ui.find({ type: 'Text', text: /CUIDADO · apaga arquivos: apaga pasta de ndesk/ }))?.text).toBeTruthy()
    expect((await ui.find({ type: 'Text', text: /CUIDADO · apaga arquivos: apaga pasta de bugfix/ }))?.text).toBeTruthy()
    expect(await ui.find({ type: 'Text', text: /ndesk antigo 0 / })).toBeFalsy()
    expect((await ui.findAll({ type: 'Text' })).length).toBeLessThanOrEqual(36 + 2)
    await ui.unmount()
  }
})
