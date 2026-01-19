'use client'
import React, { useEffect, useMemo, useState } from 'react'
import { useCartStore } from '../cartStore'
import { formatBRL } from '../../../utils/currency'
import { request } from '../../../lib/http/request'
import { useAuthStore } from '../../auth/store'
import type { VendaSnapshotItem } from '../../../types'
import { Trash2, Plus, Minus, Check, ShoppingCart, AlertCircle } from 'lucide-react'

export function CartPanel() {
  const { items, increment, decrement, removeItem, clear, subtotal, snapshot } = useCartStore()
  const total = useMemo(() => subtotal(), [items])
  const { user } = useAuthStore()
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [depositoId, setDepositoId] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await request.get<any>('/depositos/?page_size=100')
        setDepositos(res?.results ?? res ?? [])
        // Selecionar primeiro depósito automaticamente se houver
        if (res?.results?.length > 0 && !depositoId) {
          setDepositoId(res.results[0].id)
        }
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
    setLoading(true)
    try {
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
    } catch (e) {
      alert('Erro ao finalizar venda')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-white md:rounded-2xl md:shadow-sm md:border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-white">
        <h2 className="font-bold text-gray-800 flex items-center gap-2">
          <ShoppingCart className="w-5 h-5 text-primary" />
          Itens ({items.length})
        </h2>
        {items.length > 0 && (
          <button 
            onClick={clear} 
            className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-1"
          >
            <Trash2 size={14} /> Limpar
          </button>
        )}
      </div>

      {/* Lista de Itens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
            <ShoppingCart className="w-16 h-16 mb-4" />
            <p className="text-center font-medium">Seu carrinho está vazio</p>
            <p className="text-sm text-center">Adicione produtos para começar</p>
          </div>
        ) : (
          items.map((i) => (
            <div key={i.produto_id} className="flex flex-col gap-2 p-3 rounded-xl border border-gray-100 hover:border-red-100 bg-white transition-colors shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold text-gray-800 line-clamp-2">{i.produto?.nome}</div>
                  <div className="text-sm text-primary font-bold mt-1">
                    {formatBRL(i.produto?.preco_venda ?? 0)}
                  </div>
                </div>
                <button 
                  className="text-gray-400 hover:text-red-500 p-1" 
                  onClick={() => removeItem(i.produto_id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
              
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-50">
                <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-1">
                  <button 
                    className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all disabled:opacity-50" 
                    onClick={() => decrement(i.produto_id)}
                    disabled={i.quantity <= 1}
                  >
                    <Minus size={14} />
                  </button>
                  <span className="w-8 text-center font-bold text-gray-800">{i.quantity}</span>
                  <button 
                    className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all" 
                    onClick={() => increment(i.produto_id)}
                  >
                    <Plus size={14} />
                  </button>
                </div>
                <div className="font-bold text-gray-800">
                  {formatBRL((i.produto?.preco_venda ?? 0) * i.quantity)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer / Checkout */}
      <div className="p-4 border-t border-gray-50 bg-gray-50 space-y-4">
        <div className="space-y-2">
           <div className="flex justify-between text-sm text-gray-500">
            <span>Itens</span>
            <span>{items.reduce((acc, i) => acc + i.quantity, 0)}</span>
          </div>
          <div className="flex justify-between items-end">
            <span className="text-gray-600 font-medium">Total a Pagar</span>
            <span className="text-2xl font-bold text-primary">{formatBRL(total)}</span>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Depósito de Saída</label>
          <select
            className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
            value={depositoId}
            onChange={(e) => setDepositoId(e.target.value)}
          >
            <option value="">Selecione um depósito...</option>
            {depositos.map((d) => (
              <option key={d.id} value={d.id}>{d.nome}</option>
            ))}
          </select>
          {!depositoId && items.length > 0 && (
             <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
               <AlertCircle size={12} /> Selecione um depósito para continuar
             </p>
          )}
        </div>

        <button
          className={`
            w-full py-3.5 rounded-xl font-bold text-white shadow-lg shadow-red-200 flex items-center justify-center gap-2 transition-all
            ${items.length === 0 || !depositoId || loading
              ? 'bg-gray-300 cursor-not-allowed shadow-none' 
              : 'bg-primary hover:bg-primary-dark active:scale-95'
            }
          `}
          onClick={efetivar}
          disabled={items.length === 0 || !depositoId || loading}
        >
          {loading ? (
             <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <Check size={20} /> Finalizar Venda
            </>
          )}
        </button>
      </div>
    </div>
  )
}

