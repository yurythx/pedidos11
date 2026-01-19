'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import { useAuthStore } from '../../src/features/auth/store'
import type { Paginacao } from '../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, Search, Eye, Trash2 } from 'lucide-react'
import { formatBRL } from '../../src/utils/currency'

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
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

  const loadVendas = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<Paginacao<Venda>>(`/vendas/?page_size=${pageSize}&page=${page}`)
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
  }, [page, pageSize])

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
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="heading-1">Vendas</h1>
        {/* Futuramente mover formulário para um modal ou página dedicada */}
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 className="heading-2 mb-4">Nova Venda</h2>
        <form onSubmit={onCreateVenda} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Cliente</label>
              <select
                className="input"
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
              <label className="label">Tipo de Pagamento</label>
              <select
                className="input"
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
              <label className="label">Observações</label>
              <input
                className="input"
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={creating}
            className="btn btn-primary w-full md:w-auto"
          >
            <Plus className="w-5 h-5 mr-2" />
            {creating ? 'Criando...' : 'Criar Venda'}
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <h2 className="font-medium mb-4 text-gray-900">Operações</h2>
          <div className="space-y-4">
            <div>
              <label className="label">Venda Selecionada</label>
              <select
                className="input"
                value={selectedVendaId}
                onChange={(e) => setSelectedVendaId(e.target.value)}
              >
                <option value="">Selecione para gerenciar</option>
                {(data?.results ?? []).map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.numero} — {v.cliente_nome ?? 'Balcão'} ({v.status})
                  </option>
                ))}
              </select>
            </div>
            {selectedVendaId && (
              <>
                 <div>
                  <label className="label">Depósito de Saída</label>
                  <select
                    className="input"
                    value={depositoId}
                    onChange={(e) => setDepositoId(e.target.value)}
                  >
                    <option value="">Selecione</option>
                    {depositos.map((d) => (
                      <option key={d.id} value={d.id}>{d.nome}</option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-col gap-2">
                  <button onClick={(e: any) => onValidarEstoque(e)} className="btn btn-secondary w-full">Validar Estoque</button>
                  <button onClick={(e: any) => onFinalizarVenda(e)} className="btn btn-primary w-full">Finalizar Venda</button>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="font-medium mb-4 text-gray-900">Adicionar Itens</h2>
           <form onSubmit={onAdicionarItem} className="space-y-4">
            <div>
              <label className="label">Produto</label>
              <select
                className="input"
                value={produtoId}
                onChange={(e) => setProdutoId(e.target.value)}
                disabled={!selectedVendaId}
              >
                <option value="">Selecione</option>
                {produtos.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nome}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Qtd.</label>
                <input
                  className="input"
                  value={quantidade}
                  onChange={(e) => setQuantidade(e.target.value)}
                  disabled={!selectedVendaId}
                />
              </div>
              <div>
                <label className="label">Desc. (R$)</label>
                <input
                  className="input"
                  value={descontoItem}
                  onChange={(e) => setDescontoItem(e.target.value)}
                  disabled={!selectedVendaId}
                />
              </div>
            </div>
            <button type="submit" className="btn btn-secondary w-full" disabled={!selectedVendaId}>Adicionar Item</button>
          </form>
        </div>

         <div className="card">
          <h2 className="font-medium mb-4 text-gray-900">Cancelamento</h2>
          <form onSubmit={onCancelarVenda} className="space-y-4">
            <div>
              <label className="label">Motivo</label>
              <input
                className="input"
                value={motivoCancelamento}
                onChange={(e) => setMotivoCancelamento(e.target.value)}
                placeholder="Opcional"
                disabled={!selectedVendaId}
              />
            </div>
            <button type="submit" className="btn btn-secondary w-full text-red-600 hover:bg-red-50" disabled={!selectedVendaId}>Cancelar Venda</button>
          </form>
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando vendas...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      
      {!loading && !error && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Número</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead>Vendedor</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Itens</TableHead>
              <TableHead>Total</TableHead>
              <TableHead>Emissão</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(data?.results ?? []).map((v) => (
              <TableRow 
                key={v.id} 
                onClick={() => setSelectedVendaId(v.id)}
                className={selectedVendaId === v.id ? 'bg-red-50' : ''}
              >
                <TableCell><span className="font-mono font-medium">{v.numero}</span></TableCell>
                <TableCell>{v.cliente_nome ?? 'Balcão'}</TableCell>
                <TableCell>{v.vendedor_nome ?? '-'}</TableCell>
                <TableCell>
                  <span className={`
                    px-2 py-1 rounded-full text-xs font-bold
                    ${v.status === 'FINALIZADA' ? 'bg-green-100 text-green-700' : 
                      v.status === 'CANCELADA' ? 'bg-red-100 text-red-700' : 
                      'bg-blue-100 text-blue-700'}
                  `}>
                    {v.status}
                  </span>
                </TableCell>
                <TableCell>{v.quantidade_itens}</TableCell>
                <TableCell className="font-medium">{formatBRL(v.total_liquido)}</TableCell>
                <TableCell>{new Date(v.data_emissao).toLocaleDateString('pt-BR')}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {!loading && !error && (
         <TablePagination
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
          hasMore={(data?.results?.length ?? 0) >= pageSize}
        />
      )}

      {vendaDetail && (
        <div className="card mt-6">
          <h2 className="heading-2 mb-4">Itens da Venda #{vendaDetail.numero}</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Produto</TableHead>
                <TableHead>Qtd</TableHead>
                <TableHead>Preço Unit.</TableHead>
                <TableHead>Desconto</TableHead>
                <TableHead>Subtotal</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vendaDetail.itens.map((i) => (
                <TableRow key={i.id}>
                  <TableCell>{i.produto_nome}</TableCell>
                  <TableCell>{i.quantidade}</TableCell>
                  <TableCell>{formatBRL(i.preco_unitario)}</TableCell>
                  <TableCell>{formatBRL(i.desconto)}</TableCell>
                  <TableCell className="font-bold">{formatBRL(i.subtotal)}</TableCell>
                  <TableCell>
                    {vendaDetail.status === 'ABERTA' && (
                      <button
                        onClick={() => onRemoverItem(i.id)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title="Remover Item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

