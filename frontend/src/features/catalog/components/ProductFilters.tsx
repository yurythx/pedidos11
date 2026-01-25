'use client'

import React from 'react'
import { ProductFilters as Filters, TipoProduto } from '../types'
import { useCategories } from '../hooks/useCategories'
import { Search, Filter } from 'lucide-react'

interface Props {
    filters: Filters
    onChange: (filters: Filters) => void
}

export function ProductFilters({ filters, onChange }: Props) {
    const { data: categorias } = useCategories()

    const handleChange = (key: keyof Filters, value: any) => {
        onChange({ ...filters, [key]: value, page: 1 }) // Reset página ao filtrar
    }

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
            <div className="flex items-center gap-2 text-gray-700 font-medium">
                <Filter className="w-5 h-5" />
                Filtros
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Busca */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar produto..."
                        value={filters.search || ''}
                        onChange={(e) => handleChange('search', e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>

                {/* Categoria */}
                <select
                    value={filters.categoria_id || ''}
                    onChange={(e) => handleChange('categoria_id', e.target.value || undefined)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Todas as categorias</option>
                    {categorias?.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                            {cat.nome}
                        </option>
                    ))}
                </select>

                {/* Tipo */}
                <select
                    value={filters.tipo || ''}
                    onChange={(e) => handleChange('tipo', e.target.value as TipoProduto || undefined)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Todos os tipos</option>
                    <option value={TipoProduto.SIMPLES}>Simples</option>
                    <option value={TipoProduto.COMPOSTO}>Composto</option>
                    <option value={TipoProduto.MATERIA_PRIMA}>Matéria Prima</option>
                </select>

                {/* Preço Mínimo */}
                <input
                    type="number"
                    placeholder="Preço mín"
                    value={filters.preco_min || ''}
                    onChange={(e) => handleChange('preco_min', e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />

                {/* Preço Máximo */}
                <input
                    type="number"
                    placeholder="Preço máx"
                    value={filters.preco_max || ''}
                    onChange={(e) => handleChange('preco_max', e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />

                {/* Ativo */}
                <select
                    value={filters.ativo === undefined ? '' : filters.ativo.toString()}
                    onChange={(e) => handleChange('ativo', e.target.value === '' ? undefined : e.target.value === 'true')}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Todos status</option>
                    <option value="true">Ativos</option>
                    <option value="false">Inativos</option>
                </select>

                {/* Ordenação */}
                <select
                    value={filters.ordering || ''}
                    onChange={(e) => handleChange('ordering', e.target.value || undefined)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">Ordenar por...</option>
                    <option value="nome">Nome (A-Z)</option>
                    <option value="-nome">Nome (Z-A)</option>
                    <option value="preco_venda">Preço (Menor)</option>
                    <option value="-preco_venda">Preço (Maior)</option>
                    <option value="-created_at">Mais recentes</option>
                </select>

                {/* Limpar filtros */}
                <button
                    onClick={() => onChange({ page: 1, page_size: 20 })}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    Limpar
                </button>
            </div>
        </div>
    )
}
