import React, { useEffect, useState } from 'react'
import { useMesasStore } from '../mesasStore'
import type { Mesa, Paginacao } from '../../../types'
import { request } from '../../../lib/http/request'
import { Users, Receipt, Utensils, AlertTriangle, Eye, ShoppingBag } from 'lucide-react'
import { MesaDetailsModal } from './modals/MesaDetailsModal'
import { useRouter } from 'next/navigation'
import { useCartStore } from '../cartStore'

export function MesasGrid({ onSelectMesa }: { onSelectMesa: (mesa: Mesa) => void }) {
  const { mesas, setMesas } = useMesasStore()
  const [selectedDetailsMesa, setSelectedDetailsMesa] = useState<Mesa | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { clear, setMesaId } = useCartStore()

  const loadMesas = () => {
    request.get<Paginacao<Mesa>>('/mesas/?page_size=100')
      .then((res) => {
        setMesas(res.results)
        setError(null)
      })
      .catch((err) => {
        console.error(err)
        setError('Erro ao carregar mesas. Verifique sua conexão ou faça login novamente.')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadMesas()
    const interval = setInterval(loadMesas, 10000) // Poll every 10s
    return () => clearInterval(interval)
  }, [setMesas])

  const getStatusStyle = (status: Mesa['status']) => {
    switch (status) {
      case 'LIVRE': return 'bg-white border-green-200 hover:border-green-400 hover:shadow-green-100'
      case 'SUJA': return 'bg-amber-50 border-amber-200 hover:border-amber-400 hover:shadow-amber-100'
      case 'OCUPADA': return 'bg-red-50 border-red-200 hover:border-red-400 hover:shadow-red-100'
      default: return 'bg-gray-50 border-gray-200'
    }
  }

  if (loading && mesas.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 gap-2 animate-pulse">
        <Utensils className="w-6 h-6" /> Carregando mesas...
      </div>
    )
  }

  if (error && mesas.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-500 gap-4">
        <AlertTriangle className="w-10 h-10" />
        <p>{error}</p>
        <button onClick={loadMesas} className="px-4 py-2 bg-red-100 hover:bg-red-200 rounded-lg text-red-700 font-bold transition-colors">
          Tentar Novamente
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {mesas.map((m) => (
          <div
            key={m.id}
            className={`
              relative flex flex-col justify-between p-4 h-36 rounded-xl border-2 transition-all shadow-sm group cursor-pointer
              ${getStatusStyle(m.status)}
            `}
          >
            {/* Main Click Area (Select for Order) */}
            <button 
              onClick={() => onSelectMesa(m)}
              className="absolute inset-0 z-10 w-full h-full text-left"
            />

            {/* Top Row: Icon + Number */}
            <div className="flex justify-between w-full items-start pointer-events-none">
              <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-full shadow-sm ${
                    m.status === 'LIVRE' ? 'bg-green-100 text-green-700' : 
                    m.status === 'SUJA' ? 'bg-amber-100 text-amber-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                      {m.status === 'SUJA' ? <AlertTriangle className="w-4 h-4" /> : <Utensils className="w-4 h-4" />}
                  </div>
                  <span className={`font-bold text-2xl ${
                    m.status === 'LIVRE' ? 'text-gray-700' : 
                    m.status === 'SUJA' ? 'text-amber-800' :
                    'text-red-700'
                  }`}>
                  {m.numero}
                  </span>
              </div>
              
              {m.capacidade && (
                <div className="flex items-center text-xs font-medium text-gray-500 gap-1 bg-white/80 px-2 py-1 rounded-full shadow-sm border">
                  <Users className="w-3 h-3" />
                  {m.capacidade}
                </div>
              )}
            </div>

            {/* Bottom Row: Status + Total */}
            <div className="mt-2 text-left w-full pointer-events-none">
               {m.status === 'OCUPADA' ? (
                  <>
                    <div className="text-xs text-red-600 font-bold uppercase tracking-wide mb-1 flex items-center gap-1">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        Ocupada
                    </div>
                    {m.total_conta && (
                      <div className="flex items-center gap-1 text-sm font-bold text-gray-800 bg-white/80 p-1.5 rounded-lg shadow-sm border border-red-100 w-fit">
                        <Receipt className="w-3 h-3 text-red-500" />
                        R$ {m.total_conta}
                      </div>
                    )}
                  </>
               ) : m.status === 'SUJA' ? (
                  <div className="text-xs text-amber-600 font-bold uppercase tracking-wide flex items-center gap-1">
                     <AlertTriangle className="w-3 h-3" />
                     Limpeza
                  </div>
               ) : (
                  <div className="text-xs text-green-600 font-bold uppercase tracking-wide flex items-center gap-1">
                     <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                     Livre
                  </div>
               )}
            </div>

            {/* Action Button (Details/Close) - Only visible on hover/occupied */}
            {(m.status === 'OCUPADA' || m.status === 'SUJA') && (
              <button
                onClick={(e) => {
                  e.stopPropagation() // Prevent selecting table
                  setSelectedDetailsMesa(m)
                }}
                className="absolute top-2 right-2 z-20 p-2 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-all hover:bg-gray-50 text-gray-600 hover:text-blue-600 hover:scale-110"
                title="Ver Detalhes / Fechar Conta"
              >
                <Eye className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}
      </div>

      <MesaDetailsModal 
        mesa={selectedDetailsMesa}
        isOpen={!!selectedDetailsMesa}
        onClose={() => setSelectedDetailsMesa(null)}
        onSuccess={loadMesas}
      />
    </>
  )
}
