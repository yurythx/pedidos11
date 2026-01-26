import { request } from '@/lib/http/request'
import { Categoria } from '../types'

const BASE_URL = '/categorias'

export const categoriesApi = {
    async list(): Promise<Categoria[]> {
        const response = await request.get<any>(`${BASE_URL}/`)
        // Se a resposta vier paginada, retorna apenas os resultados
        return Array.isArray(response) ? response : (response.results || [])
    },

    async get(id: string): Promise<Categoria> {
        return request.get<Categoria>(`${BASE_URL}/${id}/`)
    },

    async create(data: { nome: string; descricao?: string }): Promise<Categoria> {
        return request.post<Categoria>(`${BASE_URL}/`, data)
    },

    async update(id: string, data: Partial<Categoria>): Promise<Categoria> {
        return request.put<Categoria>(`${BASE_URL}/${id}/`, data)
    },

    async delete(id: string): Promise<void> {
        return request.delete(`${BASE_URL}/${id}/`)
    },
}
