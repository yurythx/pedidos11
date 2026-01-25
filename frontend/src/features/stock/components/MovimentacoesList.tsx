'use client'

import React, { useState } from 'react'
import { useMovimentacoes } from '../hooks/useStock'
import { useDepositos } from '../hooks/useStock'
import { useProducts } from '@/features/catalog/hooks/useProducts'
import { TipoMovimentacao } from '../types'
import { formatBRL } from '@/utils/currency'
import {
    ArrowDownCircle,
    ArrowUpCircle,
    ArrowRightLeft,
    Settings,
    Plus,
    Calendar,
    Filter
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function MovimentacoesList() {
    const router = useRouter()
    const [filters, setFilters] = useState({
        page: 1,
        page_size: 20,
    })

    const { data, isLoading } = useMovimentacoes(filters)
    const { data: depositos } = useDepositos()
    const { data: produtosData } = useProducts({ page_size: 1000 })

    const getTipoConfig = (tipo: TipoMovimentacao) => {
        const configs = {
            [TipoMovimentacao.ENTRADA]: {
                label: 'Entrada',
                icon: ArrowDownCircle,
                color: 'text-green-600 bg-green-50',
            },
            [TipoMovimentacao.SAIDA]: {
                label: 'Saída',
                icon: ArrowUpCircle,
                color: 'text-red-600 bg-red-50',
            },
            [TipoMovimentacao.TRANSFERENCIA]: {
                label: 'Transferência',
                icon: ArrowRightLeft,
                color: 'text-blue-600 bg-blue-50',
            },
            [TipoMovimentacao.AJUSTE]: {
                label: 'Ajuste',
                icon: Settings,
                color: 'text-yellow-600 bg-yellow-50',
            },
            [TipoMovimentacao.INVENTARIO]: {
                label: 'Inventário',
                icon: Settings,
                color: 'text-purple-600 bg-purple-50',
            },
        }
        return configs[tipo]
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
                    <h1 className="text-2xl font-bold text-gray-800">Movimentações de Estoque</h1>
                    <p className="text-gray-500 text-sm">{data?.count || 0} movimentações registradas</p>
                </div>
                <button
                    onClick={() => router.push('/movimentacoes/nova')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Nova Movimentação
                </button>
            </div>

            {/* Filtros Rápidos */}
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex items-center gap-2 mb-3">
                    <Filter className="w-5 h-5 text-gray-500" />
                    <span className="font-medium text-gray-700">Filtros Rápidos</span>
                </div>
                <div className="flex flex-wrap gap-2">
                    {Object.values(TipoMovimentacao).map((tipo) => {
                        const config = getTipoConfig(tipo)
                        const Icon = config.icon
                        return (
                            <button
                                key={tipo}
                                onClick={() => setFilters({ ...filters, tipo, page: 1 })}
                                className={`px-3 py-2 rounded-lg border flex items-center gap-2 text-sm ${filters.tipo === tipo
                                        ? config.color + ' border-current'
                                        : 'border-gray-200 hover:bg-gray-50'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {config.label}
                            </button>
                        )
                    })}
                    {filters.tipo && (
                        <button
                            onClick={() => setFilters({ ...filters, tipo: undefined, page: 1 })}
                            className="px-3 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-sm"
                        >
                            Limpar
                        </button>
                    )}
                </div>
            </div>

            {/* Listagem */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Tipo
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Produto
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Origem → Destino
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                    Quantidade
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                    Valor
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Data/Hora
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Usuário
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {data?.results.map((mov) => {
                                const config = getTipoConfig(mov.tipo)
                                const Icon = config.icon

                                return (
                                    <tr key={mov.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${config.color}`}>
                                                <Icon className="w-4 h-4" />
                                                <span className="text-sm font-medium">{config.label}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="font-medium text-gray-800">{mov.produto.nome}</span>
                                            {mov.documento && (
                                                <p className="text-xs text-gray-500">Doc: {mov.documento}</p>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {mov.deposito_origem?.nome && (
                                                <span>{mov.deposito_origem.nome}</span>
                                            )}
                                            {mov.deposito_origem && mov.deposito_destino && (
                                                <span className="mx-2">→</span>
                                            )}
                                            {mov.deposito_destino?.nome && (
                                                <span>{mov.deposito_destino.nome}</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-right font-medium text-gray-800">
                                            {mov.quantidade}
                                        </td>
                                        <td className="px-6 py-4 text-right text-gray-600">
                                            {mov.valor_total ? formatBRL(mov.valor_total) : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {formatDate(mov.created_at)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {mov.usuario.username}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>

                {/* Empty State */}
                {data?.results.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhuma movimentação encontrada</p>
                        <p className="text-sm">Registre sua primeira movimentação de estoque</p>
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
