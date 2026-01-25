import { request } from '@/lib/http/request'
import {
    Produto,
    CreateProdutoDTO,
    ProductFilters,
    PaginatedResponse
} from '../types'

const BASE_URL = '/produtos'

export const productsApi = {
    // Listar produtos com filtros
    async list(filters?: ProductFilters): Promise<PaginatedResponse<Produto>> {
        const params = new URLSearchParams()

        if (filters?.search) params.append('search', filters.search)
        if (filters?.categoria_id) params.append('categoria', filters.categoria_id)
        if (filters?.tipo) params.append('tipo', filters.tipo)
        if (filters?.preco_min) params.append('preco_min', filters.preco_min.toString())
        if (filters?.preco_max) params.append('preco_max', filters.preco_max.toString())
        if (filters?.ativo !== undefined) params.append('ativo', filters.ativo.toString())
        if (filters?.ordering) params.append('ordering', filters.ordering)
        if (filters?.page) params.append('page', filters.page.toString())
        if (filters?.page_size) params.append('page_size', filters.page_size.toString())

        const queryString = params.toString()
        const url = queryString ? `${BASE_URL}/?${queryString}` : `${BASE_URL}/`

        return request.get<PaginatedResponse<Produto>>(url)
    },

    // Obter produto por ID
    async get(id: string): Promise<Produto> {
        return request.get<Produto>(`${BASE_URL}/${id}/`)
    },

    // Criar produto
    async create(data: CreateProdutoDTO): Promise<Produto> {
        return request.post<Produto>(`${BASE_URL}/`, data)
    },

    // Atualizar produto
    async update(id: string, data: Partial<CreateProdutoDTO>): Promise<Produto> {
        return request.put<Produto>(`${BASE_URL}/${id}/`, data)
    },

    // Deletar produto
    async delete(id: string): Promise<void> {
        return request.delete(`${BASE_URL}/${id}/`)
    },

    // Recalcular custo (para produtos compostos)
    async recalcularCusto(id: string): Promise<Produto> {
        return request.post<Produto>(`${BASE_URL}/${id}/recalcular_custo/`)
    },

    // Upload de imagem
    async uploadImage(id: string, file: File): Promise<Produto> {
        const formData = new FormData()
        formData.append('foto', file)

        return request.patch<Produto>(`${BASE_URL}/${id}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },
}
