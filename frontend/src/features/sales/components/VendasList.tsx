'use client'

import React, { useState } from 'react'
import { useVendas } from '../hooks/useSales'
import { StatusVenda, FormaPagamento } from '../types'
import { formatBRL } from '@/utils/currency'
import {
    ShoppingBag,
    CheckCircle2,
    XCircle,
    Eye,
    Calendar,
    Filter,
    DollarSign
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function VendasList() {
    const router = useRouter()
    const [filters, setFilters] = useState({
        page: 1,
        page_size: 20,
    })

    const { data, isLoading } = useVendas(filters)

    const getStatusConfig = (status: StatusVenda) => {
        const configs = {
            [StatusVenda.ABERTA]: {
                label: 'Aberta',
                icon: ShoppingBag,
                color: 'text-blue-600 bg-blue-50',
            },
            [StatusVenda.FINALIZADA]: {
                label: 'Finalizada',
                icon: CheckCircle2,
                color: 'text-green-600 bg-green-50',
            },
            [StatusVenda.CANCELADA]: {
                label: 'Cancelada',
                icon: XCircle,
                color: 'text-red-600 bg-red-50',
            },
        }
        return configs[status]
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        }).format(date)
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Vendas</h1>
                    <p className="text-gray-500 text-sm">{data?.count || 0} vendas registradas</p>
                </div>
                <button
                    onClick={() => router.push('/pdv')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                >
                    <ShoppingBag className="w-5 h-5" />
                    Nova Venda
                </button>
            </div>

            {/* Filtros Rápidos */}
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex items-center gap-2 mb-3">
                    <Filter className="w-5 h-5 text-gray-500" />
                    <span className="font-medium text-gray-700">Filtros</span>
                </div>
                <div className="flex flex-wrap gap-2">
                    {Object.values(StatusVenda).map((status) => {
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

            {/* Cards de Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <CheckCircle2 className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Vendas Finalizadas</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {data?.results.filter(v => v.status === StatusVenda.FINALIZADA).length || 0}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <ShoppingBag className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Vendas Abertas</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {data?.results.filter(v => v.status === StatusVenda.ABERTA).length || 0}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-purple-100 rounded-lg">
                            <DollarSign className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Valor Total</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {formatBRL(
                                    data?.results
                                        .filter(v => v.status === StatusVenda.FINALIZADA)
                                        .reduce((sum, v) => sum + v.valor_total, 0) || 0
                                )}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabela */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Número
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Cliente
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Itens
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Valor
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Pagamento
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Data
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Ações
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {data?.results.map((venda) => {
                            const statusConfig = getStatusConfig(venda.status)
                            const StatusIcon = statusConfig.icon

                            return (
                                <tr key={venda.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 font-medium text-gray-800">
                                        #{venda.numero}
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">
                                        {venda.cliente?.nome || 'Sem cliente'}
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">
                                        {venda.itens.length} item(ns)
                                    </td>
                                    <td className="px-6 py-4 text-right font-semibold text-gray-800">
                                        {formatBRL(venda.valor_total)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-600">
                                        {venda.forma_pagamento || '-'}
                                        {venda.parcelas && venda.parcelas > 1 && ` (${venda.parcelas}x)`}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${statusConfig.color}`}>
                                            <StatusIcon className="w-4 h-4" />
                                            <span className="text-sm font-medium">{statusConfig.label}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-600">
                                        {formatDate(venda.data_venda)}
                                    </td>
                                    <td className="px-6 py-4">
                                        <button
                                            onClick={() => router.push(`/vendas/${venda.id}`)}
                                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                                            title="Ver detalhes"
                                        >
                                            <Eye className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>

                {/* Empty State */}
                {data?.results.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhuma venda encontrada</p>
                        <p className="text-sm">Faça sua primeira venda no PDV</p>
                    </div>
                )}
            </div>

            {/* Paginação */}
            {data && data.total_pages > 1 && (
                <div className="flex justify-center gap-2">
                    <button
                        onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                        disabled={!data.previous}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                        Anterior
                    </button>
                    <span className="px-4 py-2">
                        Página {data.current_page} de {data.total_pages}
                    </span>
                    <button
                        onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                        disabled={!data.next}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                        Próxima
                    </button>
                </div>
            )}
        </div>
    )
}
