'use client'
import React from 'react'
import type { Produto } from '../../../types'
import { formatBRL } from '../../../utils/currency'

export function ProductCard({ produto, onAdd }: { produto: Produto; onAdd: (p: Produto) => void }) {
  return (
    <button
      onClick={() => onAdd(produto)}
      className="rounded border p-3 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-black"
    >
      <div className="font-medium">{produto.nome}</div>
      <div className="text-sm text-gray-600">{formatBRL(produto.preco_venda)}</div>
    </button>
  )
}

