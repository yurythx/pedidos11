'use client'
import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft, Utensils, AlertTriangle } from 'lucide-react'
import { useCartStore } from '../../../../src/features/pos/cartStore'
import { useMesasStore } from '../../../../src/features/pos/mesasStore'
import { ProductGrid } from '../../../../src/features/pos/components/ProductGrid'
import { CartPanelMesa } from '../../../../src/features/pos/components/CartPanelMesa'
import { request } from '../../../../src/lib/http/request'
import type { Mesa } from '../../../../src/types'

export default function MesaDetailPage() {
  const params = useParams()
  const mesaId = String(params.id)
  const { setMesaId, increment, decrement, clear } = useCartStore()
  const { mesas } = useMesasStore()
  
  // Busca a mesa atual do store global ou carrega se necessário
  const [mesa, setMesa] = useState<Mesa | undefined>(mesas.find(m => m.id === mesaId))

  useEffect(() => {
    // Sincroniza ID da URL com a Store
    if (mesaId) {
        setMesaId(mesaId)
        // Se não achou no store (ex: refresh da página), busca do backend
        if (!mesa) {
            request.get<Mesa>(`/mesas/${mesaId}/`)
                .then(setMesa)
                .catch(console.error)
        }
    }
  }, [mesaId, mesa])

  // Atalhos de teclado
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') clear()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [clear])

  if (!mesa) return <div className="flex items-center justify-center h-screen">Carregando mesa...</div>

  return (
    <div className="flex flex-col md:flex-row w-full h-[calc(100vh-6rem)] gap-4 relative p-4">
      {/* Área Principal: Header + Grid */}
      <div className="flex-1 flex flex-col overflow-hidden h-full gap-3">
        {/* Header da Mesa */}
        <div className="p-3 rounded-xl shadow-sm border border-gray-100 bg-white flex items-center justify-between animate-in fade-in slide-in-from-top-4">
           <div className="flex items-center gap-3">
              <Link href="/pos/salao" className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-primary transition-colors" title="Voltar para Salão">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              
              <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${
                    mesa.status === 'LIVRE' ? 'bg-green-100 text-green-700' : 
                    mesa.status === 'SUJA' ? 'bg-amber-100 text-amber-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                      {mesa.status === 'SUJA' ? <AlertTriangle className="w-5 h-5" /> : <Utensils className="w-5 h-5" />}
                  </div>
                  <div>
                      <h2 className="font-bold text-lg leading-none">Mesa {mesa.numero}</h2>
                      <span className={`text-xs font-medium ${
                        mesa.status === 'LIVRE' ? 'text-green-600' : 
                        mesa.status === 'SUJA' ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                          {mesa.status === 'LIVRE' ? 'Disponível' : 
                           mesa.status === 'SUJA' ? 'Limpeza' :
                           'Ocupada'}
                      </span>
                  </div>
              </div>
           </div>

           {mesa.status === 'OCUPADA' && (
              <div className="text-xs bg-red-50 text-red-700 px-3 py-1 rounded-full border border-red-100 font-bold flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  EM ATENDIMENTO
              </div>
           )}
        </div>
        
        <div className="flex-1 overflow-hidden">
            <ProductGrid />
        </div>
      </div>

      {/* Painel Lateral: Carrinho Específico de Mesa */}
      <div className={`
        fixed inset-0 z-40 bg-white md:relative md:z-0 md:w-96 md:block transition-transform duration-300
        hidden md:flex
      `}>
        <CartPanelMesa />
      </div>
    </div>
  )
}