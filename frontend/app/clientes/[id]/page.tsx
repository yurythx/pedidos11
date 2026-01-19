'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'

type ClienteForm = {
  nome: string
  cpf_cnpj: string
  email: string
  telefone: string
  observacoes: string
  is_active: boolean
}

export default function ClienteFormPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const isNew = params.id === 'novo'
  const id = params.id

  const [form, setForm] = useState<ClienteForm>({
    nome: '',
    cpf_cnpj: '',
    email: '',
    telefone: '',
    observacoes: '',
    is_active: true,
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isNew) {
      const loadCliente = async () => {
        setLoading(true)
        try {
          const res = await request.get<any>(`/clientes/${id}/`)
          setForm({
            nome: res.nome,
            cpf_cnpj: res.cpf_cnpj ?? '',
            email: res.email ?? '',
            telefone: res.telefone ?? '',
            observacoes: res.observacoes ?? '',
            is_active: res.is_active,
          })
        } catch (err: any) {
          setError(err?.message ?? 'Erro ao carregar cliente')
        } finally {
          setLoading(false)
        }
      }
      loadCliente()
    }
  }, [id, isNew])

  const onChange = (field: keyof ClienteForm, value: any) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...form,
        cpf_cnpj: form.cpf_cnpj || null,
        email: form.email || null,
        telefone: form.telefone || null,
        observacoes: form.observacoes || null,
      }

      if (isNew) {
        await request.post('/clientes/', payload)
      } else {
        await request.patch(`/clientes/${id}/`, payload)
      }
      router.push('/clientes')
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao salvar cliente')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !isNew && !form.nome) {
    return <div className="text-center py-8">Carregando...</div>
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/clientes" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-600" />
        </Link>
        <h1 className="heading-1">{isNew ? 'Novo Cliente' : 'Editar Cliente'}</h1>
      </div>

      <form onSubmit={onSubmit} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="label">Nome Completo</label>
            <input
              className="input"
              value={form.nome}
              onChange={(e) => onChange('nome', e.target.value)}
              required
              placeholder="Ex: João da Silva"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">CPF / CNPJ</label>
              <input
                className="input"
                value={form.cpf_cnpj}
                onChange={(e) => onChange('cpf_cnpj', e.target.value)}
                placeholder="Apenas números"
              />
            </div>
            <div>
              <label className="label">Telefone / WhatsApp</label>
              <input
                className="input"
                value={form.telefone}
                onChange={(e) => onChange('telefone', e.target.value)}
                placeholder="(00) 00000-0000"
              />
            </div>
          </div>

          <div>
            <label className="label">Email</label>
            <input
              type="email"
              className="input"
              value={form.email}
              onChange={(e) => onChange('email', e.target.value)}
              placeholder="cliente@exemplo.com"
            />
          </div>

          <div>
            <label className="label">Observações</label>
            <textarea
              className="input min-h-[100px]"
              value={form.observacoes}
              onChange={(e) => onChange('observacoes', e.target.value)}
              placeholder="Preferências, restrições, etc."
            />
          </div>

          <div className="flex items-center gap-2 pt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => onChange('is_active', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <span className="text-gray-700">Cliente Ativo</span>
            </label>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-50 flex justify-end gap-3">
          <Link href="/clientes" className="btn btn-ghost">
            Cancelar
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary min-w-[150px]"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Save className="w-5 h-5 mr-2" />
                Salvar Cliente
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
