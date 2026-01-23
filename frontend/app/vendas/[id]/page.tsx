'use client'

import React, { useEffect, useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import type { VendaDetail, Produto } from '../../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../src/components/ui/Table'
import { ArrowLeft, Plus, Trash2, CheckCircle, XCircle, AlertTriangle, Package } from 'lucide-react'
import { formatBRL } from '../../../src/utils/currency'
import Link from 'next/link'

export default function VendaDetalhesPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const id = params.id

  const [venda, setVenda] = useState<VendaDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Estados para adicionar item
  const [produtos, setProdutos] = useState<Produto[]>([])
  const [produtoId, setProdutoId] = useState<string>('')
  const [quantidade, setQuantidade] = useState<string>('1')
  const [descontoItem, setDescontoItem] = useState<string>('0')
  const [addingItem, setAddingItem] = useState(false)

  // Estados para finalizar
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [depositoId, setDepositoId] = useState<string>('')
  const [finalizing, setFinalizing] = useState(false)

  const loadVenda = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<VendaDetail>(`/vendas/${id}/`)
      setVenda(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar venda')
    } finally {
      setLoading(false)
    }
  }, [id])

  const loadProdutos = async () => {
    try {
      const res = await request.get<any>('/produtos/?page_size=200')
      setProdutos(res?.results ?? res ?? [])
    } catch {}
  }

  const loadDepositos = async () => {
    try {
      const res = await request.get<any>('/depositos/?page_size=100')
      setDepositos(res?.results ?? res ?? [])
    } catch {}
  }

  useEffect(() => {
    loadVenda()
    loadProdutos()
    loadDepositos()
  }, [loadVenda])

  const onAdicionarItem = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!produtoId) return

    setAddingItem(true)
    try {
      await request.post<any>('/itens-venda/', {
        venda: id,
        produto: produtoId,
        quantidade: Number(quantidade),
        desconto: Number(descontoItem),
      })
      setProdutoId('')
      setQuantidade('1')
      setDescontoItem('0')
      loadVenda() // Recarrega para atualizar totais e lista
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao adicionar item')
    } finally {
      setAddingItem(false)
    }
  }

  const onRemoverItem = async (itemId: string) => {
    if (!confirm('Remover item?')) return
    try {
      await request.delete(`/itens-venda/${itemId}/`)
      loadVenda()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao remover item')
    }
  }

  const onFinalizar = async () => {
    if (!depositoId) {
      alert('Selecione um depósito para baixar o estoque')
      return
    }
    if (!confirm('Tem certeza que deseja finalizar a venda? Isso irá baixar o estoque.')) return

    setFinalizing(true)
    try {
      await request.post(`/vendas/${id}/finalizar/`, { deposito_id: depositoId })
      loadVenda()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao finalizar venda')
    } finally {
      setFinalizing(false)
    }
  }

  const onCancelar = async () => {
    const motivo = prompt('Motivo do cancelamento (opcional):')
    if (motivo === null) return // Clicou em cancelar no prompt

    try {
      await request.post(`/vendas/${id}/cancelar/`, { motivo })
      loadVenda()
    } catch (err: any) {
      alert(err?.message ?? 'Erro ao cancelar venda')
    }
  }

  const onValidarEstoque = async () => {
    if (!depositoId) {
        alert('Selecione um depósito primeiro')
        return
    }
    try {
        const res = await request.get<any>(`/vendas/${id}/validar_estoque/?deposito_id=${depositoId}`)
        // Exibe resultado de forma amigável
        let msg = 'Validação de Estoque:\n\n'
        if (res.ok) {
            msg += '✅ Todo o estoque está disponível!'
        } else {
            msg += '⚠️ Problemas de estoque:\n'
            res.missing?.forEach((m: any) => {
                msg += `- ${m.produto}: Faltam ${m.falta} (Disponível: ${m.disponivel})\n`
            })
        }
        alert(msg)
    } catch (err: any) {
        alert('Erro ao validar estoque')
    }
  }

  if (loading && !venda) {
    return <div className="text-center py-12 text-gray-500">Carregando detalhes...</div>
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-4">{error}</div>
        <Link href="/vendas" className="btn btn-secondary">Voltar para Vendas</Link>
      </div>
    )
  }

  if (!venda) return null

  const isAberta = venda.status === 'ABERTA'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/vendas" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-500" />
          </Link>
          <div>
            <h1 className="heading-1 flex items-center gap-3">
              Venda #{venda.numero}
              <span className={`
                px-3 py-1 rounded-full text-sm font-bold border
                ${venda.status === 'FINALIZADA' ? 'bg-green-50 text-green-700 border-green-200' : 
                  venda.status === 'CANCELADA' ? 'bg-red-50 text-red-700 border-red-200' : 
                  'bg-blue-50 text-blue-700 border-blue-200'}
              `}>
                {venda.status}
              </span>
            </h1>
            <p className="text-gray-500 mt-1">
              {venda.cliente_nome ?? 'Cliente Balcão'} • {new Date(venda.data_emissao).toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
        
        <div className="text-right">
            <div className="text-sm text-gray-500">Total Líquido</div>
            <div className="text-3xl font-bold text-gray-900">{formatBRL(venda.total_liquido)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Coluna Principal: Itens */}
        <div className="lg:col-span-2 space-y-6">
            <div className="card min-h-[400px]">
                <h2 className="heading-2 mb-4 flex items-center justify-between">
                    Itens da Venda
                    <span className="text-sm font-normal text-gray-500">{venda.itens.length} itens</span>
                </h2>
                
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Produto</TableHead>
                            <TableHead className="w-24 text-center">Qtd</TableHead>
                            <TableHead className="w-32 text-right">Unitário</TableHead>
                            <TableHead className="w-32 text-right">Total</TableHead>
                            {isAberta && <TableHead className="w-12"><span className="sr-only">Ações</span></TableHead>}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {venda.itens.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-8 text-gray-400">
                                    Nenhum item adicionado
                                </TableCell>
                            </TableRow>
                        )}
                        {venda.itens.map((item) => (
                            <TableRow key={item.id}>
                                <TableCell>
                                    <div className="font-medium">{item.produto_nome}</div>
                                    {item.desconto > 0 && (
                                        <div className="text-xs text-green-600">Desc: {formatBRL(item.desconto)}</div>
                                    )}
                                </TableCell>
                                <TableCell className="text-center">{item.quantidade}</TableCell>
                                <TableCell className="text-right">{formatBRL(item.preco_unitario)}</TableCell>
                                <TableCell className="text-right font-bold">{formatBRL(item.subtotal)}</TableCell>
                                {isAberta && (
                                    <TableCell>
                                        <button 
                                            onClick={() => onRemoverItem(item.id)}
                                            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </TableCell>
                                )}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>

        {/* Sidebar: Ações */}
        <div className="space-y-6">
            {isAberta ? (
                <>
                    {/* Card Adicionar Item */}
                    <div className="card bg-blue-50 border-blue-100">
                        <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2">
                            <Plus className="w-5 h-5" /> Adicionar Produto
                        </h3>
                        <form onSubmit={onAdicionarItem} className="space-y-3">
                            <div>
                                <select 
                                    className="input bg-white"
                                    value={produtoId}
                                    onChange={(e) => setProdutoId(e.target.value)}
                                    required
                                >
                                    <option value="">Selecione o produto...</option>
                                    {produtos.map(p => (
                                        <option key={p.id} value={p.id}>{p.nome} ({formatBRL(p.preco_venda)})</option>
                                    ))}
                                </select>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <input 
                                        type="number" 
                                        className="input bg-white" 
                                        placeholder="Qtd" 
                                        value={quantidade}
                                        onChange={(e) => setQuantidade(e.target.value)}
                                        min="1"
                                    />
                                </div>
                                <div>
                                    <input 
                                        type="number" 
                                        className="input bg-white" 
                                        placeholder="Desc (R$)" 
                                        value={descontoItem}
                                        onChange={(e) => setDescontoItem(e.target.value)}
                                        min="0"
                                        step="0.01"
                                    />
                                </div>
                            </div>
                            <button 
                                type="submit" 
                                disabled={addingItem}
                                className="btn btn-primary w-full shadow-none"
                            >
                                {addingItem ? 'Adicionando...' : 'Adicionar'}
                            </button>
                        </form>
                    </div>

                    {/* Card Finalização */}
                    <div className="card border-l-4 border-l-green-500">
                        <h3 className="font-bold text-gray-900 mb-4">Finalizar Venda</h3>
                        <div className="space-y-3">
                            <div>
                                <label className="text-sm font-medium text-gray-700 mb-1 block">Depósito de Saída</label>
                                <select 
                                    className="input"
                                    value={depositoId}
                                    onChange={(e) => setDepositoId(e.target.value)}
                                >
                                    <option value="">Selecione...</option>
                                    {depositos.map(d => (
                                        <option key={d.id} value={d.id}>{d.nome}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-2 pt-2">
                                <button 
                                    onClick={onValidarEstoque}
                                    className="btn btn-secondary text-xs"
                                    disabled={!depositoId}
                                >
                                    <Package className="w-4 h-4 mr-1" /> Validar
                                </button>
                                <button 
                                    onClick={onFinalizar}
                                    className="btn btn-primary bg-green-600 hover:bg-green-700 text-xs"
                                    disabled={!depositoId || finalizing}
                                >
                                    <CheckCircle className="w-4 h-4 mr-1" /> Finalizar
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Botão Cancelar */}
                    <button 
                        onClick={onCancelar}
                        className="btn w-full text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100"
                    >
                        <XCircle className="w-4 h-4 mr-2" />
                        Cancelar Venda
                    </button>
                </>
            ) : (
                <div className="card bg-gray-50 text-center py-8">
                    <p className="text-gray-500">Esta venda está {venda.status.toLowerCase()} e não pode ser alterada.</p>
                </div>
            )}
        </div>
      </div>
    </div>
  )
}
