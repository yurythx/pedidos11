'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Calendar, 
  DollarSign, 
  User, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Clock,
  CreditCard
} from 'lucide-react'
import { request } from '../../../../src/lib/http/request'
import { ContaPagar, StatusConta, TipoPagamento } from '../../../../src/types'

export default function DetalheContaPagarPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [conta, setConta] = useState<ContaPagar | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Modal states
  const [showBaixaModal, setShowBaixaModal] = useState(false)
  const [baixaData, setBaixaData] = useState({
    data_pagamento: new Date().toISOString().split('T')[0],
    tipo_pagamento: 'DINHEIRO' as TipoPagamento,
    valor_juros: 0,
    valor_multa: 0,
    valor_desconto: 0
  })
  const [baixaLoading, setBaixaLoading] = useState(false)

  const fetchConta = useCallback(async () => {
    try {
      setLoading(true)
      const data = await request.get<ContaPagar>(`/api/contas-pagar/${params.id}/`)
      setConta(data)
    } catch (err: any) {
      setError('Erro ao carregar detalhes da conta.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [params.id])

  useEffect(() => {
    fetchConta()
  }, [fetchConta])

  const handleBaixa = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!conta) return

    setBaixaLoading(true)
    try {
      await request.post(`/api/contas-pagar/${conta.id}/baixar/`, baixaData)
      setShowBaixaModal(false)
      fetchConta() // Recarrega os dados
    } catch (err: any) {
      alert('Erro ao realizar baixa: ' + (err.message || 'Erro desconhecido'))
    } finally {
      setBaixaLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  if (loading) return <div className="p-8 text-center"><span className="loading loading-spinner loading-lg"></span></div>
  if (error || !conta) return <div className="p-8 text-center text-error">{error || 'Conta não encontrada'}</div>

  const getStatusBadge = (status: StatusConta, estaVencida: boolean) => {
    if (status === 'PAGA') return <div className="badge badge-success gap-2 p-3"><CheckCircle className="w-4 h-4" /> Paga</div>
    if (status === 'CANCELADA') return <div className="badge badge-ghost gap-2 p-3"><XCircle className="w-4 h-4" /> Cancelada</div>
    if (estaVencida) return <div className="badge badge-error gap-2 p-3"><AlertCircle className="w-4 h-4" /> Vencida</div>
    return <div className="badge badge-warning gap-2 p-3"><Clock className="w-4 h-4" /> Pendente</div>
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Link href="/financeiro/contas-pagar" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-500" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Detalhes da Conta a Pagar</h1>
          <div className="flex items-center gap-2 text-sm text-gray-500">
             <span>#{conta.id.slice(0, 8)}</span>
             <span>•</span>
             <span>Criada em {formatDate(conta.created_at)}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card Principal */}
        <div className="card bg-base-100 shadow-xl md:col-span-2">
          <div className="card-body">
            <div className="flex justify-between items-start">
               <div>
                  <h2 className="card-title text-2xl mb-1">{conta.descricao}</h2>
                  <p className="text-gray-500 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {conta.fornecedor_nome || 'Fornecedor não informado'}
                  </p>
               </div>
               {getStatusBadge(conta.status, conta.esta_vencida)}
            </div>

            <div className="divider"></div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase block mb-1">Categoria</span>
                <span className="badge badge-outline">{conta.categoria}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase block mb-1">Nº Documento</span>
                <span className="font-mono">{conta.numero_documento || '-'}</span>
              </div>
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase block mb-1">Emissão</span>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>{formatDate(conta.data_emissao)}</span>
                </div>
              </div>
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase block mb-1">Vencimento</span>
                <div className={`flex items-center gap-2 ${conta.esta_vencida && conta.status === 'PENDENTE' ? 'text-error font-bold' : ''}`}>
                  <Calendar className="w-4 h-4" />
                  <span>{formatDate(conta.data_vencimento)}</span>
                </div>
              </div>
            </div>

            {conta.observacoes && (
              <div className="mt-6 p-4 bg-gray-50 rounded-xl">
                <span className="text-xs font-bold text-gray-500 uppercase block mb-1">Observações</span>
                <p className="text-sm text-gray-700">{conta.observacoes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Card Financeiro */}
        <div className="space-y-6">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-lg flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-primary" />
                Valores
              </h3>
              
              <div className="space-y-3 mt-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Valor Original</span>
                  <span>{formatCurrency(conta.valor_original)}</span>
                </div>
                {conta.valor_juros > 0 && (
                  <div className="flex justify-between text-sm text-error">
                    <span>+ Juros</span>
                    <span>{formatCurrency(conta.valor_juros)}</span>
                  </div>
                )}
                {conta.valor_multa > 0 && (
                  <div className="flex justify-between text-sm text-error">
                    <span>+ Multa</span>
                    <span>{formatCurrency(conta.valor_multa)}</span>
                  </div>
                )}
                {conta.valor_desconto > 0 && (
                  <div className="flex justify-between text-sm text-success">
                    <span>- Desconto</span>
                    <span>{formatCurrency(conta.valor_desconto)}</span>
                  </div>
                )}
                
                <div className="divider my-2"></div>
                
                <div className="flex justify-between items-center">
                  <span className="font-bold text-lg">Total</span>
                  <span className="font-bold text-2xl text-primary">{formatCurrency(conta.valor_total)}</span>
                </div>
              </div>

              {(conta.status === 'PENDENTE' || conta.status === 'VENCIDA') && (
                <button 
                  className="btn btn-primary w-full mt-6"
                  onClick={() => setShowBaixaModal(true)}
                >
                  <DollarSign className="w-4 h-4 mr-2" />
                  Realizar Pagamento
                </button>
              )}
            </div>
          </div>

          {conta.status === 'PAGA' && (
             <div className="card bg-success/10 border border-success/20">
                <div className="card-body p-4">
                   <h3 className="font-bold text-success flex items-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Pagamento Realizado
                   </h3>
                   <div className="text-sm space-y-1 mt-2">
                      <p>Data: <b>{formatDate(conta.data_pagamento)}</b></p>
                      <p>Forma: <b>{conta.tipo_pagamento}</b></p>
                   </div>
                </div>
             </div>
          )}
        </div>
      </div>

      {/* Modal de Baixa */}
      {showBaixaModal && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Realizar Pagamento</h3>
            <form onSubmit={handleBaixa} className="space-y-4">
              
              <div className="form-control">
                <label className="label">Data do Pagamento</label>
                <input 
                  type="date" 
                  className="input input-bordered"
                  value={baixaData.data_pagamento}
                  onChange={e => setBaixaData({...baixaData, data_pagamento: e.target.value})}
                  required
                />
              </div>

              <div className="form-control">
                <label className="label">Forma de Pagamento</label>
                <select 
                  className="select select-bordered"
                  value={baixaData.tipo_pagamento}
                  onChange={e => setBaixaData({...baixaData, tipo_pagamento: e.target.value as TipoPagamento})}
                >
                  <option value="DINHEIRO">Dinheiro</option>
                  <option value="PIX">Pix</option>
                  <option value="CARTAO_DEBITO">Cartão Débito</option>
                  <option value="CARTAO_CREDITO">Cartão Crédito</option>
                  <option value="BOLETO">Boleto</option>
                  <option value="TRANSFERENCIA">Transferência</option>
                  <option value="CHEQUE">Cheque</option>
                </select>
              </div>

              <div className="grid grid-cols-3 gap-2">
                 <div className="form-control">
                    <label className="label text-xs">Juros (R$)</label>
                    <input 
                      type="number" step="0.01" min="0"
                      className="input input-bordered input-sm"
                      value={baixaData.valor_juros}
                      onChange={e => setBaixaData({...baixaData, valor_juros: parseFloat(e.target.value) || 0})}
                    />
                 </div>
                 <div className="form-control">
                    <label className="label text-xs">Multa (R$)</label>
                    <input 
                      type="number" step="0.01" min="0"
                      className="input input-bordered input-sm"
                      value={baixaData.valor_multa}
                      onChange={e => setBaixaData({...baixaData, valor_multa: parseFloat(e.target.value) || 0})}
                    />
                 </div>
                 <div className="form-control">
                    <label className="label text-xs">Desconto (R$)</label>
                    <input 
                      type="number" step="0.01" min="0"
                      className="input input-bordered input-sm"
                      value={baixaData.valor_desconto}
                      onChange={e => setBaixaData({...baixaData, valor_desconto: parseFloat(e.target.value) || 0})}
                    />
                 </div>
              </div>
              
              <div className="bg-base-200 p-3 rounded-lg text-center">
                 <p className="text-xs text-gray-500 uppercase">Valor Final a Pagar</p>
                 <p className="text-xl font-bold text-primary">
                    {formatCurrency(
                       conta.valor_original + 
                       baixaData.valor_juros + 
                       baixaData.valor_multa - 
                       baixaData.valor_desconto
                    )}
                 </p>
              </div>

              <div className="modal-action">
                <button 
                  type="button" 
                  className="btn btn-ghost"
                  onClick={() => setShowBaixaModal(false)}
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={baixaLoading}
                >
                  {baixaLoading ? <span className="loading loading-spinner"></span> : 'Confirmar Pagamento'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
