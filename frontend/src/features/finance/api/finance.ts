import { request } from '@/lib/http/request'
import {
    ContaPagar,
    ContaReceber,
    CreateContaPagarDTO,
    CreateContaReceberDTO,
    BaixarContaDTO,
    FinanceFilters,
    PaginatedResponse,
    DashboardFinanceiro
} from '../types'

// ==================== CONTAS A PAGAR ====================

const PAGAR_URL = '/contas-pagar'

export const contasPagarApi = {
    async list(filters?: FinanceFilters): Promise<PaginatedResponse<ContaPagar>> {
        const params = new URLSearchParams()

        if (filters?.status) params.append('status', filters.status)
        if (filters?.data_inicio) params.append('data_inicio', filters.data_inicio)
        if (filters?.data_fim) params.append('data_fim', filters.data_fim)
        if (filters?.vencimento_inicio) params.append('vencimento_inicio', filters.vencimento_inicio)
        if (filters?.vencimento_fim) params.append('vencimento_fim', filters.vencimento_fim)
        if (filters?.search) params.append('search', filters.search)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${PAGAR_URL}/?${queryString}` : `${PAGAR_URL}/`

        return request.get<PaginatedResponse<ContaPagar>>(url)
    },

    async get(id: string): Promise<ContaPagar> {
        return request.get<ContaPagar>(`${PAGAR_URL}/${id}/`)
    },

    async create(data: CreateContaPagarDTO): Promise<ContaPagar> {
        return request.post<ContaPagar>(`${PAGAR_URL}/`, data)
    },

    async update(id: string, data: Partial<CreateContaPagarDTO>): Promise<ContaPagar> {
        return request.put<ContaPagar>(`${PAGAR_URL}/${id}/`, data)
    },

    async delete(id: string): Promise<void> {
        return request.delete(`${PAGAR_URL}/${id}/`)
    },

    async baixar(id: string, data: BaixarContaDTO): Promise<ContaPagar> {
        return request.post<ContaPagar>(`${PAGAR_URL}/${id}/baixar/`, data)
    },

    async cancelar(id: string, motivo?: string): Promise<ContaPagar> {
        return request.post<ContaPagar>(`${PAGAR_URL}/${id}/cancelar/`, { motivo })
    },
}

// ==================== CONTAS A RECEBER ====================

const RECEBER_URL = '/contas-receber'

export const contasReceberApi = {
    async list(filters?: FinanceFilters): Promise<PaginatedResponse<ContaReceber>> {
        const params = new URLSearchParams()

        if (filters?.status) params.append('status', filters.status)
        if (filters?.data_inicio) params.append('data_inicio', filters.data_inicio)
        if (filters?.data_fim) params.append('data_fim', filters.data_fim)
        if (filters?.vencimento_inicio) params.append('vencimento_inicio', filters.vencimento_inicio)
        if (filters?.vencimento_fim) params.append('vencimento_fim', filters.vencimento_fim)
        if (filters?.search) params.append('search', filters.search)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${RECEBER_URL}/?${queryString}` : `${RECEBER_URL}/`

        return request.get<PaginatedResponse<ContaReceber>>(url)
    },

    async get(id: string): Promise<ContaReceber> {
        return request.get<ContaReceber>(`${RECEBER_URL}/${id}/`)
    },

    async create(data: CreateContaReceberDTO): Promise<ContaReceber> {
        return request.post<ContaReceber>(`${RECEBER_URL}/`, data)
    },

    async update(id: string, data: Partial<CreateContaReceberDTO>): Promise<ContaReceber> {
        return request.put<ContaReceber>(`${RECEBER_URL}/${id}/`, data)
    },

    async delete(id: string): Promise<void> {
        return request.delete(`${RECEBER_URL}/${id}/`)
    },

    async baixar(id: string, data: BaixarContaDTO): Promise<ContaReceber> {
        return request.post<ContaReceber>(`${RECEBER_URL}/${id}/baixar/`, data)
    },

    async cancelar(id: string, motivo?: string): Promise<ContaReceber> {
        return request.post<ContaReceber>(`${RECEBER_URL}/${id}/cancelar/`, { motivo })
    },
}

// ==================== DASHBOARD ====================

export const financeApi = {
    async getDashboard(): Promise<DashboardFinanceiro> {
        return request.get<DashboardFinanceiro>('/financeiro/dashboard/')
    },
}
