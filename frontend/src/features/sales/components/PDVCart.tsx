'use client'

import React, { useState } from 'react'
import { useProducts } from '@/features/catalog/hooks/useProducts'
import { useCartStore } from '../store/cartStore'
import { formatBRL } from '@/utils/currency'
import {
    Search,
    ShoppingCart,
    Plus,
    Minus,
    Trash2,
    Package,
    AlertCircle
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export function PDVCart() {
    const router = useRouter()
    const [search, setSearch] = useState('')
    const { data: produtosData } = useProducts({
        search,
        ativo: true,
        page_size: 50
    })

    const {
        items,
        addItem,
        updateQuantity,
        updateDesconto,
        removeItem,
        clear,
        getSubtotal,
        getDescontoTotal,
        getTotal,
    } = useCartStore()

    const handleAddProduct = (produto: any) => {
        addItem(produto, 1)
    }

    const handleFinalizarVenda = () => {
        if (items.length === 0) {
            alert('Adicione produtos ao carrinho')
            return
        }
        router.push('/pdv/finalizar')
    }

    return (
        <div className="h-screen flex">
            {/* Produtos - Lado Esquerdo */}
            <div className="flex-1 p-6 overflow-y-auto">
                <h1 className="text-2xl font-bold text-gray-800 mb-6">PDV - Ponto de Venda</h1>

                {/* Busca */}
                <div className="mb-6">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Buscar produto por nome ou código..."
                            className="w-full pl-10 pr-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                            autoFocus
                        />
                    </div>
                </div>

                {/* Grid de Produtos */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {produtosData?.results.map((produto) => (
                        <button
                            key={produto.id}
                            onClick={() => handleAddProduct(produto)}
                            className="bg-white border-2 rounded-lg p-4 hover:border-blue-500 hover:shadow-lg transition-all text-left"
                        >
                            <div className="flex items-center justify-center h-20 mb-3 bg-gray-100 rounded-lg">
                                <Package className="w-10 h-10 text-gray-400" />
                            </div>
                            <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                                {produto.nome}
                            </h3>
                            <p className="text-2xl font-bold text-green-600">
                                {formatBRL(produto.preco_venda)}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">{produto.unidade_medida}</p>
                        </button>
                    ))}
                </div>

                {/* Empty State */}
                {produtosData?.results.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg">Nenhum produto encontrado</p>
                        <p className="text-sm">Tente buscar por outro nome</p>
                    </div>
                )}
            </div>

            {/* Carrinho - Lado Direito */}
            <div className="w-96 bg-white border-l flex flex-col">
                {/* Header do Carrinho */}
                <div className="p-6 border-b">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                            <ShoppingCart className="w-6 h-6" />
                            Carrinho
                        </h2>
                        {items.length > 0 && (
                            <button
                                onClick={clear}
                                className="text-red-600 hover:text-red-700 text-sm"
                            >
                                Limpar
                            </button>
                        )}
                    </div>
                    <p className="text-sm text-gray-500">{items.length} item(ns)</p>
                </div>

                {/* Lista de Itens */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {items.length === 0 ? (
                        <div className="text-center py-12 text-gray-400">
                            <ShoppingCart className="w-16 h-16 mx-auto mb-4" />
                            <p>Carrinho vazio</p>
                            <p className="text-sm">Adicione produtos para iniciar a venda</p>
                        </div>
                    ) : (
                        items.map((item) => (
                            <div key={item.produto.id} className="bg-gray-50 rounded-lg p-4">
                                <div className="flex justify-between items-start mb-3">
                                    <h3 className="font-semibold text-gray-800 flex-1">
                                        {item.produto.nome}
                                    </h3>
                                    <button
                                        onClick={() => removeItem(item.produto.id)}
                                        className="text-red-600 hover:text-red-700 ml-2"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>

                                {/* Quantidade */}
                                <div className="flex items-center gap-3 mb-3">
                                    <button
                                        onClick={() => updateQuantity(item.produto.id, item.quantidade - 1)}
                                        className="p-1 border rounded hover:bg-gray-200"
                                    >
                                        <Minus className="w-4 h-4" />
                                    </button>
                                    <input
                                        type="number"
                                        value={item.quantidade}
                                        onChange={(e) => updateQuantity(item.produto.id, Number(e.target.value))}
                                        className="w-16 text-center px-2 py-1 border rounded"
                                        min="1"
                                    />
                                    <button
                                        onClick={() => updateQuantity(item.produto.id, item.quantidade + 1)}
                                        className="p-1 border rounded hover:bg-gray-200"
                                    >
                                        <Plus className="w-4 h-4" />
                                    </button>
                                    <span className="text-sm text-gray-500">
                                        x {formatBRL(item.produto.preco_venda)}
                                    </span>
                                </div>

                                {/* Desconto */}
                                <div className="mb-2">
                                    <label className="text-xs text-gray-600 block mb-1">Desconto</label>
                                    <input
                                        type="number"
                                        value={item.desconto}
                                        onChange={(e) => updateDesconto(item.produto.id, Number(e.target.value))}
                                        className="w-full px-2 py-1 border rounded text-sm"
                                        placeholder="0.00"
                                        min="0"
                                        step="0.01"
                                    />
                                </div>

                                {/* Total do Item */}
                                <div className="flex justify-between items-center pt-2 border-t">
                                    <span className="text-sm text-gray-600">Subtotal</span>
                                    <span className="font-bold text-gray-800">
                                        {formatBRL(
                                            item.produto.preco_venda * item.quantidade - item.desconto
                                        )}
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Resumo e Ações */}
                {items.length > 0 && (
                    <div className="p-6 border-t space-y-4">
                        <div className="space-y-2">
                            <div className="flex justify-between text-gray-600">
                                <span>Subtotal</span>
                                <span>{formatBRL(getSubtotal())}</span>
                            </div>
                            {getDescontoTotal() > 0 && (
                                <div className="flex justify-between text-green-600">
                                    <span>Desconto</span>
                                    <span>-{formatBRL(getDescontoTotal())}</span>
                                </div>
                            )}
                            <div className="flex justify-between text-2xl font-bold text-gray-800 pt-2 border-t">
                                <span>Total</span>
                                <span>{formatBRL(getTotal())}</span>
                            </div>
                        </div>

                        <button
                            onClick={handleFinalizarVenda}
                            className="w-full bg-green-600 hover:bg-green-700 text-white py-4 rounded-lg font-bold text-lg transition-colors"
                        >
                            Finalizar Venda
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}
