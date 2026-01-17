'use client'

import React, { useEffect, useState } from 'react'
import { useAuthStore } from '../../src/features/auth/store'
import { request } from '../../src/lib/http/request'

export default function PerfilPage() {
  const { user } = useAuthStore()
  const [me, setMe] = useState<any>(user)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadMe = async () => {
      try {
        const data = await request.get<any>('/usuarios/me/')
        setMe(data)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar perfil')
      }
    }
    loadMe()
  }, [])

  const onChange = (field: string, value: any) => {
    setMe((prev: any) => ({ ...prev, [field]: value }))
  }

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const data = await request.patch<any>('/usuarios/me/', {
        first_name: me.first_name,
        last_name: me.last_name,
        telefone: me.telefone,
        email: me.email,
      })
      setMe(data)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao salvar perfil')
    } finally {
      setSaving(false)
    }
  }

  const onUploadFoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('foto_perfil', file)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'}/usuarios/me/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${useAuthStore.getState().tokens.access ?? ''}`,
        },
        body: form,
      })
      if (!res.ok) throw new Error('Falha no upload da foto')
      const data = await res.json()
      setMe(data)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao enviar foto')
    }
  }

  if (!me) return <div className="p-4">Carregando perfil...</div>

  return (
    <div className="p-4 max-w-2xl">
      <h1 className="text-xl font-semibold mb-3">Meu Perfil</h1>
      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
      <form onSubmit={onSave} className="space-y-3">
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-full border overflow-hidden bg-gray-100">
            {me.foto_perfil ? (
              <img src={me.foto_perfil} alt="Avatar" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-sm text-gray-500">Sem foto</div>
            )}
          </div>
          <label className="text-sm">
            <span className="block mb-1">Alterar foto</span>
            <input type="file" accept="image/*" onChange={onUploadFoto} />
          </label>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Nome</label>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={me.first_name ?? ''}
              onChange={(e) => onChange('first_name', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm">Sobrenome</label>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={me.last_name ?? ''}
              onChange={(e) => onChange('last_name', e.target.value)}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm">Email</label>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={me.email ?? ''}
              onChange={(e) => onChange('email', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm">Telefone</label>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={me.telefone ?? ''}
              onChange={(e) => onChange('telefone', e.target.value)}
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={saving}
          className="bg-black text-white rounded px-4 py-2 disabled:opacity-60"
        >
          {saving ? 'Salvando...' : 'Salvar'}
        </button>
      </form>
    </div>
  )
}

