'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

type Deposito = {
  id: string
  nome: string
  codigo: string | null
  is_padrao: boolean
  is_virtual: boolean
  descricao: string | null
  is_active: boolean
}

export default function DepositosPage() {
  const [data, setData] = useState<Deposito[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState<string>('')
  const [ordering, setOrdering] = useState<string>('nome')
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams()
        params.set('page_size', String(pageSize))
        params.set('page', String(page))
        if (search) params.set('search', search)
        if (ordering) params.set('ordering', ordering)
        const res = await request.get<any>(`/depositos/?${params.toString()}`)
        setData(res?.results ?? res ?? [])
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar depósitos')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [search, ordering, page, pageSize])

  if (loading) return <div className="p-4">Carregando depósitos...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>

  const depositos = data ?? []

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Depósitos</h1>
      <div className="grid grid-cols-5 gap-2 mb-3">
        <input
          placeholder="Buscar por nome/código"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <select value={ordering} onChange={(e) => setOrdering(e.target.value)} className="border rounded px-3 py-2">
          <option value="nome">Ordenar: Nome</option>
          <option value="-is_padrao">Ordenar: Padrão primeiro</option>
          <option value="-created_at">Ordenar: Recentes</option>
        </select>
        <div></div>
        <div className="flex items-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="border rounded px-3 py-2 disabled:opacity-60"
          >
            Anterior
          </button>
          <span className="text-sm">Página {page}</span>
          <button
            disabled={(depositos.length ?? 0) < pageSize}
            onClick={() => setPage((p) => p + 1)}
            className="border rounded px-3 py-2 disabled:opacity-60"
          >
            Próxima
          </button>
          <select
            value={pageSize}
            onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
            className="border rounded px-3 py-2"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border">Nome</th>
            <th className="text-left p-2 border">Código</th>
            <th className="text-left p-2 border">Padrão</th>
            <th className="text-left p-2 border">Virtual</th>
            <th className="text-left p-2 border">Status</th>
          </tr>
        </thead>
        <tbody>
          {depositos.map((d) => (
            <tr key={d.id}>
              <td className="p-2 border">{d.nome}</td>
              <td className="p-2 border">{d.codigo ?? '-'}</td>
              <td className="p-2 border">{d.is_padrao ? 'Sim' : 'Não'}</td>
              <td className="p-2 border">{d.is_virtual ? 'Sim' : 'Não'}</td>
              <td className="p-2 border">{d.is_active ? 'Ativo' : 'Inativo'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

