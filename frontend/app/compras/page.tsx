'use client'

import React, { useEffect, useState } from 'react'
import { useAuthStore } from '../../src/features/auth/store'

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
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Compras & NFe</h1>
      <form onSubmit={onUpload} className="space-y-2 mb-4 border p-3 rounded">
        <div>
          <label className="block text-sm">Arquivo XML</label>
          <input type="file" name="xml" accept=".xml" className="mt-1" />
        </div>
        <button type="submit" disabled={loading} className="bg-black text-white rounded px-3 py-2 disabled:opacity-60">
          {loading ? 'Processando...' : 'Enviar XML'}
        </button>
      </form>
      {error && <div className="text-red-600 mb-3">{error}</div>}
      {preview && (
        <div className="space-y-3">
          <div className="border rounded p-3">
            <div className="text-sm">Fornecedor: {preview.fornecedor.nome} ({preview.fornecedor.cnpj})</div>
            <div className="text-sm">NFe: {preview.numero_nfe} / Série: {preview.serie_nfe}</div>
          </div>
          <div className="border rounded p-3">
            <label className="block text-sm mb-1">Depósito</label>
            <select
              className="border rounded px-2 py-1"
              value={depositoId}
              onChange={(e) => setDepositoId(e.target.value)}
            >
              <option value="">Selecione</option>
              {depositos.map((d) => (
                <option key={d.id} value={d.id}>{d.nome}</option>
              ))}
            </select>
          </div>
          <div className="border rounded p-3">
            <h2 className="font-medium mb-2">Itens</h2>
            <table className="w-full border">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-2 border">Código XML</th>
                  <th className="text-left p-2 border">Descrição</th>
                  <th className="text-left p-2 border">Produto</th>
                  <th className="text-left p-2 border">Fator</th>
                  <th className="text-left p-2 border">Qtd XML</th>
                  <th className="text-left p-2 border">Preço Custo</th>
                  <th className="text-left p-2 border">Lote</th>
                </tr>
              </thead>
              <tbody>
                {preview.itens.map((it, idx) => (
                  <tr key={it.codigo_xml}>
                    <td className="p-2 border">{it.codigo_xml}</td>
                    <td className="p-2 border">{it.descricao_xml}</td>
                    <td className="p-2 border">
                      <select
                        className="border rounded px-2 py-1 w-56"
                        value={itensForm[idx]?.produto_id ?? ''}
                        onChange={(e) => updateItem(idx, 'produto_id', e.target.value)}
                      >
                        <option value="">Selecione</option>
                        {(it.sugestoes_produtos ?? []).map((s) => (
                          <option key={s.produto_id} value={s.produto_id}>{s.nome}</option>
                        ))}
                      </select>
                    </td>
                    <td className="p-2 border">
                      <input
                        className="border rounded px-2 py-1 w-20"
                        type="number"
                        step="0.001"
                        value={itensForm[idx]?.fator_conversao ?? 1}
                        onChange={(e) => updateItem(idx, 'fator_conversao', Number(e.target.value))}
                      />
                    </td>
                    <td className="p-2 border">
                      <input
                        className="border rounded px-2 py-1 w-20"
                        type="number"
                        step="0.001"
                        value={itensForm[idx]?.qtd_xml ?? 1}
                        onChange={(e) => updateItem(idx, 'qtd_xml', Number(e.target.value))}
                      />
                    </td>
                    <td className="p-2 border">
                      <input
                        className="border rounded px-2 py-1 w-24"
                        type="number"
                        step="0.01"
                        value={itensForm[idx]?.preco_custo ?? 0}
                        onChange={(e) => updateItem(idx, 'preco_custo', Number(e.target.value))}
                      />
                    </td>
                    <td className="p-2 border">
                      <div className="grid grid-cols-3 gap-1">
                        <input
                          placeholder="Código"
                          className="border rounded px-2 py-1"
                          value={itensForm[idx]?.lote_codigo ?? ''}
                          onChange={(e) => updateItem(idx, 'lote_codigo', e.target.value)}
                        />
                        <input
                          type="date"
                          placeholder="Validade"
                          className="border rounded px-2 py-1"
                          value={itensForm[idx]?.lote_validade ?? ''}
                          onChange={(e) => updateItem(idx, 'lote_validade', e.target.value)}
                        />
                        <input
                          type="date"
                          placeholder="Fabricação"
                          className="border rounded px-2 py-1"
                          value={itensForm[idx]?.lote_fabricacao ?? ''}
                          onChange={(e) => updateItem(idx, 'lote_fabricacao', e.target.value)}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button onClick={onConfirmar} className="bg-black text-white rounded px-3 py-2">Confirmar Importação</button>
        </div>
      )}
    </div>
  )
}

