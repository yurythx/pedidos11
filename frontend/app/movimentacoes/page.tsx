'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

type Movimentacao = {
  id: string
  produto_nome: string
  deposito_nome: string
  lote_codigo: string | null
  tipo: 'ENTRADA' | 'SAIDA' | 'TRANSFERENCIA'
  quantidade: number
  valor_unitario: number
  valor_total: number
  documento: string | null
  observacao: string | null
  created_at: string
}

export default function MovimentacoesPage() {
  const [data, setData] = useState<Movimentacao[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tipo, setTipo] = useState<string>('TODOS')
  const [produto, setProduto] = useState<string>('')
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)
  const [ordering, setOrdering] = useState<string>('-created_at')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.set('page_size', String(pageSize))
      params.set('page', String(page))
      if (ordering) params.set('ordering', ordering)
      if (tipo !== 'TODOS') params.set('tipo', tipo)
      if (produto) params.set('produto_nome', produto)
      const res = await request.get<any>(`/movimentacoes/?${params.toString()}`)
      setData(res?.results ?? res ?? [])
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar movimentações')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, ordering, tipo, produto])

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Movimentações</h1>
      <div className="grid grid-cols-5 gap-2 mb-3">
        <select value={tipo} onChange={(e) => setTipo(e.target.value)} className="border rounded px-3 py-2">
          <option value="TODOS">Todos</option>
          <option value="ENTRADA">Entrada</option>
          <option value="SAIDA">Saída</option>
          <option value="TRANSFERENCIA">Transferência</option>
        </select>
        <input
          placeholder="Filtro por produto"
          value={produto}
          onChange={(e) => setProduto(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <select value={ordering} onChange={(e) => setOrdering(e.target.value)} className="border rounded px-3 py-2">
          <option value="-created_at">Ordenar: Recentes</option>
          <option value="created_at">Ordenar: Antigos</option>
        </select>
        <select
          value={pageSize}
          onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
          className="border rounded px-3 py-2"
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
        </select>
        <button onClick={() => { setPage(1); load() }} className="bg-black text-white rounded px-3 py-2">Filtrar</button>
      </div>
      {loading && <div>Carregando movimentações...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border">Data</th>
              <th className="text-left p-2 border">Tipo</th>
              <th className="text-left p-2 border">Produto</th>
              <th className="text-left p-2 border">Depósito</th>
              <th className="text-left p-2 border">Lote</th>
              <th className="text-left p-2 border">Quantidade</th>
              <th className="text-left p-2 border">Valor Unit.</th>
              <th className="text-left p-2 border">Valor Total</th>
              <th className="text-left p-2 border">Documento</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((m) => (
              <tr key={m.id}>
                <td className="p-2 border">{new Date(m.created_at).toLocaleString('pt-BR')}</td>
                <td className="p-2 border">{m.tipo}</td>
                <td className="p-2 border">{m.produto_nome}</td>
                <td className="p-2 border">{m.deposito_nome}</td>
                <td className="p-2 border">{m.lote_codigo ?? '-'}</td>
                <td className="p-2 border">{m.quantidade}</td>
                <td className="p-2 border">R$ {Number(m.valor_unitario).toFixed(2)}</td>
                <td className="p-2 border">R$ {Number(m.valor_total).toFixed(2)}</td>
                <td className="p-2 border">{m.documento ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {!loading && !error && (
        <div className="mt-3 flex items-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="border rounded px-3 py-2 disabled:opacity-60"
          >
            Anterior
          </button>
          <span className="text-sm">Página {page}</span>
          <button
            disabled={(data?.length ?? 0) < pageSize}
            onClick={() => setPage((p) => p + 1)}
            className="border rounded px-3 py-2 disabled:opacity-60"
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  )
}

