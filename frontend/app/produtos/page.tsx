'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Produto } from '../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Search, Filter, Plus, Edit, Trash2 } from 'lucide-react'
import { formatBRL } from '../../src/utils/currency'
import Link from 'next/link'

export default function ProdutosPage() {
  const [data, setData] = useState<Paginacao<Produto> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [tipo, setTipo] = useState<string>('TODOS')
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)
  
  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (tipo && tipo !== 'TODOS') params.set('tipo', tipo)
      params.set('page_size', String(pageSize))
      params.set('page', String(page))
      const res = await request.get<Paginacao<Produto>>(`/produtos/?${params.toString()}`)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar produtos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [page, pageSize, search, tipo])

  const onDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este produto?')) return
    try {
      await request.delete(`/produtos/${id}/`)
      load()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir')
    }
  }

  const onRecalcularCusto = async (id: string) => {
    try {
      await request.post<any>(`/produtos/${id}/recalcular_custo/`)
      await load()
      alert('Custo recalculado com sucesso!')
    } catch (err) {
      console.error(err)
      alert('Erro ao recalcular custo')
    }
  }

  const produtos = useMemo(() => data?.results ?? [], [data])

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="heading-1">Produtos</h1>
        <Link href="/produtos/novo" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Novo Produto
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            placeholder="Buscar por nome, SKU ou código de barras"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="w-full md:w-48 relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select 
            value={tipo} 
            onChange={(e) => setTipo(e.target.value)} 
            className="input pl-10 appearance-none"
          >
            <option value="TODOS">Todos os Tipos</option>
            <option value="COMUM">Comum</option>
            <option value="COMPOSTO">Composto</option>
            <option value="INSUMO">Insumo</option>
          </select>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando produtos...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      
      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Preço Venda</TableHead>
                <TableHead>Preço Custo</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {produtos.map((p) => (
                <TableRow key={p.id}>
                  <TableCell>
                    <div className="font-medium text-gray-900">{p.nome}</div>
                    {(p.sku || p.codigo_barras) && (
                      <div className="text-xs text-gray-500">
                        {p.sku && <span className="mr-2">SKU: {p.sku}</span>}
                        {p.codigo_barras && <span>EAN: {p.codigo_barras}</span>}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>{p.categoria_nome ?? '-'}</TableCell>
                  <TableCell>
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-medium
                      ${p.tipo === 'INSUMO' ? 'bg-blue-50 text-blue-700' : 
                        p.tipo === 'COMPOSTO' ? 'bg-purple-50 text-purple-700' : 
                        'bg-gray-100 text-gray-700'}
                    `}>
                      {p.tipo_display}
                    </span>
                  </TableCell>
                  <TableCell>{formatBRL(p.preco_venda)}</TableCell>
                  <TableCell>{p.preco_custo != null ? formatBRL(p.preco_custo) : '-'}</TableCell>
                  <TableCell className="text-right">
                     <div className="flex items-center justify-end gap-2">
                        {p.tipo === 'COMPOSTO' && (
                          <button 
                            className="text-xs text-primary hover:underline font-medium mr-2"
                            onClick={() => onRecalcularCusto(p.id)}
                            title="Recalcular Custo"
                          >
                            Recalcular
                          </button>
                        )}
                        <Link 
                          href={`/produtos/${p.id}`}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => onDelete(p.id)}
                          className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Excluir"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          <TablePagination
            page={page}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
            hasMore={(data?.results?.length ?? 0) >= pageSize}
          />
        </>
      )}
    </div>
  )
}
