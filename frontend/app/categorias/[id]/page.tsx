'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'

type CategoriaForm = {
  nome: string
  parent: string
  descricao: string
  ordem: number
  is_active: boolean
}

export default function CategoriaFormPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const isNew = params.id === 'novo'
  const id = params.id

  const [form, setForm] = useState<CategoriaForm>({
    nome: '',
    parent: '',
    descricao: '',
    ordem: 0,
    is_active: true,
  })

  const [categorias, setCategorias] = useState<{ id: string; nome: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadCategorias = async () => {
      try {
        const res = await request.get<any>('/categorias/?page_size=100')
        // Filtrar a própria categoria para não ser pai dela mesma
        const list = (res?.results ?? res ?? []).filter((c: any) => c.id !== id)
        setCategorias(list)
      } catch {
        // ignora
      }
    }
    loadCategorias()

    if (!isNew) {
      const loadCategoria = async () => {
        setLoading(true)
        try {
          const res = await request.get<any>(`/categorias/${id}/`)
          setForm({
            nome: res.nome,
            parent: res.parent ?? '',
            descricao: res.descricao ?? '',
            ordem: res.ordem ?? 0,
            is_active: res.is_active,
          })
        } catch (err: any) {
          setError(err?.message ?? 'Erro ao carregar categoria')
        } finally {
          setLoading(false)
        }
      }
      loadCategoria()
    }
  }, [id, isNew])

  const onChange = (field: keyof CategoriaForm, value: any) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...form,
        parent: form.parent || null,
        descricao: form.descricao || null,
      }

      if (isNew) {
        await request.post('/categorias/', payload)
      } else {
        await request.patch(`/categorias/${id}/`, payload)
      }
      router.push('/categorias')
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao salvar categoria')
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
        <Link href="/categorias" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-600" />
        </Link>
        <h1 className="heading-1">{isNew ? 'Nova Categoria' : 'Editar Categoria'}</h1>
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
            <label className="label">Nome da Categoria</label>
            <input
              className="input"
              value={form.nome}
              onChange={(e) => onChange('nome', e.target.value)}
              required
              placeholder="Ex: Bebidas"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Categoria Pai (Opcional)</label>
              <select
                className="input"
                value={form.parent}
                onChange={(e) => onChange('parent', e.target.value)}
              >
                <option value="">Nenhuma (Raiz)</option>
                {categorias.map((c) => (
                  <option key={c.id} value={c.id}>{c.nome}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Ordem de Exibição</label>
              <input
                type="number"
                className="input"
                value={form.ordem}
                onChange={(e) => onChange('ordem', parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <div>
            <label className="label">Descrição</label>
            <textarea
              className="input min-h-[100px]"
              value={form.descricao}
              onChange={(e) => onChange('descricao', e.target.value)}
              placeholder="Descrição interna para organização"
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
              <span className="text-gray-700">Categoria Ativa</span>
            </label>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-50 flex justify-end gap-3">
          <Link href="/categorias" className="btn btn-ghost">
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
                Salvar Categoria
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
