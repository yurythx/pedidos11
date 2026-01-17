'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../src/lib/http/request'

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

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p className="mt-2 text-sm">Resumo do dia</p>
      {loading && <div className="mt-3">Carregando...</div>}
      {error && <div className="mt-3 text-red-600">{error}</div>}
      {!loading && !error && data && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.keys(data).map((key) => (
            <div key={key} className="border rounded p-3">
              <div className="text-xs text-gray-600">{key}</div>
              <div className="text-lg font-semibold">
                {typeof data[key] === 'number' ? new Intl.NumberFormat('pt-BR').format(data[key]) : String(data[key])}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

