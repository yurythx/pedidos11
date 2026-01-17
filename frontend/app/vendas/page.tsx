'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { useAuthStore } from '../../src/features/auth/store'
import type { Paginacao, Usuario } from '../../src/types'

type Venda = {
  id: string
  numero: string
  cliente: string | null
  cliente_nome: string | null
  vendedor: string
  vendedor_nome: string | null
  status: 'ABERTA' | 'FINALIZADA' | 'CANCELADA'
  total_liquido: number
  quantidade_itens: number
  data_emissao: string
  data_finalizacao?: string | null
}

type Cliente = {
  id: string
  nome: string
}

type VendaDetail = Venda & {
  itens: Array<{
    id: string
    produto: string
    produto_nome: string
    quantidade: number
    preco_unitario: number
    desconto: number
    subtotal: number
  }>
}

type ProdutoOption = {
  id: string
  nome: string
  preco_venda: number
}

export default function VendasPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<Paginacao<Venda> | null>(null)
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [clienteId, setClienteId] = useState<string>('')
  const [tipoPagamento, setTipoPagamento] = useState<string>('DINHEIRO')
  const [observacoes, setObservacoes] = useState<string>('')
  const [creating, setCreating] = useState(false)
  const [selectedVendaId, setSelectedVendaId] = useState<string>('')
  const [depositoId, setDepositoId] = useState<string>('')
  const [motivoCancelamento, setMotivoCancelamento] = useState<string>('')
  const [vendaDetail, setVendaDetail] = useState<VendaDetail | null>(null)
  const [produtos, setProdutos] = useState<ProdutoOption[]>([])
  const [produtoId, setProdutoId] = useState<string>('')
  const [quantidade, setQuantidade] = useState<string>('1')
  const [descontoItem, setDescontoItem] = useState<string>('0')

  const loadVendas = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<Paginacao<Venda>>('/vendas/?page_size=20')
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar vendas')
    } finally {
      setLoading(false)
    }
  }

  const loadClientes = async () => {
    try {
      const res = await request.get<any>('/clientes/?page_size=100')
      const list: Cliente[] = res?.results ?? res ?? []
      setClientes(list)
    } catch {
      setClientes([])
    }
  }
  const loadDepositos = async () => {
    try {
      const res = await request.get<any>('/depositos/?page_size=100')
      const list: { id: string; nome: string }[] = res?.results ?? res ?? []
      setDepositos(list)
    } catch {
      setDepositos([])
    }
  }
  const loadProdutos = async () => {
    try {
      const res = await request.get<any>('/produtos/?page_size=200')
      const list: ProdutoOption[] = (res?.results ?? res ?? []).map((p: any) => ({
        id: String(p.id),
        nome: p.nome,
        preco_venda: Number(p.preco_venda ?? 0),
      }))
      setProdutos(list)
    } catch {
      setProdutos([])
    }
  }
  const loadVendaDetail = async (id: string) => {
    if (!id) {
      setVendaDetail(null)
      return
    }
    try {
      const res = await request.get<VendaDetail>(`/vendas/${id}/`)
      setVendaDetail(res)
    } catch {
      setVendaDetail(null)
    }
  }

  useEffect(() => {
    loadVendas()
    loadClientes()
    loadDepositos()
    loadProdutos()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadVendaDetail(selectedVendaId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedVendaId])

  const onCreateVenda = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError(null)
    try {
      const payload: any = {
        vendedor: user?.id,
        tipo_pagamento: tipoPagamento,
        observacoes,
      }
      if (clienteId) payload.cliente = clienteId
      await request.post<any>('/vendas/', payload)
      setClienteId('')
      setTipoPagamento('DINHEIRO')
      setObservacoes('')
      await loadVendas()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao criar venda')
    } finally {
      setCreating(false)
    }
  }

  const onValidarEstoque = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedVendaId || !depositoId) {
      setError('Selecione venda e depósito para validar estoque')
      return
    }
    setError(null)
    try {
      const res = await request.get<any>(`/vendas/${selectedVendaId}/validar_estoque/?deposito_id=${depositoId}`)
      alert(`Estoque: ${JSON.stringify(res)}`)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao validar estoque')
    }
  }

  const onFinalizarVenda = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedVendaId || !depositoId) {
      setError('Selecione venda e depósito para finalizar')
      return
    }
    setError(null)
    try {
      await request.post<any>(`/vendas/${selectedVendaId}/finalizar/`, { deposito_id: depositoId })
      setSelectedVendaId('')
      setDepositoId('')
      await loadVendas()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao finalizar venda')
    }
  }

  const onCancelarVenda = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedVendaId) {
      setError('Selecione venda para cancelar')
      return
    }
    setError(null)
    try {
      await request.post<any>(`/vendas/${selectedVendaId}/cancelar/`, { motivo: motivoCancelamento })
      setSelectedVendaId('')
      setMotivoCancelamento('')
      await loadVendas()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao cancelar venda')
    }
  }

  const onAdicionarItem = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedVendaId || !produtoId) {
      setError('Selecione venda e produto para adicionar item')
      return
    }
    setError(null)
    try {
      await request.post<any>('/itens-venda/', {
        venda: selectedVendaId,
        produto: produtoId,
        quantidade: Number(quantidade),
        desconto: Number(descontoItem),
      })
      setQuantidade('1')
      setDescontoItem('0')
      await loadVendaDetail(selectedVendaId)
      await loadVendas()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao adicionar item')
    }
  }

  const onRemoverItem = async (itemId: string) => {
    if (!confirm('Remover item?')) return
    try {
      await request.delete<any>(`/itens-venda/${itemId}/`)
      await loadVendaDetail(selectedVendaId)
      await loadVendas()
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao remover item')
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Vendas</h1>
      <form onSubmit={onCreateVenda} className="space-y-2 mb-4 border p-3 rounded">
        <div className="grid grid-cols-4 gap-2">
          <div className="col-span-2">
            <label className="block text-sm">Cliente</label>
            <select
              className="mt-1 w-full border rounded px-2 py-1"
              value={clienteId}
              onChange={(e) => setClienteId(e.target.value)}
            >
              <option value="">Selecione (opcional)</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm">Tipo de Pagamento</label>
            <select
              className="mt-1 w-full border rounded px-2 py-1"
              value={tipoPagamento}
              onChange={(e) => setTipoPagamento(e.target.value)}
            >
              <option value="DINHEIRO">Dinheiro</option>
              <option value="CARTAO">Cartão</option>
              <option value="PIX">Pix</option>
              <option value="BOLETO">Boleto</option>
            </select>
          </div>
          <div>
            <label className="block text-sm">Observações</label>
            <input
              className="mt-1 w-full border rounded px-2 py-1"
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={creating}
          className="bg-black text-white rounded px-3 py-2 disabled:opacity-60"
        >
          {creating ? 'Criando...' : 'Criar Venda'}
        </button>
      </form>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="border p-3 rounded">
          <h2 className="font-medium mb-2">Operações por Venda</h2>
          <div className="space-y-2">
            <label className="block text-sm">Venda</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={selectedVendaId}
              onChange={(e) => setSelectedVendaId(e.target.value)}
            >
              <option value="">Selecione</option>
              {(data?.results ?? []).map((v) => (
                <option key={v.id} value={v.id}>
                  {v.numero} — {v.cliente_nome ?? 'Balcão'} ({v.status})
                </option>
              ))}
            </select>
            <label className="block text-sm">Depósito</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={depositoId}
              onChange={(e) => setDepositoId(e.target.value)}
            >
              <option value="">Selecione</option>
              {depositos.map((d) => (
                <option key={d.id} value={d.id}>{d.nome}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <form onSubmit={onValidarEstoque}>
                <button type="submit" className="border rounded px-3 py-2">Validar Estoque</button>
              </form>
              <form onSubmit={onFinalizarVenda}>
                <button type="submit" className="border rounded px-3 py-2">Finalizar</button>
              </form>
            </div>
          </div>
        </div>
        <div className="border p-3 rounded">
          <h2 className="font-medium mb-2">Cancelamento</h2>
          <form onSubmit={onCancelarVenda} className="space-y-2">
            <label className="block text-sm">Motivo</label>
            <input
              className="w-full border rounded px-2 py-1"
              value={motivoCancelamento}
              onChange={(e) => setMotivoCancelamento(e.target.value)}
              placeholder="Opcional"
            />
            <button type="submit" className="border rounded px-3 py-2">Cancelar Venda</button>
          </form>
        </div>
        <div className="border p-3 rounded">
          <h2 className="font-medium mb-2">Itens da Venda</h2>
          <form onSubmit={onAdicionarItem} className="space-y-2">
            <label className="block text-sm">Produto</label>
            <select
              className="w-full border rounded px-2 py-1"
              value={produtoId}
              onChange={(e) => setProdutoId(e.target.value)}
            >
              <option value="">Selecione</option>
              {produtos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nome}
                </option>
              ))}
            </select>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-sm">Quantidade</label>
                <input
                  className="w-full border rounded px-2 py-1"
                  value={quantidade}
                  onChange={(e) => setQuantidade(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm">Desconto</label>
                <input
                  className="w-full border rounded px-2 py-1"
                  value={descontoItem}
                  onChange={(e) => setDescontoItem(e.target.value)}
                />
              </div>
              <div className="flex items-end">
                <button type="submit" className="border rounded px-3 py-2 w-full">Adicionar</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {loading && <div>Carregando vendas...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && (
        <table className="w-full border">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left p-2 border">Número</th>
              <th className="text-left p-2 border">Cliente</th>
              <th className="text-left p-2 border">Vendedor</th>
              <th className="text-left p-2 border">Status</th>
              <th className="text-left p-2 border">Itens</th>
              <th className="text-left p-2 border">Total</th>
              <th className="text-left p-2 border">Emissão</th>
            </tr>
          </thead>
          <tbody>
            {(data?.results ?? []).map((v) => (
              <tr key={v.id}>
                <td className="p-2 border">{v.numero}</td>
                <td className="p-2 border">{v.cliente_nome ?? '-'}</td>
                <td className="p-2 border">{v.vendedor_nome ?? '-'}</td>
                <td className="p-2 border">{v.status}</td>
                <td className="p-2 border">{v.quantidade_itens}</td>
                <td className="p-2 border">R$ {Number(v.total_liquido).toFixed(2)}</td>
                <td className="p-2 border">{new Date(v.data_emissao).toLocaleString('pt-BR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {vendaDetail && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold mb-2">Itens da Venda #{vendaDetail.numero}</h2>
          <table className="w-full border">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left p-2 border">Produto</th>
                <th className="text-left p-2 border">Quantidade</th>
                <th className="text-left p-2 border">Preço</th>
                <th className="text-left p-2 border">Desconto</th>
                <th className="text-left p-2 border">Subtotal</th>
                <th className="text-left p-2 border">Ações</th>
              </tr>
            </thead>
            <tbody>
              {vendaDetail.itens.map((i) => (
                <tr key={i.id}>
                  <td className="p-2 border">{i.produto_nome}</td>
                  <td className="p-2 border">{i.quantidade}</td>
                  <td className="p-2 border">R$ {Number(i.preco_unitario).toFixed(2)}</td>
                  <td className="p-2 border">R$ {Number(i.desconto).toFixed(2)}</td>
                  <td className="p-2 border">R$ {Number(i.subtotal).toFixed(2)}</td>
                  <td className="p-2 border">
                    <button
                      onClick={() => onRemoverItem(i.id)}
                      className="text-sm underline"
                    >
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

