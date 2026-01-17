'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

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

  useEffect(() => {
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
    load()
  }, [])

  if (loading) return <div className="p-4">Carregando categorias...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>

  const categorias = data ?? []

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Categorias</h1>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border">Nome</th>
            <th className="text-left p-2 border">Pai</th>
            <th className="text-left p-2 border">Ordem</th>
            <th className="text-left p-2 border">Status</th>
          </tr>
        </thead>
        <tbody>
          {categorias.map((c) => (
            <tr key={c.id}>
              <td className="p-2 border">{c.nome}</td>
              <td className="p-2 border">{c.parent_nome ?? '-'}</td>
              <td className="p-2 border">{c.ordem}</td>
              <td className="p-2 border">{c.is_active ? 'Ativa' : 'Inativa'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

