export enum TipoMovimentacao {
    ENTRADA = 'ENTRADA',
    SAIDA = 'SAIDA',
    TRANSFERENCIA = 'TRANSFERENCIA',
    AJUSTE = 'AJUSTE',
    INVENTARIO = 'INVENTARIO'
}

export enum StatusLote {
    OK = 'OK',
    ATENCAO = 'ATENCAO',
    CRITICO = 'CRITICO',
    VENCIDO = 'VENCIDO'
}

export interface Deposito {
    id: string
    nome: string
    codigo: string
    descricao?: string
    endereco?: string
    is_padrao: boolean
    ativo: boolean
    created_at: string
}

export interface Saldo {
    id: string
    produto: {
        id: string
        nome: string
        unidade_medida: string
    }
    deposito: {
        id: string
        nome: string
    }
    quantidade: number
    valor_medio: number
    valor_total: number
    updated_at: string
}

export interface Movimentacao {
    id: string
    tipo: TipoMovimentacao
    produto: {
        id: string
        nome: string
    }
    deposito_origem?: {
        id: string
        nome: string
    }
    deposito_destino?: {
        id: string
        nome: string
    }
    quantidade: number
    valor_unitario?: number
    valor_total?: number
    documento?: string
    observacao?: string
    usuario: {
        id: string
        username: string
    }
    created_at: string
}

export interface Lote {
    id: string
    codigo: string
    produto: {
        id: string
        nome: string
    }
    deposito: {
        id: string
        nome: string
    }
    quantidade_inicial: number
    quantidade_atual: number
    data_fabricacao?: string
    data_validade?: string
    status_validade: StatusLote
    valor_unitario?: number
    documento?: string
    observacao?: string
    created_at: string
}

export interface CreateDepositoDTO {
    nome: string
    codigo: string
    descricao?: string
    endereco?: string
    is_padrao?: boolean
    ativo?: boolean
}

export interface CreateMovimentacaoDTO {
    tipo: TipoMovimentacao
    produto_id: string
    deposito_origem_id?: string
    deposito_destino_id?: string
    quantidade: number
    valor_unitario?: number
    documento?: string
    observacao?: string
    lote_id?: string
}

export interface CreateLoteDTO {
    codigo: string
    produto_id: string
    deposito_id: string
    quantidade: number
    data_fabricacao?: string
    data_validade?: string
    valor_unitario?: number
    documento?: string
    observacao?: string
}

export interface StockFilters {
    produto_id?: string
    deposito_id?: string
    tipo?: TipoMovimentacao
    data_inicio?: string
    data_fim?: string
    status_validade?: StatusLote
    search?: string
    page?: number
    page_size?: number
}

export interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    page_size: number
    total_pages: number
    current_page: number
    results: T[]
}
