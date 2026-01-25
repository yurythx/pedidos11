'use client'

import React from 'react'
import { useLotes, useDeleteLote, useLotesVencendo } from '../hooks/useStock'
import { StatusLote } from '../types'
import { formatBRL } from '@/utils/currency'
import {
    Package,
    AlertTriangle,
    CheckCircle2,
    XCircle,
    Calendar,
    Plus,
    Edit,
    Trash2
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function LotesList() {
    const router = useRouter()
    const [filters, setFilters] = React.useState({
        page: 1,
        page_size: 20,
    })

    const { data, isLoading } = useLotes(filters)
    const { data: lotesVencendo } = useLotesVencendo(30)
    const deleteMutation = useDeleteLote()

    const handleDelete = async (id: string) => {
        if (confirm('Tem certeza que deseja excluir este lote?')) {
            try {
                await deleteMutation.mutateAsync(id)
            } catch (err) {
                alert('Erro ao excluir lote')
            }
        }
    }

    const getStatusConfig = (status: StatusLote) => {
        const configs = {
            [StatusLote.OK]: {
                label: 'OK',
                icon: CheckCircle2,
                color: 'text-green-600 bg-green-50',
            },
            [StatusLote.ATENCAO]: {
                label: 'Atenção',
                icon: AlertTriangle,
                color: 'text-yellow-600 bg-yellow-50',
            },
            [StatusLote.CRITICO]: {
                label: 'Crítico',
                icon: AlertTriangle,
                color: 'text-orange-600 bg-orange-50',
            },
            [StatusLote.VENCIDO]: {
                label: 'Vencido',
                icon: XCircle,
                color: 'text-red-600 bg-red-50',
            },
        }
        return configs[status]
    }

    const formatDate = (dateString?: string) => {
        if (!dateString) return '-'
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Lotes de Estoque</h1>
                    <p className="text-gray-500 text-sm">{data?.count || 0} lotes cadastrados</p>
                </div>
                <button
                    onClick={() => router.push('/lotes/novo')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Novo Lote
                </button>
            </div>

            {/* Alertas de Vencimento */}
            {lotesVencendo && lotesVencendo.length > 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                    <div className="flex items-start">
                        <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
                        <div>
                            <h3 className="font-semibold text-yellow-800">
                                Atenção: {lotesVencendo.length} lote(s) vencendo nos próximos 30 dias
                            </h3>
                            <p className="text-sm text-yellow-700 mt-1">
                                Verifique os lotes com status crítico para evitar perdas
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Cards de Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.values(StatusLote).map((status) => {
                    const config = getStatusConfig(status)
                    const Icon = config.icon
                    const count = data?.results.filter(l => l.status_validade === status).length || 0

                    return (
                        <div key={status} className="bg-white p-4 rounded-lg border">
                            <div className="flex items-center gap-3">
                                <div className={`p-3 rounded-lg ${config.color}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-500">{config.label}</p>
                                    <p className="text-2xl font-bold text-gray-800">{count}</p>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Tabela */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Código
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Produto
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Depósito
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Qtd Atual
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Validade
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
                        {data?.results.map((lote) => {
                            const statusConfig = getStatusConfig(lote.status_validade)
                            const StatusIcon = statusConfig.icon

                            return (
                                <tr key={lote.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 font-medium text-gray-800">
                                        {lote.codigo}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div>
                                            <p className="font-medium text-gray-800">{lote.produto.nome}</p>
                                            {lote.documento && (
                                                <p className="text-xs text-gray-500">Doc: {lote.documento}</p>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-gray-600">
                                        {lote.deposito.nome}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span className="font-medium text-gray-800">
                                            {lote.quantidade_atual}
                                        </span>
                                        <span className="text-gray-500 text-sm ml-1">
                                            / {lote.quantidade_inicial}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-600">
                                        {formatDate(lote.data_validade)}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${statusConfig.color}`}>
                                            <StatusIcon className="w-4 h-4" />
                                            <span className="text-sm font-medium">{statusConfig.label}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => router.push(`/lotes/${lote.id}`)}
                                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                                                title="Editar"
                                            >
                                                <Edit className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(lote.id)}
                                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                                                title="Excluir"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>

                {/* Empty State */}
                {data?.results.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhum lote encontrado</p>
                        <p className="text-sm">Cadastre lotes para controlar validade e rastreabilidade</p>
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
