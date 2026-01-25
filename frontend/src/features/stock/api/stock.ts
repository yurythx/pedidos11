import { request } from '@/lib/http/request'
import {
    Deposito,
    Saldo,
    Movimentacao,
    Lote,
    CreateDepositoDTO,
    CreateMovimentacaoDTO,
    CreateLoteDTO,
    StockFilters,
    PaginatedResponse
} from '../types'

// ==================== DEPÓSITOS ====================

const DEPOSITOS_URL = '/depositos'

export const depositosApi = {
    async list(): Promise<Deposito[]> {
        return request.get<Deposito[]>(`${DEPOSITOS_URL}/`)
    },

    async get(id: string): Promise<Deposito> {
        return request.get<Deposito>(`${DEPOSITOS_URL}/${id}/`)
    },

    async create(data: CreateDepositoDTO): Promise<Deposito> {
        return request.post<Deposito>(`${DEPOSITOS_URL}/`, data)
    },

    async update(id: string, data: Partial<CreateDepositoDTO>): Promise<Deposito> {
        return request.put<Deposito>(`${DEPOSITOS_URL}/${id}/`, data)
    },

    async delete(id: string): Promise<void> {
        return request.delete(`${DEPOSITOS_URL}/${id}/`)
    },
}

// ==================== SALDOS ====================

const SALDOS_URL = '/saldos'

export const saldosApi = {
    async list(filters?: { deposito_id?: string; produto_id?: string }): Promise<Saldo[]> {
        const params = new URLSearchParams()
        if (filters?.deposito_id) params.append('deposito', filters.deposito_id)
        if (filters?.produto_id) params.append('produto', filters.produto_id)

        const queryString = params.toString()
        const url = queryString ? `${SALDOS_URL}/?${queryString}` : `${SALDOS_URL}/`

        return request.get<Saldo[]>(url)
    },

    async get(id: string): Promise<Saldo> {
        return request.get<Saldo>(`${SALDOS_URL}/${id}/`)
    },
}

// ==================== MOVIMENTAÇÕES ====================

const MOVIMENTACOES_URL = '/movimentacoes'

export const movimentacoesApi = {
    async list(filters?: StockFilters): Promise<PaginatedResponse<Movimentacao>> {
        const params = new URLSearchParams()

        if (filters?.produto_id) params.append('produto', filters.produto_id)
        if (filters?.deposito_id) params.append('deposito', filters.deposito_id)
        if (filters?.tipo) params.append('tipo', filters.tipo)
        if (filters?.data_inicio) params.append('data_inicio', filters.data_inicio)
        if (filters?.data_fim) params.append('data_fim', filters.data_fim)
        if (filters?.search) params.append('search', filters.search)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${MOVIMENTACOES_URL}/?${queryString}` : `${MOVIMENTACOES_URL}/`

        return request.get<PaginatedResponse<Movimentacao>>(url)
    },

    async get(id: string): Promise<Movimentacao> {
        return request.get<Movimentacao>(`${MOVIMENTACOES_URL}/${id}/`)
    },

    async create(data: CreateMovimentacaoDTO): Promise<Movimentacao> {
        return request.post<Movimentacao>(`${MOVIMENTACOES_URL}/`, data)
    },
}

// ==================== LOTES ====================

const LOTES_URL = '/lotes'

export const lotesApi = {
    async list(filters?: StockFilters): Promise<PaginatedResponse<Lote>> {
        const params = new URLSearchParams()

        if (filters?.produto_id) params.append('produto', filters.produto_id)
        if (filters?.deposito_id) params.append('deposito', filters.deposito_id)
        if (filters?.status_validade) params.append('status_validade', filters.status_validade)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${LOTES_URL}/?${queryString}` : `${LOTES_URL}/`

        return request.get<PaginatedResponse<Lote>>(url)
    },

    async get(id: string): Promise<Lote> {
        return request.get<Lote>(`${LOTES_URL}/${id}/`)
    },

    async create(data: CreateLoteDTO): Promise<Lote> {
        return request.post<Lote>(`${LOTES_URL}/`, data)
    },

    async update(id: string, data: Partial<CreateLoteDTO>): Promise<Lote> {
        return request.put<Lote>(`${LOTES_URL}/${id}/`, data)
    },

    async delete(id: string): Promise<void> {
        return request.delete(`${LOTES_URL}/${id}/`)
    },

    async vencendo(dias: number = 30, deposito_id?: string): Promise<Lote[]> {
        const params = new URLSearchParams({ dias: dias.toString() })
        if (deposito_id) params.append('deposito', deposito_id)

        return request.get<Lote[]>(`${LOTES_URL}/vencendo/?${params.toString()}`)
    },
}
