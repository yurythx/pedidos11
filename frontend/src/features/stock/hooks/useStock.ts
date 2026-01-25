import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { depositosApi, saldosApi, movimentacoesApi, lotesApi } from '../api/stock'
import {
    CreateDepositoDTO,
    CreateMovimentacaoDTO,
    CreateLoteDTO,
    StockFilters
} from '../types'

// ==================== DEPÓSITOS ====================

const DEPOSITOS_KEY = ['depositos'] as const

export function useDepositos() {
    return useQuery({
        queryKey: DEPOSITOS_KEY,
        queryFn: () => depositosApi.list(),
        staleTime: 10 * 60 * 1000, // 10 minutos
    })
}

export function useDeposito(id: string | null) {
    return useQuery({
        queryKey: ['deposito', id] as const,
        queryFn: () => depositosApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateDeposito() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateDepositoDTO) => depositosApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: DEPOSITOS_KEY })
        },
    })
}

export function useUpdateDeposito() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<CreateDepositoDTO> }) =>
            depositosApi.update(id, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: DEPOSITOS_KEY })
            queryClient.invalidateQueries({ queryKey: ['deposito', variables.id] })
        },
    })
}

export function useDeleteDeposito() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => depositosApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: DEPOSITOS_KEY })
        },
    })
}

// ==================== SALDOS ====================

export function useSaldos(filters?: { deposito_id?: string; produto_id?: string }) {
    return useQuery({
        queryKey: ['saldos', filters] as const,
        queryFn: () => saldosApi.list(filters),
        staleTime: 2 * 60 * 1000, // 2 minutos
    })
}

// ==================== MOVIMENTAÇÕES ====================

export function useMovimentacoes(filters?: StockFilters) {
    return useQuery({
        queryKey: ['movimentacoes', filters] as const,
        queryFn: () => movimentacoesApi.list(filters),
        staleTime: 1 * 60 * 1000, // 1 minuto
    })
}

export function useMovimentacao(id: string | null) {
    return useQuery({
        queryKey: ['movimentacao', id] as const,
        queryFn: () => movimentacoesApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateMovimentacao() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateMovimentacaoDTO) => movimentacoesApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['movimentacoes'] })
            queryClient.invalidateQueries({ queryKey: ['saldos'] })
            queryClient.invalidateQueries({ queryKey: ['lotes'] })
        },
    })
}

// ==================== LOTES ====================

export function useLotes(filters?: StockFilters) {
    return useQuery({
        queryKey: ['lotes', filters] as const,
        queryFn: () => lotesApi.list(filters),
        staleTime: 5 * 60 * 1000, // 5 minutos
    })
}

export function useLote(id: string | null) {
    return useQuery({
        queryKey: ['lote', id] as const,
        queryFn: () => lotesApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateLote() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateLoteDTO) => lotesApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['lotes'] })
        },
    })
}

export function useUpdateLote() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<CreateLoteDTO> }) =>
            lotesApi.update(id, data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['lotes'] })
            queryClient.invalidateQueries({ queryKey: ['lote', variables.id] })
        },
    })
}

export function useDeleteLote() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => lotesApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['lotes'] })
        },
    })
}

export function useLotesVencendo(dias: number = 30, deposito_id?: string) {
    return useQuery({
        queryKey: ['lotes-vencendo', dias, deposito_id] as const,
        queryFn: () => lotesApi.vencendo(dias, deposito_id),
        staleTime: 5 * 60 * 1000, // 5 minutos
    })
}
