'use client'

import React from 'react'
import { Produto, TipoProduto } from '../types'
import { formatBRL } from '@/utils/currency'
import { Edit, Trash2, Package } from 'lucide-react'
import Image from 'next/image'

interface Props {
    produto: Produto
    onEdit: () => void
    onDelete: () => void
}

export function ProductCard({ produto, onEdit, onDelete }: Props) {
    const getTipoBadge = (tipo: TipoProduto) => {
        const colors = {
            [TipoProduto.SIMPLES]: 'bg-blue-100 text-blue-700',
            [TipoProduto.COMPOSTO]: 'bg-purple-100 text-purple-700',
            [TipoProduto.MATERIA_PRIMA]: 'bg-green-100 text-green-700',
        }

        const labels = {
            [TipoProduto.SIMPLES]: 'Simples',
            [TipoProduto.COMPOSTO]: 'Composto',
            [TipoProduto.MATERIA_PRIMA]: 'Matéria Prima',
        }

        return (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[tipo]}`}>
                {labels[tipo]}
            </span>
        )
    }

    return (
        <div className="bg-white border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            {/* Imagem */}
            <div className="relative h-48 bg-gray-100">
                {produto.foto ? (
                    <Image
                        src={produto.foto}
                        alt={produto.nome}
                        fill
                        className="object-cover"
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <Package className="w-16 h-16 text-gray-300" />
                    </div>
                )}

                {/* Badge Status */}
                {!produto.ativo && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-medium">
                        Inativo
                    </div>
                )}
            </div>

            {/* Conteúdo */}
            <div className="p-4 space-y-3">
                {/* Nome e Tipo */}
                <div>
                    <h3 className="font-semibold text-gray-800 text-lg truncate" title={produto.nome}>
                        {produto.nome}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        {getTipoBadge(produto.tipo)}
                        <span className="text-xs text-gray-500">{produto.categoria.nome}</span>
                    </div>
                </div>

                {/* Descricão */}
                {produto.descricao && (
                    <p className="text-sm text-gray-600 line-clamp-2">
                        {produto.descricao}
                    </p>
                )}

                {/* Preços */}
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <p className="text-xs text-gray-500">Preço Venda</p>
                        <p className="font-bold text-green-600">
                            {formatBRL(produto.preco_venda)}
                        </p>
                    </div>
                    {produto.preco_custo && (
                        <div>
                            <p className="text-xs text-gray-500">Custo</p>
                            <p className="font-medium text-gray-700">
                                {formatBRL(produto.preco_custo)}
                            </p>
                        </div>
                    )}
                </div>

                {/* Margem */}
                {produto.margem_lucro !== null && produto.margem_lucro !== undefined && (
                    <div className="pt-2 border-t">
                        <p className="text-xs text-gray-500">Margem de Lucro</p>
                        <p className={`font-semibold ${produto.margem_lucro >= 30 ? 'text-green-600' :
                                produto.margem_lucro >= 15 ? 'text-yellow-600' :
                                    'text-red-600'
                            }`}>
                            {produto.margem_lucro.toFixed(1)}%
                        </p>
                    </div>
                )}

                {/* Ações */}
                <div className="flex gap-2 pt-3 border-t">
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
        </div>
    )
}
