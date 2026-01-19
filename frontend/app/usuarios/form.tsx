'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { request } from '../../src/lib/http/request'
import type { Usuario } from '../../src/types'

interface UserFormProps {
  initialData?: Usuario
}

export default function UserForm({ initialData }: UserFormProps) {
  const router = useRouter()
  const isEditing = !!initialData

  const [formData, setFormData] = useState({
    username: initialData?.username ?? '',
    password: '',
    first_name: initialData?.first_name ?? '',
    last_name: initialData?.last_name ?? '',
    email: initialData?.email ?? '',
    cargo: initialData?.cargo ?? 'VENDEDOR',
    is_active: initialData?.is_active ?? true,
    telefone: '', // TODO: Adicionar campo telefone no tipo Usuario se necessário, mas backend aceita
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (isEditing) {
        // PUT /api/usuarios/{id}/
        // Não enviamos password na edição simples aqui
        const payload = { ...formData }
        if (!payload.password) delete (payload as any).password
        
        await request.patch(`/usuarios/${initialData.id}/`, payload)
      } else {
        // POST /api/usuarios/
        await request.post('/usuarios/', formData)
      }
      router.push('/usuarios')
      router.refresh()
    } catch (err: any) {
      console.error(err)
      setError(err?.response?.data?.detail ?? err?.message ?? 'Erro ao salvar usuário')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-lg bg-white p-6 rounded shadow">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded text-sm">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Usuário *</label>
        <input
          name="username"
          value={formData.username}
          onChange={handleChange}
          disabled={isEditing}
          className="mt-1 block w-full border border-gray-300 rounded px-3 py-2 disabled:bg-gray-100"
          required
        />
      </div>

      {!isEditing && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Senha *</label>
          <input
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
            required={!isEditing}
            minLength={8}
          />
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Nome</label>
          <input
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Sobrenome</label>
          <input
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Email *</label>
        <input
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Cargo</label>
        <select
          name="cargo"
          value={formData.cargo}
          onChange={handleChange}
          className="mt-1 block w-full border border-gray-300 rounded px-3 py-2"
        >
          <option value="VENDEDOR">Vendedor</option>
          <option value="CAIXA">Caixa</option>
          <option value="GERENTE">Gerente</option>
          <option value="ESTOQUISTA">Estoquista</option>
          <option value="FINANCEIRO">Financeiro</option>
          <option value="ADMIN">Administrador</option>
        </select>
      </div>

      <div className="flex items-center">
        <input
          id="is_active"
          name="is_active"
          type="checkbox"
          checked={formData.is_active}
          onChange={handleChange}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
        />
        <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
          Usuário Ativo
        </label>
      </div>

      <div className="pt-4 flex justify-end gap-2">
        <button
          type="button"
          onClick={() => router.back()}
          className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </form>
  )
}
