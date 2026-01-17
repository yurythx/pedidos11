'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao } from '../../src/types'

type ProdutoList = {
  id: string
  nome: string
  sku: string | null
  codigo_barras: string | null
  categoria: string | null
  categoria_nome: string | null
  tipo: 'COMUM' | 'COMPOSTO' | 'INSUMO'
  tipo_display: string
  preco_venda: number
  preco_custo: number | null
  destaque: boolean
  is_active: boolean
}

export default function ProdutosPage() {
  const [data, setData] = useState<Paginacao<ProdutoList> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [tipo, setTipo] = useState<string>('TODOS')
  const [precoMin, setPrecoMin] = useState<string>('')
  const [precoMax, setPrecoMax] = useState<string>('')
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)
  const [ordering, setOrdering] = useState<string>('nome')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (tipo && tipo !== 'TODOS') params.set('tipo', tipo)
      if (precoMin) params.set('preco_min', precoMin)
      if (precoMax) params.set('preco_max', precoMax)
      params.set('page_size', String(pageSize))
      params.set('page', String(page))
      if (ordering) params.set('ordering', ordering)
      const res = await request.get<Paginacao<ProdutoList>>(`/produtos/?${params.toString()}`)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar produtos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, ordering])

  const produtos = useMemo(() => data?.results ?? [], [data])

  const onRecalcularCusto = async (id: string) => {
    try {
      await request.post<any>(`/produtos/${id}/recalcular_custo/`)
      await load()
    } catch (err) {
      console.error(err)
      alert('Erro ao recalcular custo')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Produtos</h1>
      <div className="grid grid-cols-6 gap-2 mb-3">
        <input
          placeholder="Buscar por nome, SKU ou código de barras"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded px-3 py-2 col-span-2"
        />
        <select value={tipo} onChange={(e) => setTipo(e.target.value)} className="border rounded px-3 py-2">
          <option value="TODOS">Todos</option>
          <option value="COMUM">Comum</option>
          <option value="COMPOSTO">Composto</option>
          <option value="INSUMO">Insumo</option>
        </select>
        <input
          placeholder="Preço mín."
          value={precoMin}
          onChange={(e) => setPrecoMin(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <input
          placeholder="Preço máx."
          value={precoMax}
          onChange={(e) => setPrecoMax(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <select value={ordering} onChange={(e) => setOrdering(e.target.value)} className="border rounded px-3 py-2">
          <option value="nome">Ordenar: Nome</option>
          <option value="preco_venda">Ordenar: Preço</option>
          <option value="-created_at">Ordenar: Recentes</option>
        </select>
        <button onClick={() => { setPage(1); load() }} className="bg-black text-white rounded px-3 py-2">Filtrar</button>
      </div>
      {loading && <div>Carregando produtos...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border">Nome</th>
              <th className="text-left p-2 border">Categoria</th>
              <th className="text-left p-2 border">Tipo</th>
              <th className="text-left p-2 border">Preço Venda</th>
              <th className="text-left p-2 border">Preço Custo</th>
              <th className="text-left p-2 border">Ações</th>
            </tr>
          </thead>
          <tbody>
            {produtos.map((p) => (
              <tr key={p.id}>
                <td className="p-2 border">{p.nome}</td>
                <td className="p-2 border">{p.categoria_nome ?? '-'}</td>
                <td className="p-2 border">{p.tipo_display}</td>
                <td className="p-2 border">R$ {Number(p.preco_venda).toFixed(2)}</td>
                <td className="p-2 border">{p.preco_custo != null ? `R$ ${Number(p.preco_custo).toFixed(2)}` : '-'}</td>
                <td className="p-2 border">
                  {p.tipo === 'COMPOSTO' && (
                    <button
                      onClick={() => onRecalcularCusto(p.id)}
                      className="text-sm underline"
                    >
                      Recalcular Custo
                    </button>
                  )}
                </td>
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
            disabled={(data?.results?.length ?? 0) < pageSize}
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
      )}
    </div>
  )
}

