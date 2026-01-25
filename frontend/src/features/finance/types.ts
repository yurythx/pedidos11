export enum TipoConta {
    RECEBER = 'RECEBER',
    PAGAR = 'PAGAR'
}

export enum StatusConta {
    PENDENTE = 'PENDENTE',
    PAGO = 'PAGO',
    VENCIDO = 'VENCIDO',
    CANCELADO = 'CANCELADO'
}

export enum FormaPagamentoConta {
    DINHEIRO = 'DINHEIRO',
    TRANSFERENCIA = 'TRANSFERENCIA',
    BOLETO = 'BOLETO',
    CARTAO = 'CARTAO',
    PIX = 'PIX',
    CHEQUE = 'CHEQUE'
}

export interface ContaPagar {
    id: string
    descricao: string
    fornecedor?: {
        id: string
        nome: string
    }
    valor: number
    data_emissao: string
    data_vencimento: string
    data_pagamento?: string
    status: StatusConta
    forma_pagamento?: FormaPagamentoConta
    observacao?: string
    documento?: string
    created_at: string
}

export interface ContaReceber {
    id: string
    descricao: string
    cliente?: {
        id: string
        nome: string
    }
    venda?: {
        id: string
        numero: string
    }
    valor: number
    data_emissao: string
    data_vencimento: string
    data_recebimento?: string
    status: StatusConta
    forma_pagamento?: FormaPagamentoConta
    observacao?: string
    documento?: string
    created_at: string
}

export interface CreateContaPagarDTO {
    descricao: string
    fornecedor_id?: string
    valor: number
    data_emissao: string
    data_vencimento: string
    observacao?: string
    documento?: string
}

export interface CreateContaReceberDTO {
    descricao: string
    cliente_id?: string
    venda_id?: string
    valor: number
    data_emissao: string
    data_vencimento: string
    observacao?: string
    documento?: string
}

export interface BaixarContaDTO {
    data_pagamento: string
    forma_pagamento: FormaPagamentoConta
    valor_pago: number
    observacao?: string
}

export interface FinanceFilters {
    status?: StatusConta
    data_inicio?: string
    data_fim?: string
    vencimento_inicio?: string
    vencimento_fim?: string
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

export interface DashboardFinanceiro {
    // Contas a Receber
    total_a_receber: number
    recebido_hoje: number
    recebido_mes: number
    vencidas_receber: number

    // Contas a Pagar
    total_a_pagar: number
    pago_hoje: number
    pago_mes: number
    vencidas_pagar: number

    // Saldo
    saldo_mes: number
    saldo_geral: number
}
