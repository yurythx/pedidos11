'use client'

import React, { useState } from 'react'
import { useAuthStore } from '../../../src/features/auth/store'
import type { LoginResponse } from '../../../src/types'
import { useRouter } from 'next/navigation'
import { request } from '../../../src/lib/http/request'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const data = await request.post<LoginResponse>('/auth/token/', { username, password })
      useAuthStore.getState().login(data.user, { access: data.access, refresh: data.refresh })
      useAuthStore.getState().setTenantId(data.user.empresa_id)
      router.push('/')
    } catch (err: any) {
      const msg = err?.message ?? 'Credenciais inválidas ou erro de rede.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4 p-6 border rounded-md">
        <h1 className="text-xl font-semibold">Login</h1>
        <div>
          <label className="block text-sm">Usuário</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 w-full border rounded px-3 py-2"
            required
          />
        </div>
        <div>
          <label className="block text-sm">Senha</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border rounded px-3 py-2"
            required
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-black text-white rounded px-3 py-2 disabled:opacity-60"
        >
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}


