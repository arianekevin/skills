export type Alvo = { caminho: string; id: string }

export type Passo = {
  tipo: 'pedido' | 'fala' | 'raciocinio' | 'comando' | 'falha' | 'verde'
  texto: string
  hora: string
  cmd?: string
  sinal?: Sinal
}

export type Sinal = { forte: boolean; motivo: string; trecho?: string; mensagem?: boolean }

export type Falha = { hora: string; texto: string }

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
      plano: Shaped<string>
      falhaAberta: Shaped<Falha | null>
    }
  }
}
