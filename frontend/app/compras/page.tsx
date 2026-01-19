'use client'

import React, { useEffect, useState } from 'react'
import { useAuthStore } from '../../src/features/auth/store'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/Table'
import { Upload, Check, FileText, AlertCircle, ShoppingCart } from 'lucide-react'

type PreviewItem = {
  codigo_xml: string
  descricao_xml: string
  unidade_xml?: string
  produto_sugerido_id?: string | null
  fator_conversao_sugerido?: number
  sugestoes_produtos?: Array<{ produto_id: string; nome: string; fator_conversao?: number }>
}

type PreviewResponse = {
  success: boolean
  preview?: {
    fornecedor: { cnpj: string; nome: string }
    numero_nfe: string
    serie_nfe: string
    itens: PreviewItem[]
  }
  errors?: string[]
}

export default function ComprasPage() {
  const { tokens } = useAuthStore()
  const [preview, setPreview] = useState<PreviewResponse['preview'] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [depositoId, setDepositoId] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [itensForm, setItensForm] = useState<
    Array<{
      codigo_xml: string
      produto_id: string | null
      fator_conversao: number
      qtd_xml: number
      preco_custo: number
      lote_codigo: string
      lote_validade: string
      lote_fabricacao: string
    }>
  >([])

  useEffect(() => {
    const loadDepositos = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'}/depositos/?page_size=100`, {
          headers: { Authorization: `Bearer ${tokens.access ?? ''}` },
        })
        const data = await res.json()
        const list = data?.results ?? data ?? []
        setDepositos(list)
      } catch {
        setDepositos([])
      }
    }
    loadDepositos()
  }, [tokens])

  const onUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const input = e.currentTarget.elements.namedItem('xml') as HTMLInputElement
      const file = input?.files?.[0]
      if (!file) {
        setError('Selecione um arquivo XML')
        setLoading(false)
        return
      }
      const form = new FormData()
      form.append('arquivo', file)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'}/nfe/importacao/upload-xml/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${tokens.access ?? ''}` },
        body: form,
      })
      const data: PreviewResponse = await res.json()
      if (!data.success) {
        setError(data.errors?.join(', ') ?? 'Erro ao processar XML')
        setLoading(false)
        return
      }
      setPreview(data.preview ?? null)
      setItensForm(
        (data.preview?.itens ?? []).map((i) => ({
          codigo_xml: i.codigo_xml,
          produto_id: i.produto_sugerido_id ?? null,
          fator_conversao: i.fator_conversao_sugerido ?? 1,
          qtd_xml: 1,
          preco_custo: 0,
          lote_codigo: '',
          lote_validade: '',
          lote_fabricacao: '',
        }))
      )
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao enviar XML')
    } finally {
      setLoading(false)
    }
  }

  const updateItem = (idx: number, field: string, value: any) => {
    setItensForm((items) => {
      const next = [...items]
      ;(next[idx] as any)[field] = value
      return next
    })
  }

  const onConfirmar = async () => {
    if (!preview) {
      setError('Faça upload de um XML para confirmar')
      return
    }
    if (!depositoId) {
      setError('Selecione um depósito')
      return
    }
    setError(null)
    try {
      const payload = {
        deposito_id: depositoId,
        numero_nfe: preview.numero_nfe,
        serie_nfe: preview.serie_nfe,
        fornecedor: preview.fornecedor,
        itens: itensForm.map((i) => ({
          codigo_xml: i.codigo_xml,
          produto_id: i.produto_id,
          fator_conversao: i.fator_conversao,
          qtd_xml: i.qtd_xml,
          preco_custo: i.preco_custo,
          lote: {
            codigo: i.lote_codigo,
            validade: i.lote_validade,
            fabricacao: i.lote_fabricacao,
          },
        })),
      }
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'}/nfe/importacao/confirmar/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${tokens.access ?? ''}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (res.ok) {
        alert(`Importação: ${data.status} - ${data.message}`)
        setPreview(null)
        setItensForm([])
      } else {
        setError(data?.message ?? 'Erro ao confirmar importação')
      }
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao confirmar')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Compras & NFe</h1>
          <p className="text-gray-500 mt-1">Importação de notas fiscais e gestão de compras</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 className="heading-2 mb-4 flex items-center gap-2">
           <Upload className="w-5 h-5 text-gray-400" />
           Importar XML
        </h2>
        <form onSubmit={onUpload} className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <label className="label">Arquivo XML da NFe</label>
            <input 
              type="file" 
              name="xml" 
              accept=".xml" 
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2.5 file:px-4
                file:rounded-xl file:border-0
                file:text-sm file:font-semibold
                file:bg-primary/10 file:text-primary
                hover:file:bg-primary/20 cursor-pointer
              "
            />
          </div>
          <button 
            type="submit" 
            disabled={loading} 
            className="btn btn-primary w-full md:w-auto"
          >
            {loading ? 'Processando...' : 'Enviar e Processar'}
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-xl flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {preview && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="font-semibold text-gray-500 text-sm uppercase tracking-wider mb-3">Dados da Nota</h3>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                   <p className="font-bold text-gray-900">{preview.fornecedor.nome}</p>
                   <p className="text-sm text-gray-500">CNPJ: {preview.fornecedor.cnpj}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-50 flex gap-6">
                <div>
                   <span className="text-xs text-gray-400 block">Número</span>
                   <span className="font-mono font-medium">{preview.numero_nfe}</span>
                </div>
                <div>
                   <span className="text-xs text-gray-400 block">Série</span>
                   <span className="font-mono font-medium">{preview.serie_nfe}</span>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="font-semibold text-gray-500 text-sm uppercase tracking-wider mb-3">Destino</h3>
              <label className="label">Depósito de Entrada</label>
              <select
                className="input"
                value={depositoId}
                onChange={(e) => setDepositoId(e.target.value)}
              >
                <option value="">Selecione um depósito...</option>
                {depositos.map((d) => (
                  <option key={d.id} value={d.id}>{d.nome}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="card overflow-hidden">
            <div className="flex items-center justify-between mb-4">
               <h2 className="heading-2">Itens da Nota</h2>
               <span className="text-sm text-gray-500">{preview.itens.length} itens encontrados</span>
            </div>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Cód. XML</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Vincular Produto</TableHead>
                  <TableHead>Fator</TableHead>
                  <TableHead>Qtd</TableHead>
                  <TableHead>Custo Unit.</TableHead>
                  <TableHead>Lote / Validade</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {preview.itens.map((it, idx) => (
                  <TableRow key={it.codigo_xml}>
                    <TableCell><span className="font-mono text-xs text-gray-500">{it.codigo_xml}</span></TableCell>
                    <TableCell className="max-w-xs truncate" title={it.descricao_xml}>{it.descricao_xml}</TableCell>
                    <TableCell>
                      <select
                        className="input py-2 text-sm min-w-[200px]"
                        value={itensForm[idx]?.produto_id ?? ''}
                        onChange={(e) => updateItem(idx, 'produto_id', e.target.value)}
                      >
                        <option value="">Selecione...</option>
                        {(it.sugestoes_produtos ?? []).map((s) => (
                          <option key={s.produto_id} value={s.produto_id}>{s.nome}</option>
                        ))}
                      </select>
                    </TableCell>
                    <TableCell>
                      <input
                        className="input py-2 w-20 text-center"
                        type="number"
                        step="0.001"
                        value={itensForm[idx]?.fator_conversao ?? 1}
                        onChange={(e) => updateItem(idx, 'fator_conversao', Number(e.target.value))}
                      />
                    </TableCell>
                    <TableCell>
                      <input
                        className="input py-2 w-20 text-center"
                        type="number"
                        step="0.001"
                        value={itensForm[idx]?.qtd_xml ?? 1}
                        onChange={(e) => updateItem(idx, 'qtd_xml', Number(e.target.value))}
                      />
                    </TableCell>
                    <TableCell>
                      <input
                        className="input py-2 w-24 text-right"
                        type="number"
                        step="0.01"
                        value={itensForm[idx]?.preco_custo ?? 0}
                        onChange={(e) => updateItem(idx, 'preco_custo', Number(e.target.value))}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-2 min-w-[140px]">
                        <input
                          placeholder="Lote"
                          className="input py-1.5 text-xs"
                          value={itensForm[idx]?.lote_codigo ?? ''}
                          onChange={(e) => updateItem(idx, 'lote_codigo', e.target.value)}
                        />
                        <div className="flex gap-1">
                          <input
                            type="date"
                            title="Validade"
                            className="input py-1.5 text-xs px-1"
                            value={itensForm[idx]?.lote_validade ?? ''}
                            onChange={(e) => updateItem(idx, 'lote_validade', e.target.value)}
                          />
                          <input
                            type="date"
                            title="Fabricação"
                            className="input py-1.5 text-xs px-1"
                            value={itensForm[idx]?.lote_fabricacao ?? ''}
                            onChange={(e) => updateItem(idx, 'lote_fabricacao', e.target.value)}
                          />
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="flex justify-end pt-4">
            <button 
              onClick={onConfirmar} 
              className="btn btn-primary text-lg px-8 py-3 shadow-lg shadow-red-200"
            >
              <Check className="w-5 h-5 mr-2" />
              Confirmar Importação
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

