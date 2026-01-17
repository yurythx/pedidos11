'use client'
import React, { useMemo, useState } from 'react'
import type { Produto, Paginacao } from '../../../types'
import { request } from '../../../lib/http/request'
import { useQuery } from '@tanstack/react-query'
import { ProductCard } from './ProductCard'
import { useCartStore } from '../cartStore'

export function ProductGrid() {
  const [search, setSearch] = useState('')
  const addItem = useCartStore((s) => s.addItem)

  const query = useQuery({
    queryKey: ['produtos'],
    queryFn: async () => request.get<Paginacao<Produto>>('/produtos/'),
  })

  const produtos = useMemo(
    () =>
      (query.data?.results ?? [])
        .filter((p) => p.tipo !== 'INSUMO')
        .filter((p) => p.nome.toLowerCase().includes(search.toLowerCase())),
    [query.data, search]
  )

  return (
    <div className="flex-1">
      <div className="mb-3 flex items-center gap-2">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar produto"
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {produtos.map((p) => (
          <ProductCard key={p.id} produto={p} onAdd={addItem} />
        ))}
      </div>
    </div>
  )
}

