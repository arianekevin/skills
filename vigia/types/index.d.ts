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

export type Sessao = {
  id: string
  nome: string
  caminho: string
  offset: number
  itens: Item[]
  pendentes: Passo[]
  pedido: string
  agora: string
  ultimaNovidade: number
  plano: string
  falhaAberta: Falha | null
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
      sessoes: Shaped<Sessao[]>
    }
  }
}
