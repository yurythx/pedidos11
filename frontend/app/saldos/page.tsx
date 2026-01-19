'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/Table'
import { Search } from 'lucide-react'

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

  const saldos = data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Gestão de Estoque</h1>
          <p className="text-gray-500 mt-1">Visão geral dos saldos por depósito</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <label className="label">Produto (SKU)</label>
          <div className="relative">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
             <input
              placeholder="Buscar por SKU..."
              value={produtoSku}
              onChange={(e) => setProdutoSku(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">Depósito</label>
          <div className="relative">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
             <input
              placeholder="Buscar por nome do depósito..."
              value={depositoNome}
              onChange={(e) => setDepositoNome(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <button onClick={load} className="btn btn-secondary w-full">
           Filtrar
        </button>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando saldos...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Produto</TableHead>
              <TableHead>Depósito</TableHead>
              <TableHead>Quantidade</TableHead>
              <TableHead>Disponível</TableHead>
              <TableHead>Atualizado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {saldos.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                  Nenhum saldo encontrado.
                </TableCell>
              </TableRow>
            ) : (
              saldos.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>
                    <div className="font-medium text-gray-900">{s.produto_nome}</div>
                    {s.produto_sku && <div className="text-xs text-gray-500 mt-0.5">SKU: {s.produto_sku}</div>}
                  </TableCell>
                  <TableCell>{s.deposito_nome}</TableCell>
                  <TableCell className="font-medium">{s.quantidade}</TableCell>
                  <TableCell className="font-bold text-green-600">{s.disponivel}</TableCell>
                  <TableCell>
                    <div className="text-xs text-gray-500">
                      {new Date(s.updated_at).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(s.updated_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      )}
    </div>
  )
}

