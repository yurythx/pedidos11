'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../../src/lib/http/request'
import type { Paginacao, Movimentacao } from '../../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../../src/components/ui/Table'
import { ArrowLeft, Search, Filter } from 'lucide-react'
import { formatBRL } from '../../../src/utils/currency'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function HistoricoComprasPage() {
  const router = useRouter()
  const [data, setData] = useState<Paginacao<Movimentacao> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)
  const [searchDoc, setSearchDoc] = useState('')
  const [searchProd, setSearchProd] = useState('')

  const loadMovimentacoes = async () => {
    setLoading(true)
    setError(null)
    try {
      let url = `/movimentacoes/?tipo=ENTRADA&page_size=${pageSize}&page=${page}`
      if (searchDoc) url += `&documento=${encodeURIComponent(searchDoc)}`
      if (searchProd) url += `&produto_nome=${encodeURIComponent(searchProd)}`
      
      const res = await request.get<Paginacao<Movimentacao>>(url)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar histórico')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMovimentacoes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadMovimentacoes()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/compras" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-600" />
          </Link>
          <h1 className="heading-1">Histórico de Compras / Entradas</h1>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por NFe / Documento..."
              className="w-full pl-10 input"
              value={searchDoc}
              onChange={e => setSearchDoc(e.target.value)}
            />
          </div>
          <div className="flex-1 relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por Produto..."
              className="w-full pl-10 input"
              value={searchProd}
              onChange={e => setSearchProd(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Filtrar
          </button>
        </form>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando histórico...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      
      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Documento</TableHead>
                <TableHead>Produto</TableHead>
                <TableHead>Lote</TableHead>
                <TableHead>Qtd</TableHead>
                <TableHead>Custo Unit.</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Depósito</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.results ?? []).map((m) => (
                <TableRow key={m.id} className="hover:bg-gray-50">
                  <TableCell className="text-sm">
                    {new Date(m.created_at).toLocaleDateString('pt-BR')} <br/>
                    <span className="text-xs text-gray-400">{new Date(m.created_at).toLocaleTimeString('pt-BR')}</span>
                  </TableCell>
                  <TableCell>
                    {m.documento ? (
                      <span className="font-mono font-medium text-blue-600">{m.documento}</span>
                    ) : (
                      <span className="text-gray-400 italic">Sem doc</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-gray-900">{m.produto_nome}</div>
                  </TableCell>
                  <TableCell>
                    {m.lote_codigo ? (
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-mono">
                        {m.lote_codigo}
                      </span>
                    ) : '-'}
                  </TableCell>
                  <TableCell className="font-medium text-green-700">+{m.quantidade}</TableCell>
                  <TableCell>{formatBRL(m.valor_unitario)}</TableCell>
                  <TableCell className="font-bold">{formatBRL(m.valor_total)}</TableCell>
                  <TableCell className="text-sm text-gray-500">{m.deposito_nome}</TableCell>
                </TableRow>
              ))}
              {(data?.results ?? []).length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    Nenhuma movimentação de entrada encontrada.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          <TablePagination
            page={page}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
            hasMore={(data?.results?.length ?? 0) >= pageSize} // Simplified logic
          />
        </>
      )}
    </div>
  )
}
