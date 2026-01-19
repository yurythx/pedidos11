'use client'
import React, { useMemo, useState } from 'react'
import type { Produto, Paginacao } from '../../../types'
import { request } from '../../../lib/http/request'
import { useQuery } from '@tanstack/react-query'
import { ProductCard } from './ProductCard'
import { useCartStore } from '../cartStore'
import { Search, Loader2 } from 'lucide-react'

export function ProductGrid() {
  const [search, setSearch] = useState('')
  const addItem = useCartStore((s) => s.addItem)

  const query = useQuery({
    queryKey: ['produtos'],
    queryFn: async () => request.get<Paginacao<Produto>>('/produtos/?page_size=100'),
  })

  const produtos = useMemo(
    () =>
      (query.data?.results ?? [])
        .filter((p) => p.tipo !== 'INSUMO')
        .filter((p) => p.nome.toLowerCase().includes(search.toLowerCase())),
    [query.data, search]
  )

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header com Busca */}
      <div className="p-4 border-b border-gray-50 bg-white sticky top-0 z-10">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar produto por nome ou código..."
            className="w-full pl-10 pr-4 py-3 rounded-xl bg-gray-50 border-none focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder-gray-400"
          />
        </div>
      </div>

      {/* Grid de Produtos */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {query.isLoading ? (
          <div className="flex items-center justify-center h-64 text-gray-400">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : produtos.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <Search className="w-12 h-12 mb-2 opacity-20" />
            <p>Nenhum produto encontrado</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {produtos.map((p) => (
              <ProductCard key={p.id} produto={p} onAdd={addItem} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

