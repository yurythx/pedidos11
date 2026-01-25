import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contasPagarApi, contasReceberApi, financeApi } from '../api/finance'
import {
    CreateContaPagarDTO,
    CreateContaReceberDTO,
    BaixarContaDTO,
    FinanceFilters
} from '../types'

// ==================== CONTAS A PAGAR ====================

const PAGAR_KEY = ['contas-pagar'] as const

export function useContasPagar(filters?: FinanceFilters) {
    return useQuery({
        queryKey: [...PAGAR_KEY, filters] as const,
        queryFn: () => contasPagarApi.list(filters),
        staleTime: 2 * 60 * 1000,
    })
}

export function useContaPagar(id: string | null) {
    return useQuery({
        queryKey: ['conta-pagar', id] as const,
        queryFn: () => contasPagarApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateContaPagar() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateContaPagarDTO) => contasPagarApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PAGAR_KEY })
            queryClient.invalidateQueries({ queryKey: ['dashboard-financeiro'] })
        },
    })
}

export function useBaixarContaPagar() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: BaixarContaDTO }) =>
            contasPagarApi.baixar(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PAGAR_KEY })
            queryClient.invalidateQueries({ queryKey: ['dashboard-financeiro'] })
        },
    })
}

export function useCancelarContaPagar() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, motivo }: { id: string; motivo?: string }) =>
            contasPagarApi.cancelar(id, motivo),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: PAGAR_KEY })
        },
    })
}

// ==================== CONTAS A RECEBER ====================

const RECEBER_KEY = ['contas-receber'] as const

export function useContasReceber(filters?: FinanceFilters) {
    return useQuery({
        queryKey: [...RECEBER_KEY, filters] as const,
        queryFn: () => contasReceberApi.list(filters),
        staleTime: 2 * 60 * 1000,
    })
}

export function useContaReceber(id: string | null) {
    return useQuery({
        queryKey: ['conta-receber', id] as const,
        queryFn: () => contasReceberApi.get(id!),
        enabled: !!id,
    })
}

export function useCreateContaReceber() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateContaReceberDTO) => contasReceberApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: RECEBER_KEY })
            queryClient.invalidateQueries({ queryKey: ['dashboard-financeiro'] })
        },
    })
}

export function useBaixarContaReceber() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: BaixarContaDTO }) =>
            contasReceberApi.baixar(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: RECEBER_KEY })
            queryClient.invalidateQueries({ queryKey: ['dashboard-financeiro'] })
        },
    })
}

export function useCancelarContaReceber() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, motivo }: { id: string; motivo?: string }) =>
            contasReceberApi.cancelar(id, motivo),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: RECEBER_KEY })
        },
    })
}

// ==================== DASHBOARD ====================

export function useDashboardFinanceiro() {
    return useQuery({
        queryKey: ['dashboard-financeiro'] as const,
        queryFn: () => financeApi.getDashboard(),
        staleTime: 1 * 60 * 1000, // 1 minuto
    })
}
