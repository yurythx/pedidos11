import React, { useEffect, useState } from 'react'
import { useComandasStore } from '../comandasStore'
import type { Comanda, Paginacao } from '../../../types'
import { request } from '../../../lib/http/request'
import { CreditCard, AlertTriangle, Utensils } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function ComandasGrid({ onSelectComanda }: { onSelectComanda: (comanda: Comanda) => void }) {
  const { comandas, setComandas } = useComandasStore()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  
  const loadComandas = () => {
    request.get<Paginacao<Comanda>>('/comandas/?page_size=100')
      .then((res) => {
        setComandas(res.results)
        setError(null)
      })
      .catch((err) => {
        console.error(err)
        setError('Erro ao carregar comandas.')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadComandas()
    const interval = setInterval(loadComandas, 10000)
    return () => clearInterval(interval)
  }, [setComandas])

  const getStatusStyle = (status: Comanda['status']) => {
    switch (status) {
      case 'LIVRE': return 'bg-white border-green-200 hover:border-green-400 hover:shadow-green-100'
      case 'BLOQUEADA': return 'bg-gray-100 border-gray-300 hover:border-gray-400'
      case 'EM_USO': return 'bg-blue-50 border-blue-200 hover:border-blue-400 hover:shadow-blue-100'
      default: return 'bg-gray-50 border-gray-200'
    }
  }

  if (loading && comandas.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 gap-2 animate-pulse">
        <CreditCard className="w-6 h-6" /> Carregando comandas...
      </div>
    )
  }

  if (error && comandas.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-500 gap-4">
        <AlertTriangle className="w-10 h-10" />
        <p>{error}</p>
        <button onClick={loadComandas} className="px-4 py-2 bg-red-100 hover:bg-red-200 rounded-lg text-red-700 font-bold transition-colors">
          Tentar Novamente
        </button>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {comandas.map((c) => (
          <div
            key={c.id}
            className={`
              relative flex flex-col justify-between p-4 h-32 rounded-xl border-2 transition-all shadow-sm group cursor-pointer
              ${getStatusStyle(c.status)}
            `}
            onClick={() => onSelectComanda(c)}
          >
            {/* Top Row: Icon + Code */}
            <div className="flex justify-between w-full items-start pointer-events-none">
              <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-full shadow-sm ${
                    c.status === 'LIVRE' ? 'bg-green-100 text-green-700' : 
                    c.status === 'BLOQUEADA' ? 'bg-gray-200 text-gray-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                      <CreditCard className="w-4 h-4" />
                  </div>
                  <span className={`font-bold text-xl ${
                    c.status === 'LIVRE' ? 'text-gray-700' : 
                    c.status === 'BLOQUEADA' ? 'text-gray-500' :
                    'text-blue-700'
                  }`}>
                  {c.codigo}
                  </span>
              </div>
            </div>

            {/* Bottom Row: Status */}
            <div className="mt-2 text-left w-full pointer-events-none">
               {c.status === 'EM_USO' ? (
                  <>
                    <div className="text-xs text-blue-600 font-bold uppercase tracking-wide mb-1 flex items-center gap-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        Em Uso
                    </div>
                  </>
               ) : c.status === 'BLOQUEADA' ? (
                  <div className="text-xs text-gray-500 font-bold uppercase tracking-wide flex items-center gap-1">
                     <AlertTriangle className="w-3 h-3" />
                     Bloqueada
                  </div>
               ) : (
                  <div className="text-xs text-green-600 font-bold uppercase tracking-wide flex items-center gap-1">
                     <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                     Livre
                  </div>
               )}
            </div>
          </div>
        ))}
      </div>
  )
}
