'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Usuario } from '../../src/types'
import Link from 'next/link'

export default function UsuariosPage() {
  const [data, setData] = useState<Paginacao<Usuario> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await request.get<Paginacao<Usuario>>('/usuarios/?page_size=20')
        setData(res)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar usuários')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div className="p-4">Carregando usuários...</div>
  if (error) return <div className="p-4 text-red-600">{error}</div>

  const usuarios = data?.results ?? []

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-semibold">Usuários</h1>
        <Link href="/perfil" className="text-sm underline">Meu Perfil</Link>
      </div>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border">Nome</th>
            <th className="text-left p-2 border">Usuário</th>
            <th className="text-left p-2 border">Email</th>
            <th className="text-left p-2 border">Cargo</th>
            <th className="text-left p-2 border">Ativo</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              <td className="p-2 border">{[u.first_name, u.last_name].filter(Boolean).join(' ') || u.username}</td>
              <td className="p-2 border">{u.username}</td>
              <td className="p-2 border">{u.email ?? '-'}</td>
              <td className="p-2 border">{u.cargo}</td>
              <td className="p-2 border">{u.is_active ? 'Sim' : 'Não'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

