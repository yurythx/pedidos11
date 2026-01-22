'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Movimentacao } from '../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Filter, Search } from 'lucide-react'
import { formatBRL } from '../../src/utils/currency'

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
  }, [page, pageSize, ordering, tipo])

  const movimentacoes = data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Movimentações</h1>
          <p className="text-gray-500 mt-1">Histórico de entradas, saídas e transferências</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select 
            value={tipo} 
            onChange={(e) => setTipo(e.target.value)} 
            className="input pl-10"
          >
            <option value="TODOS">Todas as Movimentações</option>
            <option value="ENTRADA">Entrada</option>
            <option value="SAIDA">Saída</option>
            <option value="TRANSFERENCIA">Transferência</option>
          </select>
        </div>
        <div className="relative md:col-span-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            placeholder="Filtrar por nome do produto"
            value={produto}
            onChange={(e) => setProduto(e.target.value)}
            className="input pl-10"
          />
        </div>
        <button onClick={() => { setPage(1); load() }} className="btn btn-primary w-full">
           Filtrar
        </button>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando movimentações...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Produto</TableHead>
                <TableHead>Origem/Lote</TableHead>
                <TableHead>Qtd</TableHead>
                <TableHead>Valor Total</TableHead>
                <TableHead>Documento</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {movimentacoes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                    Nenhuma movimentação encontrada.
                  </TableCell>
                </TableRow>
              ) : (
                movimentacoes.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell>
                      <div className="text-xs text-gray-500">
                        {new Date(m.created_at).toLocaleDateString('pt-BR')}
                      </div>
                      <div className="text-xs font-medium text-gray-700">
                        {new Date(m.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={`
                        px-2 py-1 rounded-full text-xs font-bold
                        ${m.tipo === 'ENTRADA' ? 'bg-green-100 text-green-700' : 
                          m.tipo === 'SAIDA' ? 'bg-red-100 text-red-700' : 
                          'bg-blue-100 text-blue-700'}
                      `}>
                        {m.tipo}
                      </span>
                    </TableCell>
                    <TableCell><div className="font-medium text-gray-900">{m.produto_nome}</div></TableCell>
                    <TableCell>
                      <div className="text-sm">{m.deposito_nome}</div>
                      {m.lote_codigo && <div className="text-xs text-gray-500 font-mono">Lote: {m.lote_codigo}</div>}
                    </TableCell>
                    <TableCell>
                      <span className={m.tipo === 'SAIDA' ? 'text-red-600 font-bold' : 'text-green-600 font-bold'}>
                        {m.tipo === 'SAIDA' ? '-' : '+'}{m.quantidade}
                      </span>
                    </TableCell>
                    <TableCell className="font-medium">{formatBRL(m.valor_total)}</TableCell>
                    <TableCell>{m.documento ?? '-'}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <TablePagination
            page={page}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
            hasMore={movimentacoes.length >= pageSize}
          />
        </>
      )}
    </div>
  )
}

