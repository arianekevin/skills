export type Alvo = { caminho: string; id: string }

export type Passo = {
  tipo: 'pedido' | 'fala' | 'raciocinio' | 'comando' | 'falha'
  texto: string
  hora: string
  cmd?: string
  alerta?: { nivel: 'cuidado' | 'atencao'; motivo: string; trecho?: string }
}

/** Uma linha do painel. */
export type Item = {
  tipo: 'resumo' | 'cuidado' | 'atencao' | 'pedido' | 'aviso'
  hora: string
  texto: string
  porque?: string
  trecho?: string
}

declare module 'claude-code' {
  interface PluginState {
    vigia: {
      alvo: Shaped<Alvo | null>
      offset: Shaped<number>
      itens: Shaped<Item[]>
      pendentes: Shaped<Passo[]>
      pedido: Shaped<string>
      agora: Shaped<string>
      ultimaNovidade: Shaped<number>
    }
  }
}
