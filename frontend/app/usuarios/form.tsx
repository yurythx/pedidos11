'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { request } from '../../src/lib/http/request'
import type { Usuario } from '../../src/types'
import { Save, X, UserCircle, ShieldCheck, Percent, Phone, Mail, User as UserIcon } from 'lucide-react'
import { toast } from 'sonner'

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
    telefone: initialData?.telefone ?? '',
    is_colaborador: initialData?.is_colaborador ?? false,
    role_atendente: initialData?.role_atendente ?? false,
    role_caixa: initialData?.role_caixa ?? false,
    comissao_percentual: initialData?.comissao_percentual ?? '10.00',
  })

  const [loading, setLoading] = useState(false)

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

    try {
      const payload = { ...formData }
      if (isEditing && !payload.password) {
        delete (payload as any).password
      }

      if (isEditing) {
        await request.patch(`/usuarios/${initialData.id}/`, payload)
        toast.success('Usuário atualizado com sucesso!')
      } else {
        await request.post('/usuarios/', payload)
        toast.success('Usuário criado com sucesso!')
      }

      router.push('/usuarios')
      router.refresh()
    } catch (err: any) {
      console.error(err)
      toast.error(err?.message ?? 'Erro ao salvar usuário')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Lado Esquerdo - Informações Básicas */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-6 border-b border-gray-50 pb-4">
              <UserCircle className="w-6 h-6 text-primary" />
              <h3 className="text-lg font-bold text-gray-900">Informações Pessoais</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="label">Nome</label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="input pl-10"
                    placeholder="Ex: João"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="label">Sobrenome</label>
                <input
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Ex: Silva"
                />
              </div>

              <div className="space-y-1.5 md:col-span-2">
                <label className="label">Email *</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="input pl-10"
                    placeholder="joao@empresa.com"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="label">Telefone</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    name="telefone"
                    value={formData.telefone}
                    onChange={handleChange}
                    className="input pl-10"
                    placeholder="(11) 99999-9999"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="label">Usuário (Login) *</label>
                <input
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={isEditing}
                  className="input disabled:bg-gray-50 disabled:text-gray-400"
                  placeholder="joao.silva"
                  required
                />
              </div>

              {!isEditing && (
                <div className="space-y-1.5">
                  <label className="label">Senha Inicial *</label>
                  <input
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="input"
                    placeholder="••••••••"
                    required={!isEditing}
                    minLength={8}
                  />
                </div>
              )}
            </div>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-6 border-b border-gray-50 pb-4">
              <ShieldCheck className="w-6 h-6 text-primary" />
              <h3 className="text-lg font-bold text-gray-900">Acessos e Funções</h3>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1.5">
                  <label className="label">Cargo Principal</label>
                  <select
                    name="cargo"
                    value={formData.cargo}
                    onChange={handleChange}
                    className="input"
                  >
                    <option value="VENDEDOR">Vendedor / Atendente</option>
                    <option value="CAIXA">Operador de Caixa</option>
                    <option value="GERENTE">Gerente de Loja</option>
                    <option value="ESTOQUISTA">Estoquista</option>
                    <option value="FINANCEIRO">Auxiliar Financeiro</option>
                    <option value="ADMIN">Administrador Geral</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="label">Comissão sobre Vendas (%)</label>
                  <div className="relative">
                    <Percent className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      name="comissao_percentual"
                      type="number"
                      step="0.01"
                      value={formData.comissao_percentual}
                      onChange={handleChange}
                      className="input pl-10"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
                <h4 className="text-sm font-bold text-gray-700 mb-4">Permissões Específicas</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <label className="flex items-center p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                    <input
                      name="role_atendente"
                      type="checkbox"
                      checked={formData.role_atendente}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                    />
                    <span className="ml-3 text-sm font-medium text-gray-700">Pode atender mesas</span>
                  </label>

                  <label className="flex items-center p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                    <input
                      name="role_caixa"
                      type="checkbox"
                      checked={formData.role_caixa}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                    />
                    <span className="ml-3 text-sm font-medium text-gray-700">Pode operar caixa</span>
                  </label>

                  <label className="flex items-center p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                    <input
                      name="is_colaborador"
                      type="checkbox"
                      checked={formData.is_colaborador}
                      onChange={handleChange}
                      className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                    />
                    <span className="ml-3 text-sm font-medium text-gray-700">É colaborador interno</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lado Direito - Status e Ações */}
        <div className="space-y-6">
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-6 border-b border-gray-50 pb-4">Status da Conta</h3>

            <label className="flex items-center justify-between p-4 bg-gray-50 rounded-xl cursor-pointer">
              <span className="text-sm font-bold text-gray-700">Conta Ativa</span>
              <div className="relative inline-flex items-center cursor-pointer">
                <input
                  name="is_active"
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </div>
            </label>
            <p className="mt-4 text-xs text-gray-500 leading-relaxed italic">
              * Contas inativas não podem realizar login no sistema ou no aplicativo de pedidos.
            </p>
          </div>

          <div className="flex flex-col gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-4 text-lg shadow-lg shadow-primary/20"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Salvando...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save className="w-5 h-5" />
                  Salvar Usuário
                </span>
              )}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="btn btn-secondary w-full py-4 text-lg"
            >
              <X className="w-5 h-5 mr-2" />
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}
