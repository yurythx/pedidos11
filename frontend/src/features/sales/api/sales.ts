import { request } from '@/lib/http/request'
import {
    Venda,
    CreateVendaDTO,
    AddItemVendaDTO,
    FinalizarVendaDTO,
    VendaFilters,
    PaginatedResponse
} from '../types'

const BASE_URL = '/vendas'

export const vendasApi = {
    // Listar vendas
    async list(filters?: VendaFilters): Promise<PaginatedResponse<Venda>> {
        const params = new URLSearchParams()

        if (filters?.status) params.append('status', filters.status)
        if (filters?.cliente_id) params.append('cliente', filters.cliente_id)
        if (filters?.data_inicio) params.append('data_inicio', filters.data_inicio)
        if (filters?.data_fim) params.append('data_fim', filters.data_fim)
        if (filters?.search) params.append('search', filters.search)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${BASE_URL}/?${queryString}` : `${BASE_URL}/`

        return request.get<PaginatedResponse<Venda>>(url)
    },

    // Obter venda por ID
    async get(id: string): Promise<Venda> {
        return request.get<Venda>(`${BASE_URL}/${id}/`)
    },

    // Criar nova venda
    async create(data: CreateVendaDTO): Promise<Venda> {
        return request.post<Venda>(`${BASE_URL}/`, data)
    },

    // Adicionar item à venda
    async addItem(vendaId: string, data: AddItemVendaDTO): Promise<Venda> {
        return request.post<Venda>(`${BASE_URL}/${vendaId}/adicionar_item/`, data)
    },

    // Remover item da venda
    async removeItem(vendaId: string, itemId: string): Promise<Venda> {
        return request.delete<Venda>(`${BASE_URL}/${vendaId}/remover_item/${itemId}/`)
    },

    // Atualizar quantidade do item
    async updateItem(vendaId: string, itemId: string, data: Partial<AddItemVendaDTO>): Promise<Venda> {
        return request.patch<Venda>(`${BASE_URL}/${vendaId}/atualizar_item/${itemId}/`, data)
    },

    // Finalizar venda
    async finalizar(vendaId: string, data: FinalizarVendaDTO): Promise<Venda> {
        return request.post<Venda>(`${BASE_URL}/${vendaId}/finalizar/`, data)
    },

    // Cancelar venda
    async cancelar(vendaId: string, motivo?: string): Promise<Venda> {
        return request.post<Venda>(`${BASE_URL}/${vendaId}/cancelar/`, { motivo })
    },

    // Reabrir venda
    async reabrir(vendaId: string): Promise<Venda> {
        return request.post<Venda>(`${BASE_URL}/${vendaId}/reabrir/`)
    },
}
