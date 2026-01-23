'use client'
import React, { useState, useEffect } from 'react'
import { formatBRL } from '../../../../utils/currency'
import { Check, X, CreditCard, Banknote, QrCode, Building2, User } from 'lucide-react'
import { request } from '../../../../lib/http/request'
import { colaboradorService, Colaborador } from '../../../../features/partners/services/colaboradorService'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  total: number
  onConfirm: (paymentData: { 
    tipo_pagamento: string; 
    deposito_id: string; 
    valor_pago: number;
    colaborador_id?: string;
    cpf?: string;
    emitir_nfe?: boolean;
  }) => Promise<void>
}

export function PaymentModal({ isOpen, onClose, total, onConfirm }: PaymentModalProps) {
  const [tipoPagamento, setTipoPagamento] = useState('DINHEIRO')
  const [depositoId, setDepositoId] = useState('')
  const [valorPago, setValorPago] = useState<string>(total.toFixed(2))
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [colaboradorId, setColaboradorId] = useState('')
  const [loading, setLoading] = useState(false)
  const [cpf, setCpf] = useState('')
  const [emitirNFe, setEmitirNFe] = useState(false)

  useEffect(() => {
    if (isOpen) {
        setValorPago(total.toFixed(2))
        setCpf('')
        setEmitirNFe(false)
        
        // Carregar Depósitos
        request.get<any>('/depositos/?page_size=100')
            .then(res => {
                const lista = res?.results ?? res ?? []
                setDepositos(lista)
                if (lista.length > 0 && !depositoId) setDepositoId(lista[0].id)
            })
            .catch(() => setDepositos([]))
            
        // Carregar Colaboradores
        colaboradorService.getColaboradores()
            .then(res => setColaboradores((res as any)?.results || res || []))
            .catch(console.error)
    }
  }, [isOpen, total])

  if (!isOpen) return null

  const handleConfirm = async () => {
    if (!depositoId) {
        alert('Selecione um depósito de saída')
        return
    }
    
    setLoading(true)
    try {
        console.log('Enviando pagamento:', { tipoPagamento, depositoId, valorPago, colaboradorId })
        await onConfirm({
            tipo_pagamento: tipoPagamento,
            deposito_id: depositoId,
            valor_pago: parseFloat(valorPago),
            colaborador_id: colaboradorId || undefined,
            cpf: cpf.replace(/\D/g, ''),
            emitir_nfe: emitirNFe
        })
        onClose()
    } catch (e) {
        console.error(e)
    } finally {
        setLoading(false)
    }
  }

  const troco = Math.max(0, parseFloat(valorPago || '0') - total)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
            <h2 className="text-xl font-bold text-gray-800">Finalizar Pagamento</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                <X className="w-5 h-5 text-gray-500" />
            </button>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto">
            <div className="text-center">
                <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Total a Pagar</span>
                <div className="text-4xl font-extrabold text-primary mt-1">{formatBRL(total)}</div>
            </div>

            <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">Forma de Pagamento</label>
                <div className="grid grid-cols-2 gap-3">
                    <button
                        onClick={() => setTipoPagamento('DINHEIRO')}
                        className={`p-3 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${tipoPagamento === 'DINHEIRO' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-100 hover:border-gray-200 text-gray-600'}`}
                    >
                        <Banknote className="w-6 h-6" />
                        <span className="font-bold text-sm">Dinheiro</span>
                    </button>
                    <button
                        onClick={() => setTipoPagamento('PIX')}
                        className={`p-3 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${tipoPagamento === 'PIX' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-100 hover:border-gray-200 text-gray-600'}`}
                    >
                        <QrCode className="w-6 h-6" />
                        <span className="font-bold text-sm">PIX</span>
                    </button>
                    <button
                        onClick={() => setTipoPagamento('CARTAO_CREDITO')}
                        className={`p-3 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${tipoPagamento === 'CARTAO_CREDITO' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-100 hover:border-gray-200 text-gray-600'}`}
                    >
                        <CreditCard className="w-6 h-6" />
                        <span className="font-bold text-sm">Crédito</span>
                    </button>
                    <button
                        onClick={() => setTipoPagamento('CARTAO_DEBITO')}
                        className={`p-3 rounded-xl border-2 flex flex-col items-center gap-2 transition-all ${tipoPagamento === 'CARTAO_DEBITO' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-100 hover:border-gray-200 text-gray-600'}`}
                    >
                        <CreditCard className="w-6 h-6" />
                        <span className="font-bold text-sm">Débito</span>
                    </button>
                </div>
            </div>

            {tipoPagamento === 'DINHEIRO' && (
                 <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">Valor Recebido</label>
                    <input
                        type="number"
                        step="0.01"
                        value={valorPago}
                        onChange={(e) => setValorPago(e.target.value)}
                        className="w-full text-2xl font-bold p-3 border rounded-xl focus:ring-2 focus:ring-primary/20 outline-none text-right"
                    />
                    {troco > 0 && (
                        <div className="flex justify-between items-center text-green-600 font-bold px-2">
                            <span>Troco:</span>
                            <span>{formatBRL(troco)}</span>
                        </div>
                    )}
                 </div>
            )}
            
            <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Atendente / Garçom (Comissão)</label>
                <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <select
                        value={colaboradorId}
                        onChange={(e) => setColaboradorId(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-gray-50 border-none rounded-xl focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                        <option value="">Operador do Caixa (Padrão)</option>
                        {colaboradores.map(c => (
                            <option key={c.id} value={c.id}>
                                {c.nome} ({c.cargo} - {c.comissao_percentual}%)
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Depósito de Saída (Estoque)</label>
                <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <select
                        value={depositoId}
                        onChange={(e) => setDepositoId(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-gray-50 border-none rounded-xl focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                        {depositos.map(d => (
                            <option key={d.id} value={d.id}>{d.nome}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Fiscal Section */}
            <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 space-y-3">
                <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2 cursor-pointer w-full select-none">
                        <input 
                            type="checkbox" 
                            checked={emitirNFe}
                            onChange={e => setEmitirNFe(e.target.checked)}
                            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="font-bold text-blue-800">Emitir Cupom Fiscal (NFC-e)</span>
                    </label>
                </div>
                
                {emitirNFe && (
                    <div className="space-y-1 animate-in fade-in slide-in-from-top-2">
                        <label className="block text-xs font-bold text-blue-600 uppercase">CPF no Cupom (Opcional)</label>
                        <input
                            type="text"
                            value={cpf}
                            onChange={(e) => {
                                let v = e.target.value.replace(/\D/g, '')
                                if (v.length > 11) v = v.slice(0, 11)
                                setCpf(v)
                            }}
                            placeholder="000.000.000-00"
                            className="w-full p-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-200 outline-none bg-white font-mono"
                        />
                    </div>
                )}
            </div>
        </div>

        <div className="p-4 border-t border-gray-100 bg-gray-50">
            <button
                onClick={handleConfirm}
                disabled={loading || !depositoId}
                className={`
                    w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg flex items-center justify-center gap-2 transition-all
                    ${loading || !depositoId ? 'bg-gray-300 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 active:scale-95 shadow-green-200'}
                `}
            >
                {loading ? (
                    <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                    <>
                        <Check className="w-6 h-6" /> Confirmar Pagamento
                    </>
                )}
            </button>
        </div>
      </div>
    </div>
  )
}
