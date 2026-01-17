'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

type Lote = {
  id: string
  codigo_lote: string
  produto_nome: string
  deposito_nome: string
  data_validade: string | null
  quantidade_atual: number
  dias_ate_vencer: number | null
  status_validade: string | null
}

export default function LotesPage() {
  const [data, setData] = useState<Lote[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [validadeMin, setValidadeMin] = useState<string>('')
  const [validadeMax, setValidadeMax] = useState<string>('')
  const [statusValidade, setStatusValidade] = useState<string>('TODOS')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (validadeMin) params.set('validade_min', validadeMin)
      if (validadeMax) params.set('validade_max', validadeMax)
      if (statusValidade !== 'TODOS') params.set('status_validade', statusValidade)
      params.set('page_size', '100')
      const res = await request.get<any>(`/lotes/?${params.toString()}`)
      setData(res?.results ?? res ?? [])
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar lotes')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusValidade])

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Lotes</h1>
      <div className="grid grid-cols-5 gap-2 mb-3">
        <input
          type="date"
          value={validadeMin}
          onChange={(e) => setValidadeMin(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <input
          type="date"
          value={validadeMax}
          onChange={(e) => setValidadeMax(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <select
          value={statusValidade}
          onChange={(e) => setStatusValidade(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="TODOS">Todos</option>
          <option value="OK">OK</option>
          <option value="ATENCAO">Atenção</option>
          <option value="CRITICO">Crítico</option>
          <option value="VENCIDO">Vencido</option>
        </select>
        <button onClick={load} className="bg-black text-white rounded px-3 py-2">Filtrar</button>
      </div>
      {loading && <div>Carregando lotes...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border">Código</th>
              <th className="text-left p-2 border">Produto</th>
              <th className="text-left p-2 border">Depósito</th>
              <th className="text-left p-2 border">Validade</th>
              <th className="text-left p-2 border">Quantidade</th>
              <th className="text-left p-2 border">Status</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((l) => (
              <tr key={l.id}>
                <td className="p-2 border">{l.codigo_lote}</td>
                <td className="p-2 border">{l.produto_nome}</td>
                <td className="p-2 border">{l.deposito_nome}</td>
                <td className="p-2 border">{l.data_validade ? new Date(l.data_validade).toLocaleDateString('pt-BR') : '-'}</td>
                <td className="p-2 border">{l.quantidade_atual}</td>
                <td className="p-2 border">{l.status_validade ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

