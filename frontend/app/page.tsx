'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../src/lib/http/request'
import { 
  DollarSign, 
  ShoppingBag, 
  TrendingUp, 
  Calendar,
  AlertCircle,
  ArrowUpCircle,
  BarChart3,
  Award
} from 'lucide-react'
import { formatBRL } from '../src/utils/currency'

interface DashboardData {
  total_vendas: string
  qtd_pedidos: number
  ticket_medio: string
  contas_receber_hoje: string
  contas_pagar_hoje: string
  ranking_produtos: Array<{
    produto: string
    quantidade: string
    valor_total: string
  }>
  vendas_por_hora: Array<{
    hora: number
    total: string
  }>
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const res = await request.get<DashboardData>('/dashboard/resumo-dia/')
        setData(res)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar resumo do dia')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const kpiMap = [
    { key: 'total_vendas', label: 'Vendas Hoje', icon: DollarSign, color: 'text-green-600 bg-green-50' },
    { key: 'qtd_pedidos', label: 'Pedidos', icon: ShoppingBag, color: 'text-blue-600 bg-blue-50' },
    { key: 'ticket_medio', label: 'Ticket Médio', icon: TrendingUp, color: 'text-purple-600 bg-purple-50' },
    { key: 'contas_receber_hoje', label: 'A Receber', icon: ArrowUpCircle, color: 'text-teal-600 bg-teal-50' },
  ]

  const formatValue = (key: string, value: any) => {
    if (['total_vendas', 'ticket_medio', 'contas_receber_hoje', 'contas_pagar_hoje'].includes(key)) {
      return formatBRL(Number(value))
    }
    return value
  }

  // Helper para o gráfico de barras CSS
  const getMaxVendaHora = () => {
    if (!data?.vendas_por_hora.length) return 1
    return Math.max(...data.vendas_por_hora.map(i => Number(i.total)))
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500 text-sm flex items-center gap-2">
            <Calendar className="w-4 h-4" /> Resumo de Hoje
          </p>
        </div>
      </div>

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
            {[1,2,3,4].map(i => <div key={i} className="h-32 bg-gray-100 rounded-xl" />)}
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-2 border border-red-100">
          <AlertCircle size={20} /> {error}
        </div>
      )}

      {data && !loading && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {kpiMap.map((kpi) => (
              <div key={kpi.key} className="card p-4 hover:shadow-md transition-all border border-base-200">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-gray-500">{kpi.label}</p>
                    <h3 className="text-2xl font-bold text-gray-900 mt-1">
                      {formatValue(kpi.key, (data as any)[kpi.key])}
                    </h3>
                  </div>
                  <div className={`p-3 rounded-xl ${kpi.color}`}>
                    <kpi.icon className="w-6 h-6" />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Vendas por Hora (Chart) */}
            <div className="card p-6 border border-base-200 shadow-sm">
              <h3 className="font-bold text-lg text-gray-800 mb-6 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-500" />
                Vendas por Hora
              </h3>
              
              <div className="h-48 flex items-end gap-2">
                {data.vendas_por_hora.length === 0 ? (
                  <div className="w-full text-center text-gray-400 text-sm self-center">
                    Nenhuma venda registrada hoje
                  </div>
                ) : (
                  Array.from({ length: 24 }).map((_, hora) => {
                    const venda = data.vendas_por_hora.find(v => v.hora === hora)
                    const total = venda ? Number(venda.total) : 0
                    const max = getMaxVendaHora()
                    const height = max > 0 ? (total / max) * 100 : 0
                    
                    return (
                      <div key={hora} className="flex-1 flex flex-col justify-end group relative">
                        {total > 0 && (
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10 shadow-lg">
                            {formatBRL(total)}
                          </div>
                        )}
                        <div 
                          className={`w-full rounded-t-sm transition-all duration-500 ${total > 0 ? 'bg-blue-500 hover:bg-blue-600 cursor-pointer' : 'bg-gray-100'}`}
                          style={{ height: `${total > 0 ? Math.max(height, 5) : 5}%` }}
                        ></div>
                        <span className="text-[10px] text-gray-400 text-center mt-1 select-none">
                          {hora % 3 === 0 ? `${hora}h` : ''}
                        </span>
                      </div>
                    )
                  })
                )}
              </div>
            </div>

            {/* Ranking Produtos */}
            <div className="card p-6 border border-base-200 shadow-sm">
              <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-500" />
                Top 5 Produtos
              </h3>
              
              <div className="space-y-4">
                {data.ranking_produtos.length === 0 ? (
                  <div className="text-center text-gray-400 text-sm py-10">
                    Nenhum produto vendido hoje
                  </div>
                ) : (
                  data.ranking_produtos.map((prod, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold 
                          ${idx === 0 ? 'bg-yellow-100 text-yellow-700' : 
                            idx === 1 ? 'bg-gray-200 text-gray-700' : 
                            idx === 2 ? 'bg-orange-100 text-orange-700' : 'bg-white text-gray-500 border border-gray-200'}`}>
                          {idx + 1}
                        </span>
                        <div>
                          <p className="font-medium text-gray-800">{prod.produto}</p>
                          <p className="text-xs text-gray-500">{Number(prod.quantidade)} unidades</p>
                        </div>
                      </div>
                      <span className="font-bold text-gray-900">
                        {formatBRL(Number(prod.valor_total))}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
