'use client'
import React, { useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, ShoppingBag } from 'lucide-react'
import { useCartStore } from '../../../src/features/pos/cartStore'
import { ProductGrid } from '../../../src/features/pos/components/ProductGrid'
import { CartPanelBalcao } from '../../../src/features/pos/components/CartPanelBalcao'

export default function BalcaoPage() {
  const { resetBalcao, items, increment, decrement, clear } = useCartStore()

  // Garante que ao entrar no balcão, não temos mesa selecionada
  useEffect(() => {
    resetBalcao()
  }, [])

  // Atalhos de teclado globais
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') clear()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [increment, decrement, clear])

  return (
    <div className="flex flex-col md:flex-row w-full h-[calc(100vh-6rem)] gap-4 relative p-4">
      {/* Área Principal: Header + Grid de Produtos */}
      <div className="flex-1 flex flex-col overflow-hidden h-full gap-3">
        {/* Header Específico do Balcão */}
        <div className="p-3 rounded-xl shadow-sm border border-blue-100 bg-blue-50 flex items-center justify-between animate-in fade-in slide-in-from-top-4">
           <div className="flex items-center gap-3">
              <Link href="/pos" className="p-2 hover:bg-white/50 rounded-lg text-blue-700 hover:text-blue-900 transition-colors" title="Voltar ao Início">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              
              <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-blue-100 text-blue-700">
                      <ShoppingBag className="w-5 h-5" />
                  </div>
                  <div>
                      <h2 className="font-bold text-lg leading-none text-blue-900">Venda Balcão</h2>
                      <span className="text-xs font-medium text-blue-600">Venda Direta / Delivery</span>
                  </div>
              </div>
           </div>

           <div className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full font-bold shadow-sm">
              CAIXA LIVRE
           </div>
        </div>
        
        <div className="flex-1 overflow-hidden">
            {/* Reutilizamos o Grid de Produtos que já funciona bem */}
            <ProductGrid />
        </div>
      </div>

      {/* Painel Lateral: Carrinho Específico de Balcão */}
      <div className={`
        fixed inset-0 z-40 bg-white md:relative md:z-0 md:w-96 md:block transition-transform duration-300
        hidden md:flex
      `}>
        <CartPanelBalcao />
      </div>
    </div>
  )
}