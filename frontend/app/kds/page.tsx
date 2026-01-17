'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'

type ItemVenda = {
  id: string
  produto: string
  produto_nome: string
  venda: string
  quantidade: number
  status_producao: 'PENDENTE' | 'EM_PREPARO' | 'PRONTO' | 'ENTREGUE'
}

export default function KdsPage() {
  const [items, setItems] = useState<ItemVenda[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string>('PENDENTE')

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<any>(`/itens-venda/?page_size=200&status_producao=${status}`)
      setItems(res?.results ?? res ?? [])
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar itens')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status])

  const act = async (id: string, action: 'preparar' | 'pronto' | 'entregar') => {
    try {
      await request.post<any>(`/itens-venda/${id}/${action}/`)
      await load()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao atualizar status')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">KDS</h1>
      <div className="mb-3">
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="border rounded px-3 py-2">
          <option value="PENDENTE">Pendentes</option>
          <option value="EM_PREPARO">Em Preparo</option>
          <option value="PRONTO">Prontos</option>
          <option value="ENTREGUE">Entregues</option>
        </select>
      </div>
      {loading && <div>Carregando...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {items.map((i) => (
            <div key={i.id} className="border rounded p-3">
              <div className="font-medium">{i.produto_nome}</div>
              <div className="text-sm text-gray-600">Qtd: {i.quantidade}</div>
              <div className="mt-2 text-xs">Status: {i.status_producao}</div>
              <div className="mt-2 flex gap-2">
                {i.status_producao === 'PENDENTE' && (
                  <button onClick={() => act(i.id, 'preparar')} className="border rounded px-3 py-1">Preparar</button>
                )}
                {i.status_producao === 'EM_PREPARO' && (
                  <button onClick={() => act(i.id, 'pronto')} className="border rounded px-3 py-1">Pronto</button>
                )}
                {i.status_producao === 'PRONTO' && (
                  <button onClick={() => act(i.id, 'entregar')} className="border rounded px-3 py-1">Entregar</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

