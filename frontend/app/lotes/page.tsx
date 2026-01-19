'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/Table'
import { Filter, Calendar } from 'lucide-react'

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

  const lotes = data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Lotes</h1>
          <p className="text-gray-500 mt-1">Controle de validade e rastreabilidade</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div>
          <label className="label">Validade Início</label>
          <div className="relative">
             <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
             <input
              type="date"
              value={validadeMin}
              onChange={(e) => setValidadeMin(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">Validade Fim</label>
          <div className="relative">
             <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
             <input
              type="date"
              value={validadeMax}
              onChange={(e) => setValidadeMax(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div>
          <label className="label">Status</label>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={statusValidade}
              onChange={(e) => setStatusValidade(e.target.value)}
              className="input pl-10"
            >
              <option value="TODOS">Todos</option>
              <option value="OK">OK</option>
              <option value="ATENCAO">Atenção</option>
              <option value="CRITICO">Crítico</option>
              <option value="VENCIDO">Vencido</option>
            </select>
          </div>
        </div>
        <button onClick={load} className="btn btn-secondary w-full">
           Filtrar
        </button>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando lotes...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl mb-4">{error}</div>}

      {!loading && !error && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Código</TableHead>
              <TableHead>Produto</TableHead>
              <TableHead>Depósito</TableHead>
              <TableHead>Validade</TableHead>
              <TableHead>Quantidade</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {lotes.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                  Nenhum lote encontrado.
                </TableCell>
              </TableRow>
            ) : (
              lotes.map((l) => (
                <TableRow key={l.id}>
                  <TableCell><span className="font-mono text-gray-600">{l.codigo_lote}</span></TableCell>
                  <TableCell><div className="font-medium text-gray-900">{l.produto_nome}</div></TableCell>
                  <TableCell>{l.deposito_nome}</TableCell>
                  <TableCell>{l.data_validade ? new Date(l.data_validade).toLocaleDateString('pt-BR') : '-'}</TableCell>
                  <TableCell>{l.quantidade_atual}</TableCell>
                  <TableCell>
                    <span className={`
                      px-2.5 py-1 rounded-full text-xs font-bold
                      ${l.status_validade === 'VENCIDO' ? 'bg-red-100 text-red-700' : 
                        l.status_validade === 'CRITICO' ? 'bg-orange-100 text-orange-700' :
                        l.status_validade === 'ATENCAO' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'}
                    `}>
                      {l.status_validade ?? '-'}
                    </span>
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

