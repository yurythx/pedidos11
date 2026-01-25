export enum StatusVenda {
    ABERTA = 'ABERTA',
    FINALIZADA = 'FINALIZADA',
    CANCELADA = 'CANCELADA'
}

export enum FormaPagamento {
    DINHEIRO = 'DINHEIRO',
    CREDITO = 'CREDITO',
    DEBITO = 'DEBITO',
    PIX = 'PIX',
    BOLETO = 'BOLETO'
}

export interface Cliente {
    id: string
    nome: string
    cpf_cnpj?: string
    email?: string
    telefone?: string
}

export interface ItemVenda {
    id?: string
    produto: {
        id: string
        nome: string
        preco_venda: number
    }
    quantidade: number
    preco_unitario: number
    desconto: number
    valor_total: number
    observacao?: string
}

export interface Venda {
    id: string
    numero: string
    cliente?: Cliente
    status: StatusVenda
    itens: ItemVenda[]

    // Valores
    subtotal: number
    desconto_total: number
    valor_total: number

    // Pagamento
    forma_pagamento?: FormaPagamento
    parcelas?: number
    valor_pago?: number
    troco?: number

    // Datas
    data_venda: string
    data_finalizacao?: string

    // Relacionamentos
    vendedor: {
        id: string
        username: string
    }

    created_at: string
    updated_at: string
}

export interface CreateVendaDTO {
    cliente_id?: string
    observacao?: string
}

export interface AddItemVendaDTO {
    produto_id: string
    quantidade: number
    preco_unitario?: number
    desconto?: number
    observacao?: string
}

export interface FinalizarVendaDTO {
    forma_pagamento: FormaPagamento
    parcelas?: number
    valor_pago?: number
}

export interface VendaFilters {
    status?: StatusVenda
    cliente_id?: string
    data_inicio?: string
    data_fim?: string
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

// Store do Carrinho
export interface CartItem {
    produto: {
        id: string
        nome: string
        preco_venda: number
        unidade_medida: string
    }
    quantidade: number
    desconto: number
    observacao?: string
}

export interface CartState {
    items: CartItem[]
    cliente?: Cliente
    observacao?: string

    // Actions
    addItem: (produto: any, quantidade: number) => void
    updateQuantity: (produtoId: string, quantidade: number) => void
    updateDesconto: (produtoId: string, desconto: number) => void
    removeItem: (produtoId: string) => void
    setCliente: (cliente: Cliente | undefined) => void
    setObservacao: (observacao: string) => void
    clear: () => void

    // Computed
    getSubtotal: () => number
    getDescontoTotal: () => number
    getTotal: () => number
}
