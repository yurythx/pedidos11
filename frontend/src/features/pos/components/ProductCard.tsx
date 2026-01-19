'use client'
import React from 'react'
import type { Produto } from '../../../types'
import { formatBRL } from '../../../utils/currency'
import { Plus } from 'lucide-react'

export function ProductCard({ produto, onAdd }: { produto: Produto; onAdd: (p: Produto) => void }) {
  return (
    <button
      onClick={() => onAdd(produto)}
      className="group relative flex flex-col justify-between h-32 md:h-40 p-4 bg-white rounded-xl border border-gray-100 hover:border-primary/50 hover:shadow-md transition-all duration-200 text-left active:scale-95 overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="bg-primary text-white p-1 rounded-full shadow-sm">
          <Plus size={16} />
        </div>
      </div>
      
      <div className="font-semibold text-gray-800 line-clamp-2 text-sm md:text-base leading-tight">
        {produto.nome}
      </div>
      
      <div className="mt-2">
        <div className="text-xs text-gray-500 mb-0.5">Preço</div>
        <div className="font-bold text-primary text-base md:text-lg">
          {formatBRL(produto.preco_venda)}
        </div>
      </div>
    </button>
  )
}

