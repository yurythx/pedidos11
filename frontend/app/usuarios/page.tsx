'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Usuario } from '../../src/types'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, User, Trash2, Edit, Shield, ShieldAlert, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'

export default function UsuariosPage() {
  const router = useRouter()
  const [data, setData] = useState<Paginacao<Usuario> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
      toast.success('Usuário removido com sucesso!')
      fetchData()
    } catch (err: any) {
      toast.error(err?.message ?? 'Erro ao excluir usuário')
    }
  }

  const getCargoColor = (cargo: string) => {
    switch (cargo) {
      case 'ADMIN': return 'bg-red-50 text-red-700 border-red-100'
      case 'GERENTE': return 'bg-purple-50 text-purple-700 border-purple-100'
      case 'FINANCEIRO': return 'bg-green-50 text-green-700 border-green-100'
      default: return 'bg-blue-50 text-blue-700 border-blue-100'
    }
  }

  const usuarios = data?.results ?? []

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="heading-1">Equipe & Acessos</h1>
          <p className="text-gray-500 mt-1">Gerencie os colaboradores e defina seus níveis de permissão no sistema.</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/usuarios/novo"
            className="btn btn-primary shadow-lg shadow-primary/20"
          >
            <Plus className="w-5 h-5 mr-2" />
            Novo Colaborador
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <p className="text-gray-500 font-medium tracking-wide">Sincronizando equipe...</p>
          </div>
        )}

        {error && (
          <div className="p-8 text-center">
            <div className="bg-red-50 text-red-600 p-4 rounded-xl inline-flex items-center gap-3">
              <ShieldAlert className="w-5 h-5" />
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {!loading && !error && (
          <>
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-50/50">
                  <TableHead className="w-[300px]">Colaborador</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Nível de Acesso</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {usuarios.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-gray-500 py-16">
                      <div className="flex flex-col items-center gap-2">
                        <User className="w-12 h-12 text-gray-200" />
                        <p>Nenhum usuário cadastrado até o momento.</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  usuarios.map((u) => (
                    <TableRow key={u.id} className="hover:bg-gray-50/50 transition-colors">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-gray-600 font-bold border border-white shadow-sm">
                            {u.first_name?.[0] || u.username[0].toUpperCase()}
                          </div>
                          <div className="flex flex-col">
                            <span className="font-bold text-gray-900 leading-tight">
                              {[u.first_name, u.last_name].filter(Boolean).join(' ') || u.username}
                            </span>
                            <span className="text-xs text-gray-500">@{u.username}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-600 font-medium">{u.email ?? '-'}</TableCell>
                      <TableCell>
                        <span className={`px-3 py-1 border text-xs font-bold rounded-lg ${getCargoColor(u.cargo)}`}>
                          {u.cargo}
                        </span>
                      </TableCell>
                      <TableCell>
                        {u.is_active ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span> Ativo
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-500">
                            <span className="w-1.5 h-1.5 rounded-full bg-gray-400 mr-1.5"></span> Inativo
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Link
                            href={`/usuarios/${u.id}`}
                            className="p-2 text-gray-400 hover:text-primary hover:bg-red-50 rounded-xl transition-all"
                            title="Editar Perfil"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(u.id)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
                            title="Remover Acesso"
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

            <div className="p-4 border-t border-gray-50">
              <TablePagination
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
                hasMore={!!data?.next}
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
