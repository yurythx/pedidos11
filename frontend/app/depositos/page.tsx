'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, Search, Filter, Edit, Trash2 } from 'lucide-react'
import Link from 'next/link'

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

  useEffect(() => {
    load()
  }, [search, ordering, page, pageSize])

  const onDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este depósito?')) return
    try {
      await request.delete(`/depositos/${id}/`)
      load()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir')
    }
  }

  const depositos = data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Depósitos</h1>
          <p className="text-gray-500 mt-1">Gerencie os locais de estoque da sua empresa</p>
        </div>
        <Link href="/depositos/novo" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Novo Depósito
        </Link>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            placeholder="Buscar por nome ou código"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="w-full md:w-56 relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select 
            value={ordering} 
            onChange={(e) => setOrdering(e.target.value)} 
            className="input pl-10 appearance-none"
          >
            <option value="nome">Ordenar: Nome</option>
            <option value="-is_padrao">Ordenar: Padrão primeiro</option>
            <option value="-created_at">Ordenar: Recentes</option>
          </select>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando depósitos...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Código</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {depositos.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                    Nenhum depósito encontrado.
                  </TableCell>
                </TableRow>
              ) : (
                depositos.map((d) => (
                  <TableRow key={d.id}>
                    <TableCell>
                      <div className="font-medium text-gray-900">{d.nome}</div>
                      {d.descricao && <div className="text-xs text-gray-500 mt-0.5">{d.descricao}</div>}
                    </TableCell>
                    <TableCell>{d.codigo ?? '-'}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {d.is_padrao && (
                          <span className="px-2 py-1 bg-amber-50 text-amber-700 text-xs font-bold rounded-full">
                            Padrão
                          </span>
                        )}
                        {d.is_virtual && (
                          <span className="px-2 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full">
                            Virtual
                          </span>
                        )}
                        {!d.is_padrao && !d.is_virtual && (
                           <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-bold rounded-full">
                            Físico
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {d.is_active ? (
                        <span className="text-green-600 text-sm font-medium flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Ativo
                        </span>
                      ) : (
                        <span className="text-red-600 text-sm font-medium flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span> Inativo
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                       <div className="flex items-center justify-end gap-2">
                          <Link 
                            href={`/depositos/${d.id}`}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => onDelete(d.id)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Excluir"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                    </TableCell>
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
            hasMore={depositos.length >= pageSize}
          />
        </>
      )}
    </div>
  )
}
