'use client'

import React, { useState } from 'react'
import { useProducts, useDeleteProduct } from '../hooks/useProducts'
import { ProductFilters as Filters } from '../types'
import { ProductFilters } from './ProductFilters'
import { ProductCard } from './ProductCard'
import { Loader2, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function ProductList() {
    const router = useRouter()
    const [filters, setFilters] = useState<Filters>({
        page: 1,
        page_size: 20,
    })

    const { data, isLoading, error } = useProducts(filters)
    const deleteMutation = useDeleteProduct()

    const handleDelete = async (id: string) => {
        if (confirm('Tem certeza que deseja excluir este produto?')) {
            try {
                await deleteMutation.mutateAsync(id)
            } catch (err) {
                alert('Erro ao excluir produto')
            }
        }
    }

    const handlePageChange = (page: number) => {
        setFilters(prev => ({ ...prev, page }))
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg">
                Erro ao carregar produtos
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Produtos</h1>
                    <p className="text-gray-500 text-sm">{data?.count || 0} produtos cadastrados</p>
                </div>
                <button
                    onClick={() => router.push('/produtos/novo')}
                    className="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Novo Produto
                </button>
            </div>

            {/* Filtros */}
            <ProductFilters filters={filters} onChange={setFilters} />

            {/* Grid de Produtos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {data?.results.map((produto) => (
                    <ProductCard
                        key={produto.id}
                        produto={produto}
                        onDelete={() => handleDelete(produto.id)}
                        onEdit={() => router.push(`/produtos/${produto.id}`)}
                    />
                ))}
            </div>

            {/* Paginação */}
            {data && data.total_pages > 1 && (
                <div className="flex justify-center gap-2 mt-6">
                    <button
                        onClick={() => handlePageChange(filters.page! - 1)}
                        disabled={!data.previous}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                        Anterior
                    </button>
                    <span className="px-4 py-2">
                        Página {data.current_page} de {data.total_pages}
                    </span>
                    <button
                        onClick={() => handlePageChange(filters.page! + 1)}
                        disabled={!data.next}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                        Próxima
                    </button>
                </div>
            )}

            {/* Empty State */}
            {data?.results.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <p className="text-lg">Nenhum produto encontrado</p>
                    <p className="text-sm">Tente ajustar os filtros ou criar um novo produto</p>
                </div>
            )}
        </div>
    )
}
