'use client'
import React, { useEffect, useState, useCallback } from 'react'
import { request } from '../../src/lib/http/request'
import { Clock, CheckCircle, ChefHat, AlertCircle, RefreshCw, Play, X } from 'lucide-react'

interface KdsItem {
  id: string
  produto: string
  quantidade: number
  status: 'PENDENTE' | 'EM_PREPARO' | 'PRONTO' | 'ENTREGUE'
  observacoes?: string
  complementos: string[]
}

interface KdsOrder {
  venda_id: string
  identificacao: string
  inicio: string // ISO date
  itens: KdsItem[]
}

export default function KdsPage() {
  const [orders, setOrders] = useState<KdsOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [setorId, setSetorId] = useState<string>('')

  const load = useCallback(async () => {
    try {
      setError(null)
      const url = setorId ? `/kds/?setor_id=${setorId}` : '/kds/'
      const res = await request.get<KdsOrder[]>(url)
      setOrders(res)
      setLastUpdated(new Date())
    } catch (err: any) {
      console.error(err)
      setError('Erro ao carregar pedidos. Verifique se o servidor está rodando.')
    } finally {
      setLoading(false)
    }
  }, [setorId])

  useEffect(() => {
    load()
    const interval = setInterval(load, 5000) // 5s refresh
    return () => clearInterval(interval)
  }, [load])

  const avancarItem = async (itemId: string) => {
    try {
        await request.post(`/kds/${itemId}/avancar/`)
        load()
    } catch (e) {
        // Optimistic update failed, reload
        load()
    }
  }

  const getTimeDiff = (dateStr: string) => {
    const start = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - start.getTime()
    return Math.floor(diffMs / 60000)
  }

  const getCardColor = (minutes: number) => {
      if (minutes > 30) return 'bg-red-50 border-red-200'
      if (minutes > 15) return 'bg-yellow-50 border-yellow-200'
      return 'bg-white border-gray-200'
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-800">
            <ChefHat className="text-orange-600 w-8 h-8" /> 
            <span>KDS - Produção</span>
        </h1>
        <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="hidden md:inline">Atualizado: {lastUpdated.toLocaleTimeString()}</span>
            <button 
                onClick={load} 
                className="p-2 bg-gray-100 rounded-full shadow-sm hover:bg-gray-200 transition-colors"
                title="Atualizar"
            >
                <RefreshCw size={20} className={loading ? 'animate-spin text-primary' : 'text-gray-600'} />
            </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-xl mb-6 flex items-center gap-2 border border-red-200 shadow-sm">
            <AlertCircle size={20} />
            {error}
        </div>
      )}

      {/* Grid de Pedidos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
        {orders.map(order => {
            const waitTime = getTimeDiff(order.inicio)
            return (
                <div key={order.venda_id} className={`rounded-xl border shadow-sm flex flex-col overflow-hidden transition-all duration-300 ${getCardColor(waitTime)}`}>
                    {/* Header do Cartão */}
                    <div className="p-3 border-b border-gray-200/50 flex justify-between items-center bg-white/50 backdrop-blur-sm">
                        <span className="font-bold text-lg text-gray-800">{order.identificacao}</span>
                        <div className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full shadow-sm ${waitTime > 30 ? 'bg-red-100 text-red-700 animate-pulse' : 'bg-gray-100 text-gray-600'}`}>
                            <Clock size={12} /> {waitTime} min
                        </div>
                    </div>

                    {/* Lista de Itens */}
                    <div className="flex-1 p-3 space-y-3 overflow-y-auto max-h-[400px] custom-scrollbar">
                        {order.itens.map(item => (
                            <div key={item.id} className="flex flex-col gap-1 border-b border-dashed border-gray-200 last:border-0 pb-2 last:pb-0 group">
                                <div className="flex justify-between items-start gap-2">
                                    <span className="font-bold text-gray-800 leading-tight flex-1 text-sm">
                                        <span className="text-lg mr-1">{item.quantidade}x</span> {item.produto}
                                    </span>
                                    
                                    {/* Botão de Ação por Item */}
                                    <button 
                                        onClick={() => avancarItem(item.id)}
                                        className={`p-2 rounded-lg transition-all shadow-sm flex-shrink-0 transform active:scale-90
                                            ${item.status === 'PENDENTE' ? 'bg-blue-100 text-blue-700 hover:bg-blue-200 hover:shadow-md' : 
                                              item.status === 'EM_PREPARO' ? 'bg-orange-100 text-orange-700 hover:bg-orange-200 hover:shadow-md' : 
                                              'bg-green-100 text-green-700'}
                                        `}
                                        title={item.status === 'PENDENTE' ? 'Iniciar Preparo' : item.status === 'EM_PREPARO' ? 'Marcar Pronto' : 'Entregue'}
                                    >
                                        {item.status === 'PENDENTE' ? <Play size={16} fill="currentColor" /> : 
                                         item.status === 'EM_PREPARO' ? <ChefHat size={16} /> : 
                                         <CheckCircle size={16} />}
                                    </button>
                                </div>
                                
                                {item.observacoes && (
                                    <div className="text-xs bg-yellow-100 text-yellow-800 p-2 rounded border border-yellow-200 font-medium">
                                        📝 {item.observacoes}
                                    </div>
                                )}
                                
                                {item.complementos.length > 0 && (
                                    <ul className="text-xs text-gray-500 pl-2 border-l-2 border-gray-300 ml-1">
                                        {item.complementos.map((c, i) => <li key={i}>{c}</li>)}
                                    </ul>
                                )}

                                <div className={`text-[10px] uppercase font-bold tracking-wider mt-1 
                                    ${item.status === 'PENDENTE' ? 'text-blue-500' : 
                                      item.status === 'EM_PREPARO' ? 'text-orange-500' : 'text-green-600'}
                                `}>
                                    {item.status.replace('_', ' ')}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )
        })}
        
        {orders.length === 0 && !loading && (
            <div className="col-span-full flex flex-col items-center justify-center py-20 text-gray-400 opacity-60">
                <div className="bg-white p-8 rounded-full shadow-sm mb-6">
                    <ChefHat size={64} className="text-gray-300" />
                </div>
                <h2 className="text-2xl font-bold text-gray-500">Cozinha em dia!</h2>
                <p className="text-gray-400 mt-2">Nenhum pedido pendente na fila.</p>
            </div>
        )}
      </div>
    </div>
  )
}
