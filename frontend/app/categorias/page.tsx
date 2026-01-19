'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/Table'
import { Plus, Edit, Trash2 } from 'lucide-react'
import Link from 'next/link'

type Categoria = {
  id: string
  nome: string
  slug: string
  parent: string | null
  parent_nome: string | null
  descricao: string | null
  ordem: number
  caminho_completo: string
  is_active: boolean
}

export default function CategoriasPage() {
  const [data, setData] = useState<Categoria[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<any>('/categorias/?page_size=100')
      const list: Categoria[] = res?.results ?? res ?? []
      setData(list)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar categorias')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const onDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta categoria?')) return
    try {
      await request.delete(`/categorias/${id}/`)
      load()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao excluir')
    }
  }

  const categorias = data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Categorias</h1>
          <p className="text-gray-500 mt-1">Organize seus produtos por categorias</p>
        </div>
        <Link href="/categorias/novo" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Nova Categoria
        </Link>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando categorias...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Categoria Pai</TableHead>
              <TableHead>Ordem</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {categorias.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                  Nenhuma categoria encontrada.
                </TableCell>
              </TableRow>
            ) : (
              categorias.map((c) => (
                <TableRow key={c.id}>
                  <TableCell><div className="font-medium text-gray-900">{c.nome}</div></TableCell>
                  <TableCell>{c.parent_nome ?? '-'}</TableCell>
                  <TableCell>{c.ordem}</TableCell>
                  <TableCell>
                    {c.is_active ? (
                       <span className="text-green-600 text-sm font-medium flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Ativa
                       </span>
                    ) : (
                       <span className="text-red-600 text-sm font-medium flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span> Inativa
                       </span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                     <div className="flex items-center justify-end gap-2">
                        <Link 
                          href={`/categorias/${c.id}`}
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
              ))
            )}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
