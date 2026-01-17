'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

type Saldo = {
  id: string
  produto: string
  produto_nome: string
  produto_sku: string | null
  deposito: string
  deposito_nome: string
  quantidade: number
  disponivel: number
  updated_at: string
}

export default function SaldosPage() {
  const [data, setData] = useState<Saldo[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [produtoSku, setProdutoSku] = useState<string>('')
  const [depositoNome, setDepositoNome] = useState<string>('')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<any>('/saldos/?page_size=100')
      const list: Saldo[] = res?.results ?? res ?? []
      const filtered = list.filter((s) =>
        (produtoSku ? (s.produto_sku ?? '').toLowerCase().includes(produtoSku.toLowerCase()) : true) &&
        (depositoNome ? s.deposito_nome.toLowerCase().includes(depositoNome.toLowerCase()) : true)
      )
      setData(filtered)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar saldos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Saldos</h1>
      <div className="flex gap-2 mb-3">
        <input
          placeholder="Filtro por SKU do produto"
          value={produtoSku}
          onChange={(e) => setProdutoSku(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <input
          placeholder="Filtro por nome do depósito"
          value={depositoNome}
          onChange={(e) => setDepositoNome(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <button onClick={load} className="bg-black text-white rounded px-3 py-2">Filtrar</button>
      </div>
      {loading && <div>Carregando saldos...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border">Produto</th>
              <th className="text-left p-2 border">SKU</th>
              <th className="text-left p-2 border">Depósito</th>
              <th className="text-left p-2 border">Quantidade</th>
              <th className="text-left p-2 border">Disponível</th>
              <th className="text-left p-2 border">Atualizado em</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map((s) => (
              <tr key={s.id}>
                <td className="p-2 border">{s.produto_nome}</td>
                <td className="p-2 border">{s.produto_sku ?? '-'}</td>
                <td className="p-2 border">{s.deposito_nome}</td>
                <td className="p-2 border">{s.quantidade}</td>
                <td className="p-2 border">{s.disponivel}</td>
                <td className="p-2 border">{new Date(s.updated_at).toLocaleString('pt-BR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

