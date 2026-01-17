'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Fornecedor } from '../../src/types'

export default function FornecedoresPage() {
  const [data, setData] = useState<Paginacao<Fornecedor> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await request.get<Paginacao<Fornecedor>>(`/fornecedores/?page_size=${pageSize}&page=${page}`)
        setData(res)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar fornecedores')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [page, pageSize])

  if (loading) return <div className="p-4">Carregando fornecedores...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>

  const fornecedores = data?.results ?? []

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Fornecedores</h1>
      <div className="mb-3 flex items-center gap-2">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          className="border rounded px-3 py-2 disabled:opacity-60"
        >
          Anterior
        </button>
        <span className="text-sm">Página {page}</span>
        <button
          disabled={(fornecedores.length ?? 0) < pageSize}
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
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border">Nome</th>
            <th className="text-left p-2 border">Documento</th>
            <th className="text-left p-2 border">Email</th>
            <th className="text-left p-2 border">Telefone</th>
          </tr>
        </thead>
        <tbody>
          {fornecedores.map((f) => (
            <tr key={f.id}>
              <td className="p-2 border">{f.nome}</td>
              <td className="p-2 border">{f.cpf_cnpj ?? '-'}</td>
              <td className="p-2 border">{f.email ?? '-'}</td>
              <td className="p-2 border">{f.telefone ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

