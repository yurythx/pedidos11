'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'

type DepositoForm = {
  nome: string
  codigo: string
  descricao: string
  is_padrao: boolean
  is_virtual: boolean
  is_active: boolean
}

export default function DepositoFormPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const isNew = params.id === 'novo'
  const id = params.id

  const [form, setForm] = useState<DepositoForm>({
    nome: '',
    codigo: '',
    descricao: '',
    is_padrao: false,
    is_virtual: false,
    is_active: true,
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isNew) {
      const loadDeposito = async () => {
        setLoading(true)
        try {
          const res = await request.get<any>(`/depositos/${id}/`)
          setForm({
            nome: res.nome,
            codigo: res.codigo ?? '',
            descricao: res.descricao ?? '',
            is_padrao: res.is_padrao,
            is_virtual: res.is_virtual,
            is_active: res.is_active,
          })
        } catch (err: any) {
          setError(err?.message ?? 'Erro ao carregar depósito')
        } finally {
          setLoading(false)
        }
      }
      loadDeposito()
    }
  }, [id, isNew])

  const onChange = (field: keyof DepositoForm, value: any) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...form,
        codigo: form.codigo || null,
        descricao: form.descricao || null,
      }

      if (isNew) {
        await request.post('/depositos/', payload)
      } else {
        await request.patch(`/depositos/${id}/`, payload)
      }
      router.push('/depositos')
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao salvar depósito')
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
        <Link href="/depositos" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-600" />
        </Link>
        <h1 className="heading-1">{isNew ? 'Novo Depósito' : 'Editar Depósito'}</h1>
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
            <label className="label">Nome do Depósito</label>
            <input
              className="input"
              value={form.nome}
              onChange={(e) => onChange('nome', e.target.value)}
              required
              placeholder="Ex: Depósito Principal"
            />
          </div>

          <div>
            <label className="label">Código Interno</label>
            <input
              className="input"
              value={form.codigo}
              onChange={(e) => onChange('codigo', e.target.value)}
              placeholder="Ex: DEP-01"
            />
          </div>

          <div>
            <label className="label">Descrição</label>
            <textarea
              className="input min-h-[100px]"
              value={form.descricao}
              onChange={(e) => onChange('descricao', e.target.value)}
              placeholder="Endereço ou detalhes do local"
            />
          </div>

          <div className="space-y-3 pt-2 border-t border-gray-50">
            <h3 className="font-medium text-gray-900">Configurações</h3>
            
            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 border border-transparent hover:border-gray-100 transition-colors">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => onChange('is_active', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <div>
                <span className="font-medium text-gray-700 block">Depósito Ativo</span>
                <span className="text-xs text-gray-500">Habilitar movimentações neste local</span>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 border border-transparent hover:border-gray-100 transition-colors">
              <input
                type="checkbox"
                checked={form.is_padrao}
                onChange={(e) => onChange('is_padrao', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <div>
                <span className="font-medium text-gray-700 block">Depósito Padrão</span>
                <span className="text-xs text-gray-500">Usado automaticamente em vendas e compras</span>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 border border-transparent hover:border-gray-100 transition-colors">
              <input
                type="checkbox"
                checked={form.is_virtual}
                onChange={(e) => onChange('is_virtual', e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <div>
                <span className="font-medium text-gray-700 block">Depósito Virtual</span>
                <span className="text-xs text-gray-500">Não controla estoque físico (ex: Perdas, Ajustes)</span>
              </div>
            </label>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-50 flex justify-end gap-3">
          <Link href="/depositos" className="btn btn-ghost">
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
                Salvar Depósito
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
