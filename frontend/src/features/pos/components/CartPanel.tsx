'use client'
import React, { useEffect, useMemo, useState } from 'react'
import { useCartStore } from '../cartStore'
import { formatBRL } from '../../../utils/currency'
import { request } from '../../../lib/http/request'
import { useAuthStore } from '../../auth/store'
import type { VendaSnapshotItem } from '../../../types'
import { Trash2, Plus, Minus, Check } from 'lucide-react'

export function CartPanel() {
  const { items, increment, decrement, removeItem, clear, subtotal, snapshot } = useCartStore()
  const total = useMemo(() => subtotal(), [items])
  const { user } = useAuthStore()
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [depositoId, setDepositoId] = useState<string>('')

  useEffect(() => {
    const load = async () => {
      try {
        const res = await request.get<any>('/depositos/?page_size=100')
        setDepositos(res?.results ?? res ?? [])
      } catch {
        setDepositos([])
      }
    }
    load()
  }, [])

  const efetivar = async () => {
    if (!depositoId) {
      alert('Selecione um depósito para finalizar')
      return
    }
    // Cria venda e adiciona itens via API oficial
    const venda = await request.post<any>('/vendas/', {
      vendedor: user?.id ?? null,
      tipo_pagamento: 'DINHEIRO',
      observacoes: 'PDV',
    })
    const vendaId = venda?.id
    const payload: VendaSnapshotItem[] = snapshot()
    for (const item of payload) {
      await request.post<any>('/itens-venda/', {
        venda: vendaId,
        produto: item.produto_id,
        quantidade: item.quantidade,
      })
    }
    await request.post<any>(`/vendas/${vendaId}/finalizar/`, { deposito_id: depositoId })
    alert('Venda finalizada no PDV')
    clear()
  }

  return (
    <aside className="w-full md:w-80 border-l p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="font-semibold">Carrinho</div>
        <button onClick={clear} className="text-sm px-2 py-1 border rounded flex items-center gap-1">
          <Trash2 size={16} /> Limpar
        </button>
      </div>
      <div className="space-y-2">
        {items.map((i) => (
          <div key={i.produto_id} className="flex items-center justify-between border rounded p-2">
            <div>
              <div className="text-sm font-medium">{i.produto?.nome}</div>
              <div className="text-xs text-gray-600">{formatBRL(i.produto?.preco_venda ?? 0)}</div>
            </div>
            <div className="flex items-center gap-2">
              <button className="border rounded p-1" onClick={() => decrement(i.produto_id)}>
                <Minus size={16} />
              </button>
              <span className="w-6 text-center">{i.quantidade}</span>
              <button className="border rounded p-1" onClick={() => increment(i.produto_id)}>
                <Plus size={16} />
              </button>
              <button className="border rounded p-1" onClick={() => removeItem(i.produto_id)}>
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
        <div className="border-t pt-2 mt-2 flex items-center justify-between">
          <div className="text-sm">Subtotal estimado</div>
          <div className="font-semibold">{formatBRL(total)}</div>
        </div>
        <div className="mt-2">
          <label className="block text-sm">Depósito</label>
          <select
            className="mt-1 w-full border rounded px-3 py-2"
            value={depositoId}
            onChange={(e) => setDepositoId(e.target.value)}
          >
            <option value="">Selecione</option>
            {depositos.map((d) => (
              <option key={d.id} value={d.id}>{d.nome}</option>
            ))}
          </select>
        </div>
        <button
          className="w-full bg-black text-white rounded px-3 py-2 mt-3 flex items-center justify-center gap-2"
          onClick={efetivar}
          disabled={items.length === 0}
        >
          <Check size={18} /> Efetivar
        </button>
      </div>
    </aside>
  )
}

