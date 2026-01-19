'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../src/lib/http/request'
import { 
  DollarSign, 
  ShoppingBag, 
  TrendingUp, 
  Users, 
  Calendar,
  AlertCircle
} from 'lucide-react'
import { formatBRL } from '../src/utils/currency'

export default function DashboardPage() {
  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await request.get<any>('/dashboard/resumo-dia/')
        setData(res)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar resumo do dia')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Mapeamento de chaves para labels e ícones amigáveis
  const kpiMap: Record<string, { label: string, icon: React.ElementType, color: string }> = {
    'total_vendas': { label: 'Vendas Hoje', icon: DollarSign, color: 'text-green-600 bg-green-50' },
    'qtd_pedidos': { label: 'Pedidos Realizados', icon: ShoppingBag, color: 'text-blue-600 bg-blue-50' },
    'ticket_medio': { label: 'Ticket Médio', icon: TrendingUp, color: 'text-purple-600 bg-purple-50' },
    'novos_clientes': { label: 'Novos Clientes', icon: Users, color: 'text-orange-600 bg-orange-50' },
  }

  const formatValue = (key: string, value: any) => {
    if (key === 'total_vendas' || key === 'ticket_medio') return formatBRL(Number(value))
    return value
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Dashboard</h1>
          <p className="text-gray-500 mt-1 flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Resumo do dia de hoje
          </p>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-100 rounded-2xl"></div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* KPIs Grid */}
      {!loading && !error && data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.keys(data).map((key) => {
            // Se tiver no mapa usa, senão cria genérico
            const config = kpiMap[key] || { 
              label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), 
              icon: Calendar, 
              color: 'text-gray-600 bg-gray-50' 
            }
            const Icon = config.icon

            return (
              <div key={key} className="card hover:shadow-md transition-shadow duration-200">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-1">{config.label}</p>
                    <h3 className="text-2xl font-bold text-gray-900">
                      {formatValue(key, data[key])}
                    </h3>
                  </div>
                  <div className={`p-3 rounded-xl ${config.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
      
      {!loading && !error && (!data || Object.keys(data).length === 0) && (
        <div className="text-center py-12 bg-white rounded-2xl border border-gray-100">
           <p className="text-gray-500">Nenhum dado disponível para hoje.</p>
        </div>
      )}
    </div>
  )
}

