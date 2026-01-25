'use client'

import React from 'react'
import { useDepositos, useDeleteDeposito } from '../hooks/useStock'
import { Deposito } from '../types'
import { Warehouse, Edit, Trash2, Plus, CheckCircle2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function DepositosList() {
    const router = useRouter()
    const { data: depositos, isLoading, error } = useDepositos()
    const deleteMutation = useDeleteDeposito()

    const handleDelete = async (id: string) => {
        if (confirm('Tem certeza que deseja excluir este depósito?')) {
            try {
                await deleteMutation.mutateAsync(id)
            } catch (err) {
                alert('Erro ao excluir depósito. Pode haver saldos associados.')
            }
        }
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                Erro ao carregar depósitos
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Depósitos</h1>
                    <p className="text-gray-500 text-sm">{depositos?.length || 0} depósitos cadastrados</p>
                </div>
                <button
                    onClick={() => router.push('/depositos/novo')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Novo Depósito
                </button>
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {depositos?.map((deposito) => (
                    <DepositoCard
                        key={deposito.id}
                        deposito={deposito}
                        onEdit={() => router.push(`/depositos/${deposito.id}`)}
                        onDelete={() => handleDelete(deposito.id)}
                    />
                ))}
            </div>

            {/* Empty State */}
            {depositos?.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <Warehouse className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg">Nenhum depósito cadastrado</p>
                    <p className="text-sm">Crie seu primeiro depósito para gerenciar o estoque</p>
                </div>
            )}
        </div>
    )
}

interface DepositoCardProps {
    deposito: Deposito
    onEdit: () => void
    onDelete: () => void
}

function DepositoCard({ deposito, onEdit, onDelete }: DepositoCardProps) {
    return (
        <div className="bg-white border rounded-lg p-6 hover:shadow-lg transition-shadow">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg ${deposito.is_padrao ? 'bg-blue-100' : 'bg-gray-100'}`}>
                        <Warehouse className={`w-6 h-6 ${deposito.is_padrao ? 'text-blue-600' : 'text-gray-600'}`} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                            {deposito.nome}
                            {deposito.is_padrao && (
                                <CheckCircle2 className="w-4 h-4 text-blue-600" title="Depósito Padrão" />
                            )}
                        </h3>
                        <p className="text-sm text-gray-500">{deposito.codigo}</p>
                    </div>
                </div>

                {!deposito.ativo && (
                    <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                        Inativo
                    </span>
                )}
            </div>

            {/* Descrição */}
            {deposito.descricao && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {deposito.descricao}
                </p>
            )}

            {/* Endereço */}
            {deposito.endereco && (
                <p className="text-xs text-gray-500 mb-4">
                    📍 {deposito.endereco}
                </p>
            )}

            {/* Ações */}
            <div className="flex gap-2 pt-4 border-t">
                <button
                    onClick={onEdit}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                >
                    <Edit className="w-4 h-4" />
                    Editar
                </button>

                <button
                    onClick={onDelete}
                    className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                    title="Excluir"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    )
}
