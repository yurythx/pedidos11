import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vendasApi } from '../api/sales'
import { CreateVendaDTO, AddItemVendaDTO, FinalizarVendaDTO, VendaFilters } from '../types'

const VENDAS_KEY = ['vendas'] as const

export function useVendas(filters?: VendaFilters) {
    return useQuery({
        queryKey: [...VENDAS_KEY, filters] as const,
        queryFn: () => vendasApi.list(filters),
        staleTime: 1 * 60 * 1000, // 1 minuto
    })
}

export function useVenda(id: string | null) {
    return useQuery({
        queryKey: ['venda', id] as const,
        queryFn: () => vendasApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateVendaDTO) => vendasApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
        },
    })
}

export function useAddItemVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ vendaId, data }: { vendaId: string; data: AddItemVendaDTO }) =>
            vendasApi.addItem(vendaId, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
            queryClient.invalidateQueries({ queryKey: ['venda', variables.vendaId] })
        },
    })
}

export function useRemoveItemVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ vendaId, itemId }: { vendaId: string; itemId: string }) =>
            vendasApi.removeItem(vendaId, itemId),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
            queryClient.invalidateQueries({ queryKey: ['venda', variables.vendaId] })
        },
    })
}

export function useFinalizarVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ vendaId, data }: { vendaId: string; data: FinalizarVendaDTO }) =>
            vendasApi.finalizar(vendaId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
        },
    })
}

export function useCancelarVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ vendaId, motivo }: { vendaId: string; motivo?: string }) =>
            vendasApi.cancelar(vendaId, motivo),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
        },
    })
}

export function useReabrirVenda() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (vendaId: string) => vendasApi.reabrir(vendaId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: VENDAS_KEY })
        },
    })
}
