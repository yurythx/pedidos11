'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Save, AlertCircle } from 'lucide-react'
import { request } from '../../../../src/lib/http/request'
import { Fornecedor } from '../../../../src/types'

export default function NovaContaPagarPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([])

  const [formData, setFormData] = useState({
    fornecedor: '',
    descricao: '',
    valor_original: '',
    data_vencimento: '',
    data_emissao: new Date().toISOString().split('T')[0],
    numero_documento: '',
    categoria: 'OUTROS',
    observacoes: ''
  })

  useEffect(() => {
    async function loadFornecedores() {
      try {
        const response = await request.get<{ results: Fornecedor[] }>('/api/fornecedores/')
        setFornecedores(response.results || [])
      } catch (err) {
        console.error('Erro ao carregar fornecedores', err)
      }
    }
    loadFornecedores()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await request.post('/api/contas-pagar/', {
        ...formData,
        valor_original: parseFloat(formData.valor_original.replace(',', '.'))
      })
      router.push('/financeiro/contas-pagar')
    } catch (err: any) {
      setError(err.message || 'Erro ao criar conta a pagar')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Link href="/financeiro/contas-pagar" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-500" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Nova Conta a Pagar</h1>
          <p className="text-gray-500">Registre uma nova despesa ou conta</p>
        </div>
      </div>

      <div className="card bg-base-100 shadow-xl">
        <form onSubmit={handleSubmit} className="card-body">
          {error && (
            <div className="alert alert-error">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          <div className="form-control w-full">
            <label className="label">
              <span className="label-text">Descrição *</span>
            </label>
            <input
              type="text"
              name="descricao"
              value={formData.descricao}
              onChange={handleChange}
              className="input input-bordered w-full"
              placeholder="Ex: Aluguel, Fornecedor X, Energia..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Fornecedor</span>
              </label>
              <select
                name="fornecedor"
                value={formData.fornecedor}
                onChange={handleChange}
                className="select select-bordered w-full"
              >
                <option value="">Selecione um fornecedor (opcional)</option>
                {fornecedores.map(f => (
                  <option key={f.id} value={f.id}>{f.nome_fantasia || f.razao_social}</option>
                ))}
              </select>
            </div>

            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Categoria</span>
              </label>
              <select
                name="categoria"
                value={formData.categoria}
                onChange={handleChange}
                className="select select-bordered w-full"
              >
                <option value="OUTROS">Outros</option>
                <option value="OPERACIONAL">Operacional</option>
                <option value="PESSOAL">Pessoal</option>
                <option value="MERCADORIA">Mercadoria</option>
                <option value="IMPOSTO">Imposto</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Valor Total (R$) *</span>
              </label>
              <input
                type="number"
                step="0.01"
                name="valor_original"
                value={formData.valor_original}
                onChange={handleChange}
                className="input input-bordered w-full"
                placeholder="0.00"
                required
              />
            </div>

            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Número do Documento</span>
              </label>
              <input
                type="text"
                name="numero_documento"
                value={formData.numero_documento}
                onChange={handleChange}
                className="input input-bordered w-full"
                placeholder="Nº da NF ou Boleto"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Data de Emissão *</span>
              </label>
              <input
                type="date"
                name="data_emissao"
                value={formData.data_emissao}
                onChange={handleChange}
                className="input input-bordered w-full"
                required
              />
            </div>

            <div className="form-control w-full">
              <label className="label">
                <span className="label-text">Data de Vencimento *</span>
              </label>
              <input
                type="date"
                name="data_vencimento"
                value={formData.data_vencimento}
                onChange={handleChange}
                className="input input-bordered w-full"
                required
              />
            </div>
          </div>

          <div className="form-control w-full">
            <label className="label">
              <span className="label-text">Observações</span>
            </label>
            <textarea
              name="observacoes"
              value={formData.observacoes}
              onChange={handleChange}
              className="textarea textarea-bordered h-24"
              placeholder="Informações adicionais..."
            ></textarea>
          </div>

          <div className="card-actions justify-end mt-4">
            <Link href="/financeiro/contas-pagar" className="btn btn-ghost">
              Cancelar
            </Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="loading loading-spinner"></span> : <Save className="w-4 h-4 mr-2" />}
              Salvar Conta
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
