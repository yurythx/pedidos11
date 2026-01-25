'use client'

import React, { useState } from 'react'
import { useContasReceber, useBaixarContaReceber } from '../hooks/useFinance'
import { StatusConta, FormaPagamentoConta } from '../types'
import { formatBRL } from '@/utils/currency'
import {
    TrendingUp,
    CheckCircle2,
    AlertCircle,
    XCircle,
    DollarSign,
    Plus,
    Filter
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function ContasReceberList() {
    const router = useRouter()
    const [filters, setFilters] = useState({
        page: 1,
        page_size: 20,
    })
    const [showBaixarModal, setShowBaixarModal] = useState<string | null>(null)

    const { data, isLoading } = useContasReceber(filters)
    const baixarMutation = useBaixarContaReceber()

    const getStatusConfig = (status: StatusConta) => {
        const configs = {
            [StatusConta.PENDENTE]: {
                label: 'Pendente',
                icon: AlertCircle,
                color: 'text-yellow-600 bg-yellow-50',
            },
            [StatusConta.PAGO]: {
                label: 'Recebido',
                icon: CheckCircle2,
                color: 'text-green-600 bg-green-50',
            },
            [StatusConta.VENCIDO]: {
                label: 'Vencido',
                icon: XCircle,
                color: 'text-red-600 bg-red-50',
            },
            [StatusConta.CANCELADO]: {
                label: 'Cancelado',
                icon: XCircle,
                color: 'text-gray-600 bg-gray-50',
            },
        }
        return configs[status]
    }

    const handleBaixar = async (id: string) => {
        try {
            await baixarMutation.mutateAsync({
                id,
                data: {
                    data_pagamento: new Date().toISOString().split('T')[0],
                    forma_pagamento: FormaPagamentoConta.DINHEIRO,
                    valor_pago: 0, // Será obtido da conta
                },
            })
            setShowBaixarModal(null)
            alert('Conta baixada com sucesso!')
        } catch (error) {
            alert('Erro ao baixar conta')
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return new Intl.DateTimeFormat('pt-BR').format(date)
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        )
    }

    const totalPendente = data?.results
        .filter(c => c.status === StatusConta.PENDENTE)
        .reduce((sum, c) => sum + c.valor, 0) || 0

    const totalVencido = data?.results
        .filter(c => c.status === StatusConta.VENCIDO)
        .reduce((sum, c) => sum + c.valor, 0) || 0

    const totalRecebido = data?.results
        .filter(c => c.status === StatusConta.PAGO)
        .reduce((sum, c) => sum + c.valor, 0) || 0

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Contas a Receber</h1>
                    <p className="text-gray-500 text-sm">{data?.count || 0} contas cadastradas</p>
                </div>
                <button
                    onClick={() => router.push('/financeiro/receber/nova')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                >
                    <Plus className="w-5 h-5" />
                    Nova Conta
                </button>
            </div>

            {/* Cards de Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <AlertCircle className="w-6 h-6 text-yellow-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">A Receber</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {formatBRL(totalPendente)}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-red-100 rounded-lg">
                            <XCircle className="w-6 h-6 text-red-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Vencido</p>
                            <p className="text-2xl font-bold text-red-600">
                                {formatBRL(totalVencido)}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <CheckCircle2 className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Recebido</p>
                            <p className="text-2xl font-bold text-green-600">
                                {formatBRL(totalRecebido)}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filtros */}
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex items-center gap-2 mb-3">
                    <Filter className="w-5 h-5 text-gray-500" />
                    <span className="font-medium text-gray-700">Filtros</span>
                </div>
                <div className="flex flex-wrap gap-2">
                    {Object.values(StatusConta).map((status) => {
                        const config = getStatusConfig(status)
                        const Icon = config.icon
                        return (
                            <button
                                key={status}
                                onClick={() => setFilters({ ...filters, status, page: 1 })}
                                className={`px-3 py-2 rounded-lg border flex items-center gap-2 text-sm ${filters.status === status
                                        ? config.color + ' border-current'
                                        : 'border-gray-200 hover:bg-gray-50'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {config.label}
                            </button>
                        )
                    })}
                    {filters.status && (
                        <button
                            onClick={() => setFilters({ ...filters, status: undefined, page: 1 })}
                            className="px-3 py-2 rounded-lg border hover:bg-gray-50 text-sm"
                        >
                            Limpar
                        </button>
                    )}
                </div>
            </div>

            {/* Tabela */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Descrição
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Cliente
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Valor
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Vencimento
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Ações
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {data?.results.map((conta) => {
                            const statusConfig = getStatusConfig(conta.status)
                            const StatusIcon = statusConfig.icon

                            return (
                                <tr key={conta.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4">
                                        <div>
                                            <p className="font-medium text-gray-800">{conta.descricao}</p>
                                            {conta.documento && (
                                                <p className="text-xs text-gray-500">Doc: {conta.documento}</p>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">
                                        {conta.cliente?.nome || '-'}
                                    </td>
                                    <td className="px-6 py-4 text-right font-semibold text-gray-800">
                                        {formatBRL(conta.valor)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-600">
                                        {formatDate(conta.data_vencimento)}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${statusConfig.color}`}>
                                            <StatusIcon className="w-4 h-4" />
                                            <span className="text-sm font-medium">{statusConfig.label}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {conta.status === StatusConta.PENDENTE && (
                                            <button
                                                onClick={() => handleBaixar(conta.id)}
                                                className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                                            >
                                                Baixar
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>

                {/* Empty State */}
                {data?.results.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhuma conta a receber encontrada</p>
                    </div>
                )}
            </div>
        </div>
    )
}
