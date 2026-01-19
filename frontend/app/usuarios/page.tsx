'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Usuario } from '../../src/types'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, User, Trash2, Edit } from 'lucide-react'

export default function UsuariosPage() {
  const router = useRouter()
  const [data, setData] = useState<Paginacao<Usuario> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Estado de paginação
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<Paginacao<Usuario>>(`/usuarios/?page=${page}&page_size=${pageSize}`)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar usuários')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return
    try {
      await request.delete(`/usuarios/${id}/`)
      fetchData() // Recarrega
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir usuário')
    }
  }

  const usuarios = data?.results ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Gerenciar Usuários</h1>
          <p className="text-gray-500 mt-1">Administre os usuários e permissões do sistema</p>
        </div>
        <div className="flex gap-3">
            <Link 
                href="/perfil" 
                className="btn btn-secondary"
            >
                <User className="w-4 h-4 mr-2" />
                Meu Perfil
            </Link>
            <Link 
                href="/usuarios/novo" 
                className="btn btn-primary"
            >
                <Plus className="w-5 h-5 mr-2" />
                Novo Usuário
            </Link>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando usuários...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Cargo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {usuarios.length === 0 ? (
                  <TableRow>
                      <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                          Nenhum usuário encontrado.
                      </TableCell>
                  </TableRow>
              ) : (
                  usuarios.map((u) => (
                    <TableRow key={u.id}>
                      <TableCell>
                        <div className="font-medium text-gray-900">{[u.first_name, u.last_name].filter(Boolean).join(' ') || '-'}</div>
                      </TableCell>
                      <TableCell className="text-gray-600">{u.username}</TableCell>
                      <TableCell className="text-gray-600">{u.email ?? '-'}</TableCell>
                      <TableCell>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-full">
                          {u.cargo}
                        </span>
                      </TableCell>
                      <TableCell>
                        {u.is_active ? (
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
                            href={`/usuarios/${u.id}`}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(u.id)}
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
