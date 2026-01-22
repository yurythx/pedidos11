import React from 'react'
import { X, Printer, DollarSign, Receipt, CreditCard } from 'lucide-react'
import { formatBRL } from '../../../../utils/currency'
import { request } from '../../../../lib/http/request'
import { Mesa } from '../../../../types'

interface MesaDetailsModalProps {
  mesa: Mesa | null
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void // Called after closing/payment
}

interface ResumoConta {
  mesa: string
  venda_numero: number
  total_bruto: number
  total_desconto: number
  total_liquido: number
  itens: Array<{
    produto: string
    quantidade: number
    preco_unitario: number
    subtotal: number
    complementos: Array<{ nome: string; quantidade: number; preco: number }>
  }>
}

export function MesaDetailsModal({ mesa, isOpen, onClose, onSuccess }: MesaDetailsModalProps) {
  const [resumo, setResumo] = React.useState<ResumoConta | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [closing, setClosing] = React.useState(false)

  React.useEffect(() => {
    if (isOpen && mesa?.status === 'OCUPADA') {
      setLoading(true)
      request.get<ResumoConta>(`/mesas/${mesa.id}/conta/`)
        .then(setResumo)
        .catch(err => console.error('Erro ao carregar conta:', err))
        .finally(() => setLoading(false))
    }
  }, [isOpen, mesa])

  if (!isOpen || !mesa) return null

  const handleImprimir = () => {
    // TODO: Implementar endpoint de impressão real
    alert('Enviado para impressora')
  }

  const handleFecharConta = async () => {
    if (!confirm(`Deseja fechar a conta da Mesa ${mesa.numero}?`)) return

    setClosing(true)
    try {
      // TODO: Obter deposito_id padrão da configuração
      // Por enquanto, vou hardcodar ou pedir via prompt, mas o ideal é ter config
      // Vou simular um deposito_id qualquer por enquanto ou o backend pegar o padrao
      // Backend exige deposito_id. 
      // Workaround: Buscar depósitos e pegar o primeiro (LOJA)
      const depositos = await request.get<{ results: any[] }>('/depositos/')
      const depositoId = depositos.results[0]?.id

      if (!depositoId) throw new Error('Nenhum depósito configurado')

      await request.post(`/mesas/${mesa.id}/fechar/`, { deposito_id: depositoId })
      
      alert('Conta fechada')
      onSuccess()
      onClose()
    } catch (err: any) {
      alert('Erro ao fechar conta: ' + (err.message || 'Erro desconhecido'))
    } finally {
      setClosing(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center bg-gray-50 rounded-t-xl">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Mesa {mesa.numero}</h2>
            <span className={`text-xs font-bold px-2 py-0.5 rounded ${
              mesa.status === 'OCUPADA' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
            }`}>
              {mesa.status}
            </span>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex justify-center py-12">
              <span className="loading loading-spinner loading-lg text-primary"></span>
            </div>
          ) : !resumo ? (
            <div className="text-center py-12 text-gray-500">
              {mesa.status === 'LIVRE' ? 'Mesa livre. Nenhum consumo.' : 'Não foi possível carregar a conta.'}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Lista de Itens */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                  <Receipt className="w-4 h-4" />
                  Consumo
                </h3>
                <div className="divide-y border rounded-lg overflow-hidden">
                  {resumo.itens.map((item, idx) => (
                    <div key={idx} className="p-3 bg-white flex justify-between items-start hover:bg-gray-50">
                      <div>
                        <div className="font-medium text-gray-800">
                          {item.quantidade}x {item.produto}
                        </div>
                        {item.complementos.length > 0 && (
                          <ul className="text-xs text-gray-500 mt-1 pl-2 border-l-2 border-gray-200">
                            {item.complementos.map((comp, i) => (
                              <li key={i}>+ {comp.quantidade}x {comp.nome}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                      <div className="font-semibold text-gray-700">
                        {formatBRL(item.subtotal)}
                      </div>
                    </div>
                  ))}
                  {resumo.itens.length === 0 && (
                    <div className="p-4 text-center text-gray-500 text-sm">Nenhum item lançado</div>
                  )}
                </div>
              </div>

              {/* Totais */}
              <div className="bg-gray-50 p-4 rounded-xl space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Subtotal</span>
                  <span>{formatBRL(resumo.total_bruto)}</span>
                </div>
                {resumo.total_desconto > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Descontos</span>
                    <span>- {formatBRL(resumo.total_desconto)}</span>
                  </div>
                )}
                <div className="divider my-1"></div>
                <div className="flex justify-between text-xl font-bold text-gray-900">
                  <span>Total</span>
                  <span>{formatBRL(resumo.total_liquido)}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t bg-gray-50 rounded-b-xl flex gap-3 justify-end">
          {mesa.status === 'OCUPADA' && resumo && (
            <>
              <button 
                onClick={handleImprimir}
                className="btn btn-ghost gap-2 text-gray-600"
              >
                <Printer className="w-4 h-4" />
                Imprimir Parcial
              </button>
              
              <button 
                onClick={handleFecharConta}
                disabled={closing}
                className="btn btn-primary gap-2"
              >
                {closing ? <span className="loading loading-spinner loading-sm"></span> : <DollarSign className="w-4 h-4" />}
                Fechar Conta e Liberar Mesa
              </button>
            </>
          )}
          
          {mesa.status === 'SUJA' && (
             <button 
                onClick={async () => {
                    await request.post(`/mesas/${mesa.id}/liberar/`)
                    onSuccess()
                    onClose()
                }}
                className="btn btn-warning gap-2"
             >
                <Utensils className="w-4 h-4" />
                Liberar Mesa (Limpa)
             </button>
          )}
        </div>
      </div>
    </div>
  )
}
