'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Cliente } from '../../src/types'
import Link from 'next/link'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, Edit, Trash2, MapPin } from 'lucide-react'

export default function ClientesPage() {
  const [data, setData] = useState<Paginacao<Cliente> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<Paginacao<Cliente>>(`/clientes/?page_size=${pageSize}&page=${page}`)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar clientes')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const onDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este cliente?')) return
    try {
      await request.delete(`/clientes/${id}/`)
      fetchData()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir')
    }
  }

  const clientes = data?.results ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="heading-1">Clientes</h1>
        <Link href="/clientes/novo" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Novo Cliente
        </Link>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando clientes...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Documento</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>Endereços</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clientes.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <div className="font-medium text-gray-900">{c.nome}</div>
                  </TableCell>
                  <TableCell>{c.cpf_cnpj ?? '-'}</TableCell>
                  <TableCell>{c.email ?? '-'}</TableCell>
                  <TableCell>{c.telefone ?? '-'}</TableCell>
                  <TableCell>
                    <Link 
                      href={`/clientes/${c.id}/enderecos`} 
                      className="text-sm text-gray-500 hover:text-primary hover:underline font-medium flex items-center gap-1"
                    >
                      <MapPin className="w-3 h-3" /> Gerenciar
                    </Link>
                  </TableCell>
                  <TableCell className="text-right">
                     <div className="flex items-center justify-end gap-2">
                        <Link 
                          href={`/clientes/${c.id}`}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => onDelete(c.id)}
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
