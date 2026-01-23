'use client'
import React, { useEffect, useState, useMemo } from 'react'
import { useCartStore } from '../cartStore'
import { formatBRL } from '../../../utils/currency'
import { request } from '../../../lib/http/request'
import { useAuthStore } from '../../auth/store'
import { useCaixaStore } from '@/features/financial/store/caixaStore'
import type { VendaSnapshotItem } from '../../../types'
import { Trash2, Plus, Minus, Check, ShoppingCart, ShoppingBag } from 'lucide-react'

import { PaymentModal } from './modals/PaymentModal'

export function CartPanelBalcao() {
  const { items, increment, decrement, removeItem, clear, subtotal, snapshot } = useCartStore()
  
  const total = useMemo(() => subtotal(), [items])
  const { user } = useAuthStore()
  const { sessaoAberta } = useCaixaStore()
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const handlePaymentConfirm = async (paymentData: { tipo_pagamento: string; deposito_id: string; valor_pago: number }) => {
    try {
      // Cria venda e adiciona itens via API oficial
      const venda = await request.post<any>('/vendas/', {
        vendedor: user?.id ?? null,
        tipo_pagamento: paymentData.tipo_pagamento,
        observacoes: 'PDV Balcão',
      })
      const vendaId = venda?.id
      const payload: VendaSnapshotItem[] = snapshot()
      for (const item of payload) {
        await request.post<any>('/itens-venda/', {
          venda: vendaId,
          produto: item.produto_id,
          quantidade: item.quantidade,
          observacoes: item.observacoes
        })
      }
      await request.post<any>(`/vendas/${vendaId}/finalizar/`, { deposito_id: paymentData.deposito_id })
      
      setSuccessMessage('Venda finalizada')
      setTimeout(() => setSuccessMessage(null), 3000)
      clear()
      setShowPaymentModal(false)
    } catch (e: any) {
      console.error('Erro ao finalizar venda:', e)
      const errorMsg = e.response?.data?.error || e.response?.data?.detail || e.message || 'Erro desconhecido'
      const finalMsg = Array.isArray(errorMsg) ? errorMsg.join('\n') : errorMsg
      alert(`Erro ao finalizar venda:\n${finalMsg}`)
    }
  }

  const canSubmit = items.length > 0

  return (
    <div className="h-full flex flex-col bg-white md:rounded-2xl md:shadow-sm md:border border-gray-100 overflow-hidden relative">
      {successMessage && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/90 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="flex flex-col items-center gap-4 p-8 bg-white rounded-2xl shadow-2xl border border-green-100 transform scale-110">
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-2">
                    <Check className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 text-center">{successMessage}</h3>
            </div>
        </div>
      )}

      <PaymentModal 
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        total={total}
        onConfirm={handlePaymentConfirm}
      />

      {/* Header Balcão */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between shadow-sm z-10 bg-white">
        <h2 className="font-bold text-gray-800 flex items-center gap-2">
          <ShoppingBag className="w-5 h-5 text-primary" />
          Carrinho Balcão ({items.length})
        </h2>
        {items.length > 0 && (
          <button 
            onClick={clear} 
            className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-1"
          >
            <Trash2 size={14} />
          </button>
        )}
      </div>

      {/* Lista de Itens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
            <ShoppingCart className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-center font-medium">Seu carrinho está vazio</p>
            <p className="text-sm text-center px-8">Adicione produtos para realizar a venda</p>
          </div>
        ) : (
          items.map((i) => (
            <div key={i.produto_id} className="flex flex-col gap-2 p-3 rounded-xl border border-gray-100 hover:border-red-200 bg-white transition-colors shadow-sm animate-in fade-in zoom-in-95 duration-200">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold text-gray-800 line-clamp-2">{i.produto?.nome}</div>
                  <div className="text-sm text-primary font-bold mt-1">
                    {formatBRL(i.produto?.preco_venda ?? 0)}
                  </div>
                </div>
                <button 
                  className="text-gray-400 hover:text-red-500 p-2 rounded-full hover:bg-red-50 transition-colors z-20 relative" 
                  onClick={(e) => {
                    e.stopPropagation()
                    removeItem(i.produto_id)
                  }}
                >
                  <Trash2 size={18} />
                </button>
              </div>
              
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-50">
                <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-1">
                  <button 
                    className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all disabled:opacity-50" 
                    onClick={() => decrement(i.produto_id)}
                    disabled={i.quantidade <= 1}
                  >
                    <Minus size={14} />
                  </button>
                  <span className="w-8 text-center font-bold text-gray-800">{i.quantidade}</span>
                  <button 
                    className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all" 
                    onClick={() => increment(i.produto_id)}
                  >
                    <Plus size={14} />
                  </button>
                </div>
                <div className="font-bold text-gray-800">
                  {formatBRL(((i.produto?.preco_venda ?? 0) * i.quantidade) || 0)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Balcão */}
      <div className="p-4 border-t border-gray-50 bg-gray-50 space-y-4">
        <div className="space-y-2">
           <div className="flex justify-between text-sm text-gray-500">
            <span>Itens</span>
            <span>{items.reduce((acc, i) => acc + i.quantidade, 0)}</span>
          </div>
          <div className="flex justify-between items-end">
            <span className="text-gray-600 font-medium">Total a Pagar</span>
            <span className="text-3xl font-bold text-primary">{formatBRL(total || 0)}</span>
          </div>
        </div>

        <button
            className={`
              w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg shadow-red-200 flex items-center justify-center gap-2 transition-all
              ${!canSubmit
                ? 'bg-gray-300 cursor-not-allowed shadow-none' 
                : 'bg-primary hover:bg-primary-dark active:scale-95'
              }
            `}
            onClick={() => {
                if (!sessaoAberta) {
                    alert('Caixa Fechado! É necessário abrir o caixa para realizar vendas.')
                    return
                }
                setShowPaymentModal(true)
            }}
            disabled={!canSubmit}
          >
            <Check size={24} /> Finalizar Venda Rápida
          </button>
      </div>
    </div>
  )
}