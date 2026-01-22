import React, { useState } from 'react'
import { X, Check, Loader2 } from 'lucide-react'
import { formatBRL } from '../../utils/currency'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (data: PaymentData) => Promise<void>
  valorOriginal: number
  tipo: 'PAGAR' | 'RECEBER'
}

export interface PaymentData {
  data_pagamento: string
  tipo_pagamento: string
  valor_juros: number
  valor_multa: number
  valor_desconto: number
}

export function PaymentModal({ isOpen, onClose, onConfirm, valorOriginal, tipo }: PaymentModalProps) {
  const [loading, setLoading] = useState(false)
  const [dataPagamento, setDataPagamento] = useState(new Date().toISOString().split('T')[0])
  const [tipoPagamento, setTipoPagamento] = useState('PIX')
  const [juros, setJuros] = useState('')
  const [multa, setMulta] = useState('')
  const [desconto, setDesconto] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onConfirm({
        data_pagamento: dataPagamento,
        tipo_pagamento: tipoPagamento,
        valor_juros: Number(juros) || 0,
        valor_multa: Number(multa) || 0,
        valor_desconto: Number(desconto) || 0
      })
      // Parent should close, but we can ensure here too if needed
    } catch (err) {
      // Error handling is done by parent usually, but we can stop loading
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const valorTotal = valorOriginal + (Number(juros) || 0) + (Number(multa) || 0) - (Number(desconto) || 0)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
          <h3 className="font-bold text-lg text-gray-900">
            {tipo === 'PAGAR' ? 'Baixar Conta a Pagar' : 'Baixar Conta a Receber'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="label">Data do Pagamento</label>
            <input 
              type="date" 
              className="input" 
              value={dataPagamento}
              onChange={e => setDataPagamento(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="label">Forma de Pagamento</label>
            <select 
              className="input"
              value={tipoPagamento}
              onChange={e => setTipoPagamento(e.target.value)}
            >
              <option value="DINHEIRO">Dinheiro</option>
              <option value="PIX">Pix</option>
              <option value="CARTAO_DEBITO">Cartão de Débito</option>
              <option value="CARTAO_CREDITO">Cartão de Crédito</option>
              <option value="BOLETO">Boleto</option>
              <option value="TRANSFERENCIA">Transferência</option>
              <option value="CHEQUE">Cheque</option>
            </select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="label text-xs">Juros (R$)</label>
              <input 
                type="number" 
                className="input text-sm" 
                value={juros}
                onChange={e => setJuros(e.target.value)}
                min="0"
                step="0.01"
                placeholder="0,00"
              />
            </div>
            <div>
              <label className="label text-xs">Multa (R$)</label>
              <input 
                type="number" 
                className="input text-sm" 
                value={multa}
                onChange={e => setMulta(e.target.value)}
                min="0"
                step="0.01"
                placeholder="0,00"
              />
            </div>
            <div>
              <label className="label text-xs">Desconto (R$)</label>
              <input 
                type="number" 
                className="input text-sm" 
                value={desconto}
                onChange={e => setDesconto(e.target.value)}
                min="0"
                step="0.01"
                placeholder="0,00"
              />
            </div>
          </div>

          <div className="pt-4 border-t mt-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-500">Valor Original</span>
              <span className="font-medium">{formatBRL(valorOriginal)}</span>
            </div>
            <div className="flex justify-between items-center text-lg font-bold text-gray-900">
              <span>Total a {tipo === 'PAGAR' ? 'Pagar' : 'Receber'}</span>
              <span>{formatBRL(valorTotal)}</span>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-ghost">Cancelar</button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Check className="w-4 h-4 mr-2" />}
              Confirmar Baixa
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
