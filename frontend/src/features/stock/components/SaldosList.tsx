'use client'

import React from 'react'
import { useSaldos } from '../hooks/useStock'
import { useDepositos } from '../hooks/useStock'
import { useProducts } from '@/features/catalog/hooks/useProducts'
import { Saldo } from '../types'
import { formatBRL } from '@/utils/currency'
import { Package, AlertTriangle, Warehouse } from 'lucide-react'

export function SaldosList() {
    const [selectedDeposito, setSelectedDeposito] = React.useState<string>('')
    const [search, setSearch] = React.useState('')

    const { data: saldos, isLoading } = useSaldos({
        deposito_id: selectedDeposito || undefined,
    })
    const { data: depositos } = useDepositos()

    const filteredSaldos = React.useMemo(() => {
        if (!saldos) return []
        if (!search) return saldos

        return saldos.filter(saldo =>
            saldo.produto.nome.toLowerCase().includes(search.toLowerCase())
        )
    }, [saldos, search])

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
            <div>
                <h1 className="text-2xl font-bold text-gray-800">Saldos de Estoque</h1>
                <p className="text-gray-500 text-sm">Visualize o estoque disponível por produto e depósito</p>
            </div>

            {/* Filtros */}
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Buscar Produto
                        </label>
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Digite o nome do produto..."
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Depósito
                        </label>
                        <select
                            value={selectedDeposito}
                            onChange={(e) => setSelectedDeposito(e.target.value)}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">Todos os depósitos</option>
                            {depositos?.map((dep) => (
                                <option key={dep.id} value={dep.id}>
                                    {dep.nome}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <Package className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total de Produtos</p>
                            <p className="text-2xl font-bold text-gray-800">{filteredSaldos.length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <Warehouse className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Valor Total</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {formatBRL(filteredSaldos.reduce((sum, s) => sum + s.valor_total, 0))}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <AlertTriangle className="w-6 h-6 text-yellow-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Alertas</p>
                            <p className="text-2xl font-bold text-gray-800">
                                {filteredSaldos.filter(s => s.quantidade <= 10).length}
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
                                Produto
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Depósito
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Quantidade
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Valor Médio
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Valor Total
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {filteredSaldos.map((saldo) => (
                            <SaldoRow key={saldo.id} saldo={saldo} />
                        ))}
                    </tbody>
                </table>

                {/* Empty State */}
                {filteredSaldos.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhum saldo encontrado</p>
                        <p className="text-sm">Realize movimentações de entrada para gerar saldos</p>
                    </div>
                )}
            </div>
        </div>
    )
}

interface SaldoRowProps {
    saldo: Saldo
}

function SaldoRow({ saldo }: SaldoRowProps) {
    const isLow = saldo.quantidade <= 10

    return (
        <tr className="hover:bg-gray-50">
            <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-800">{saldo.produto.nome}</span>
                    {isLow && (
                        <AlertTriangle className="w-4 h-4 text-yellow-600" title="Estoque baixo" />
                    )}
                </div>
            </td>
            <td className="px-6 py-4 text-gray-600">
                {saldo.deposito.nome}
            </td>
            <td className={`px-6 py-4 text-right font-medium ${isLow ? 'text-yellow-600' : 'text-gray-800'}`}>
                {saldo.quantidade} {saldo.produto.unidade_medida}
            </td>
            <td className="px-6 py-4 text-right text-gray-600">
                {formatBRL(saldo.valor_medio)}
            </td>
            <td className="px-6 py-4 text-right font-semibold text-gray-800">
                {formatBRL(saldo.valor_total)}
            </td>
        </tr>
    )
}
