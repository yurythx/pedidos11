'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'

type ProdutoForm = {
  nome: string
  sku: string
  codigo_barras: string
  categoria: string
  tipo: string
  preco_venda: string
  preco_custo: string
  unidade: string
  is_active: boolean
  destaque: boolean
}

export default function ProdutoFormPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const isNew = params.id === 'novo'
  const id = params.id

  const [form, setForm] = useState<ProdutoForm>({
    nome: '',
    sku: '',
    codigo_barras: '',
    categoria: '',
    tipo: 'COMUM',
    preco_venda: '0',
    preco_custo: '0',
    unidade: 'UN',
    is_active: true,
    destaque: false,
  })

  const [categorias, setCategorias] = useState<{ id: string; nome: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadCategorias = async () => {
      try {
        const res = await request.get<any>('/categorias/?page_size=100')
        setCategorias(res?.results ?? res ?? [])
      } catch {
        // ignora erro de categorias
      }
    }
    loadCategorias()

    if (!isNew) {
      const loadProduto = async () => {
        setLoading(true)
        try {
          const res = await request.get<any>(`/produtos/${id}/`)
          setForm({
            nome: res.nome,
            sku: res.sku ?? '',
            codigo_barras: res.codigo_barras ?? '',
            categoria: res.categoria ?? '',
            tipo: res.tipo,
            preco_venda: res.preco_venda,
            preco_custo: res.preco_custo ?? '0',
            unidade: res.unidade ?? 'UN',
            is_active: res.is_active,
            destaque: res.destaque,
          })
        } catch (err: any) {
          setError(err?.message ?? 'Erro ao carregar produto')
        } finally {
          setLoading(false)
        }
      }
      loadProduto()
    }
  }, [id, isNew])

  const onChange = (field: keyof ProdutoForm, value: any) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...form,
        categoria: form.categoria || null,
        sku: form.sku || null,
        codigo_barras: form.codigo_barras || null,
        preco_venda: Number(form.preco_venda),
        preco_custo: Number(form.preco_custo),
      }

      if (isNew) {
        await request.post('/produtos/', payload)
      } else {
        await request.patch(`/produtos/${id}/`, payload)
      }
      router.push('/produtos')
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao salvar produto')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !isNew && !form.nome) {
    return <div className="text-center py-8">Carregando...</div>
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/produtos" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-600" />
        </Link>
        <h1 className="heading-1">{isNew ? 'Novo Produto' : 'Editar Produto'}</h1>
      </div>

      <form onSubmit={onSubmit} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="label">Nome do Produto</label>
              <input
                className="input"
                value={form.nome}
                onChange={(e) => onChange('nome', e.target.value)}
                required
                placeholder="Ex: Coca-Cola 350ml"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Preço Venda (R$)</label>
                <input
                  type="number"
                  step="0.01"
                  className="input"
                  value={form.preco_venda}
                  onChange={(e) => onChange('preco_venda', e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="label">Preço Custo (R$)</label>
                <input
                  type="number"
                  step="0.01"
                  className="input"
                  value={form.preco_custo}
                  onChange={(e) => onChange('preco_custo', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Categoria</label>
                <select
                  className="input"
                  value={form.categoria}
                  onChange={(e) => onChange('categoria', e.target.value)}
                >
                  <option value="">Sem Categoria</option>
                  {categorias.map((c) => (
                    <option key={c.id} value={c.id}>{c.nome}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Tipo</label>
                <select
                  className="input"
                  value={form.tipo}
                  onChange={(e) => onChange('tipo', e.target.value)}
                >
                  <option value="COMUM">Comum (Revenda)</option>
                  <option value="COMPOSTO">Composto (Ficha Técnica)</option>
                  <option value="INSUMO">Insumo (Matéria Prima)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="label">SKU (Código Interno)</label>
              <input
                className="input"
                value={form.sku}
                onChange={(e) => onChange('sku', e.target.value)}
                placeholder="Opcional"
              />
            </div>
            <div>
              <label className="label">Código de Barras (EAN)</label>
              <input
                className="input"
                value={form.codigo_barras}
                onChange={(e) => onChange('codigo_barras', e.target.value)}
                placeholder="Opcional"
              />
            </div>
            <div>
              <label className="label">Unidade de Medida</label>
              <select
                className="input"
                value={form.unidade}
                onChange={(e) => onChange('unidade', e.target.value)}
              >
                <option value="UN">Unidade (UN)</option>
                <option value="KG">Quilograma (KG)</option>
                <option value="L">Litro (L)</option>
                <option value="M">Metro (M)</option>
              </select>
            </div>
            
            <div className="flex items-center gap-6 pt-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => onChange('is_active', e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="text-gray-700">Produto Ativo</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.destaque}
                  onChange={(e) => onChange('destaque', e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="text-gray-700">Destaque no PDV</span>
              </label>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-50 flex justify-end gap-3">
          <Link href="/produtos" className="btn btn-ghost">
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
                Salvar Produto
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
