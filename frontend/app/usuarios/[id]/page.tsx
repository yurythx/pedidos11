'use client'

import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import UserForm from '../form'
import { request } from '../../../src/lib/http/request'
import type { Usuario } from '../../../src/types'

export default function EditUserPage() {
  const params = useParams()
  const id = params.id as string
  
  const [user, setUser] = useState<Usuario | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await request.get<Usuario>(`/usuarios/${id}/`)
        setUser(data)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar usuário')
      } finally {
        setLoading(false)
      }
    }
    if (id) {
      fetchUser()
    }
  }, [id])

  if (loading) return <div className="p-6">Carregando...</div>
  if (error) return <div className="p-6 text-red-600">{error}</div>
  if (!user) return <div className="p-6">Usuário não encontrado</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Editar Usuário: {user.username}</h1>
      <UserForm initialData={user} />
    </div>
  )
}
