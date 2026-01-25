import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { productsApi } from '../api/products'
import { CreateProdutoDTO, ProductFilters } from '../types'

const QUERY_KEYS = {
    products: (filters?: ProductFilters) => ['products', filters] as const,
    product: (id: string) => ['product', id] as const,
}

export function useProducts(filters?: ProductFilters) {
    return useQuery({
        queryKey: QUERY_KEYS.products(filters),
        queryFn: () => productsApi.list(filters),
        staleTime: 5 * 60 * 1000, // 5 minutos
    })
}

export function useProduct(id: string | null) {
    return useQuery({
        queryKey: QUERY_KEYS.product(id!),
        queryFn: () => productsApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateProduct() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateProdutoDTO) => productsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] })
        },
    })
}

export function useUpdateProduct() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<CreateProdutoDTO> }) =>
            productsApi.update(id, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['products'] })
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.product(variables.id) })
        },
    })
}

export function useDeleteProduct() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => productsApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] })
        },
    })
}

export function useRecalcularCusto() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => productsApi.recalcularCusto(id),
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.product(id) })
        },
    })
}
