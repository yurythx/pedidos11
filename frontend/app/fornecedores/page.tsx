'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Fornecedor } from '../../src/types'
import Link from 'next/link'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, Edit, Trash2 } from 'lucide-react'

export default function FornecedoresPage() {
  const [data, setData] = useState<Paginacao<Fornecedor> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

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

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const onDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este fornecedor?')) return
    try {
      await request.delete(`/fornecedores/${id}/`)
      fetchData()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir')
    }
  }

  const fornecedores = data?.results ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Fornecedores</h1>
          <p className="text-gray-500 mt-1">Gerencie seus fornecedores e parceiros</p>
        </div>
        <Link href="/fornecedores/novo" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Novo Fornecedor
        </Link>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando fornecedores...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Documento</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {fornecedores.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                    Nenhum fornecedor encontrado.
                  </TableCell>
                </TableRow>
              ) : (
                fornecedores.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell><div className="font-medium text-gray-900">{f.nome}</div></TableCell>
                    <TableCell>{f.cpf_cnpj ?? '-'}</TableCell>
                    <TableCell>{f.email ?? '-'}</TableCell>
                    <TableCell>{f.telefone ?? '-'}</TableCell>
                    <TableCell className="text-right">
                       <div className="flex items-center justify-end gap-2">
                          <Link 
                            href={`/fornecedores/${f.id}`}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => onDelete(f.id)}
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
            hasMore={!!data?.next}
          />
        </>
      )}
    </div>
  )
}
