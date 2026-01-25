import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { categoriesApi } from '../api/categories'
import { Categoria } from '../types'

const QUERY_KEYS = {
    categories: ['categories'] as const,
    category: (id: string) => ['category', id] as const,
}

export function useCategories() {
    return useQuery({
        queryKey: QUERY_KEYS.categories,
        queryFn: () => categoriesApi.list(),
        staleTime: 10 * 60 * 1000, // 10 minutos
    })
}

export function useCategory(id: string | null) {
    return useQuery({
        queryKey: QUERY_KEYS.category(id!),
        queryFn: () => categoriesApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateCategory() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: { nome: string; descricao?: string }) => categoriesApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.categories })
        },
    })
}

export function useUpdateCategory() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Categoria> }) =>
            categoriesApi.update(id, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.categories })
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.category(variables.id) })
        },
    })
}

export function useDeleteCategory() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => categoriesApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.categories })
        },
    })
}
