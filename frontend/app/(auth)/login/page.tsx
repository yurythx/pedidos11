'use client'

import React, { useState } from 'react'
import { useAuthStore } from '../../../src/features/auth/store'
import type { LoginResponse } from '../../../src/types'
import { useRouter } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { Store, ArrowRight, Loader2 } from 'lucide-react'

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
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Lado Esquerdo - Branding */}
      <div className="hidden md:flex md:w-1/2 bg-primary items-center justify-center p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-dark to-primary opacity-50" />
        <div className="relative z-10 max-w-lg text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-3 mb-6">
            <div className="bg-white/20 p-3 rounded-2xl backdrop-blur-sm">
              <Store className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Nix Food</h1>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
            Gerencie seu delivery com inteligência.
          </h2>
          <p className="text-lg text-white/90 leading-relaxed">
            A plataforma completa para automação de pedidos, controle de estoque e gestão financeira do seu restaurante.
          </p>
        </div>
      </div>

      {/* Lado Direito - Form */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center md:text-left">
            <h2 className="heading-1 mb-2">Bem-vindo de volta!</h2>
            <p className="text-gray-500">Insira suas credenciais para acessar o painel.</p>
          </div>

          <form onSubmit={onSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="label">Usuário</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input"
                  placeholder="Seu nome de usuário"
                  required
                />
              </div>

              <div>
                <label className="label">Senha</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="p-6 rounded-2xl bg-gradient-to-r from-red-500 to-red-600 text-white text-center shadow-2xl border-2 border-red-400 animate-shake">
                <div className="flex items-center justify-center gap-3 mb-2">
                  <span className="text-3xl">⚠️</span>
                  <h3 className="text-xl font-bold">Erro ao fazer login</h3>
                </div>
                <p className="text-white/90">{error}</p>
                <p className="text-sm text-white/75 mt-2">Verifique suas credenciais e tente novamente.</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-3 text-lg group"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Entrar no Sistema
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="text-center text-sm text-gray-400 mt-8">
            &copy; 2026 Nix Food. Todos os direitos reservados.
          </div>
        </div>
      </div>
    </div>
  )
}
