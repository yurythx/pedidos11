'use client'
import React, { useEffect, useState, useMemo } from 'react'
import { useCartStore } from '../cartStore'
import { useMesasStore } from '../mesasStore'
import { useCaixaStore } from '@/features/financial/store/caixaStore'
import { useAuthStore } from '@/features/auth/store'
import { userService, User } from '@/features/users/services/userService'
import { formatBRL } from '../../../utils/currency'
import { request } from '../../../lib/http/request'
import type { VendaSnapshotItem } from '../../../types'
import { Trash2, Plus, Minus, Check, Utensils, Receipt, X } from 'lucide-react'
import { PaymentModal } from './modals/PaymentModal'
import { MessageModal } from './modals/MessageModal'

interface ResumoConta {
  mesa: string
  venda_numero: number
  total_bruto: number
  total_desconto: number
  total_liquido: number
  itens: Array<{
    id: string
    produto: string
    quantidade: number
    preco_unitario: number
    subtotal: number
    complementos: Array<{ nome: string; quantidade: number; preco: number }>
  }>
}

export function CartPanelMesa() {
  const { items, increment, decrement, removeItem, clearItems, subtotal, snapshot, mesaId } = useCartStore()
  const { mesas } = useMesasStore()
  const { sessaoAberta } = useCaixaStore()
  const { user } = useAuthStore()
  const currentMesa = useMemo(() => mesas.find(m => m.id === mesaId), [mesas, mesaId])
  
  const total = useMemo(() => subtotal(), [items])
  const [loading, setLoading] = useState(false)
  const [contaMesa, setContaMesa] = useState<ResumoConta | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [atendentes, setAtendentes] = useState<User[]>([])
  const [selectedAtendente, setSelectedAtendente] = useState<string>('')
  
  const canChooseAtendente = user?.role_caixa || ['ADMIN', 'GERENTE'].includes(user?.cargo || '')
  
  const [messageModal, setMessageModal] = useState<{
    isOpen: boolean
    title: string
    message: string
    type: 'success' | 'error' | 'confirm' | 'info'
    onConfirm?: () => void
  }>({ isOpen: false, title: '', message: '', type: 'info' })

  const showMessage = (title: string, message: string, type: 'success' | 'error' | 'confirm' | 'info' = 'info', onConfirm?: () => void) => {
    setMessageModal({ isOpen: true, title, message, type, onConfirm })
  }

  const closeMessage = () => setMessageModal(prev => ({ ...prev, isOpen: false }))
  
  // Para fechamento de conta
  // const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([]) // Movido para o Modal
  // const [depositoId, setDepositoId] = useState<string>('') // Movido para o Modal

  const handlePrintConferencia = () => {
    if (!contaMesa || !currentMesa) return

    const content = `
      <html>
        <head>
          <title>Conferência - Mesa ${currentMesa.numero}</title>
          <style>
            body { font-family: 'Courier New', monospace; font-size: 12px; width: 300px; margin: 0 auto; padding: 10px; color: #000; }
            .text-center { text-align: center; }
            .text-right { text-align: right; }
            .bold { font-weight: bold; }
            .flex { display: flex; justify-content: space-between; align-items: flex-start; }
            .divider { border-bottom: 1px dashed #000; margin: 8px 0; }
            .mb-1 { margin-bottom: 4px; }
            .mt-2 { margin-top: 8px; }
            .item-name { width: 65%; word-wrap: break-word; }
            @media print { 
                @page { margin: 0; }
                body { padding: 5px; width: 100%; }
            }
          </style>
        </head>
        <body>
          <div class="text-center mb-1">
            <div class="bold" style="font-size: 16px; margin-bottom: 4px;">NIX RESTAURANTE</div>
            <div>CONFERÊNCIA DE CONTA</div>
            <div>${new Date().toLocaleString()}</div>
          </div>
          
          <div class="divider"></div>
          <div class="text-center bold" style="font-size: 14px">MESA ${currentMesa.numero}</div>
          <div class="divider"></div>
          
          <div style="margin-bottom: 10px;">
          ${contaMesa.itens.map(item => `
            <div class="flex mb-1">
              <span class="item-name">${item.quantidade}x ${item.produto}</span>
              <span class="text-right" style="flex: 1">${formatBRL(item.subtotal)}</span>
            </div>
            ${item.complementos.map(comp => `
                <div class="flex" style="color: #444; font-size: 10px; padding-left: 10px;">
                    <span>+ ${comp.quantidade}x ${comp.nome}</span>
                </div>
            `).join('')}
          `).join('')}
          </div>
          
          <div class="divider"></div>
          
          <div class="flex bold" style="font-size: 14px; margin-top: 5px;">
            <span>TOTAL A PAGAR</span>
            <span>${formatBRL(contaMesa.total_liquido)}</span>
          </div>
          
          <div class="text-center" style="margin-top: 30px; font-size: 10px;">
            *** NÃO É DOCUMENTO FISCAL ***
            <br/>Conferência de mesa
          </div>
          
          <script>
            window.onload = function() { window.print(); window.setTimeout(function(){ window.close() }, 500); }
          </script>
        </body>
      </html>
    `
    
    const popup = window.open('', '_blank', 'width=350,height=600')
    if (popup) {
        popup.document.open()
        popup.document.write(content)
        popup.document.close()
    }
  }

  useEffect(() => {
    // Carrega atendentes apenas se tiver permissão de escolha (Caixa/Gerente)
    if (canChooseAtendente) {
        userService.getAtendentes().then(data => {
            const list = Array.isArray(data) ? data : (data as any).results || []
            setAtendentes(list)
        }).catch(console.error)
    }
  }, [canChooseAtendente])

  // Carregar conta da mesa
  const loadConta = async () => {
    if (mesaId && currentMesa?.status === 'OCUPADA') {
        try {
            const res = await request.get<ResumoConta>(`/mesas/${mesaId}/conta/`)
            setContaMesa(res)
        } catch (e) {
            console.error(e)
            setContaMesa(null)
        }
    } else {
        setContaMesa(null)
    }
  }

  useEffect(() => {
    loadConta()
    
    // Polling inteligente: atualiza a conta a cada 5 segundos se a mesa estiver ocupada
    // Isso garante que pedidos feitos por outros garçons apareçam
    const interval = setInterval(() => {
        if (mesaId && currentMesa?.status === 'OCUPADA') {
            loadConta()
        }
    }, 5000)

    return () => clearInterval(interval)
  }, [mesaId, currentMesa?.status])

  const enviarPedido = async () => {
    if (!mesaId) return
    setLoading(true)
    try {
      if (currentMesa?.status === 'LIVRE') {
        await request.post(`/mesas/${mesaId}/abrir/`, { atendente_id: selectedAtendente })
      }

      const payload = snapshot()
      for (const item of payload) {
        await request.post(`/mesas/${mesaId}/adicionar_pedido/`, {
          produto_id: item.produto_id,
          quantidade: item.quantidade,
          observacoes: item.observacoes // Envia observação para o backend
        })
      }
      showMessage('Sucesso', 'Pedido enviado', 'success')
      clearItems()
      loadConta() // Atualiza histórico
    } catch (e: any) {
      showMessage('Erro', 'Erro ao enviar pedido: ' + (e.response?.data?.error || e.message), 'error')
    } finally {
      setLoading(false)
    }
  }

  const cancelarItem = (itemId: string, nome: string, qtd: number) => {
    if (!mesaId) return
    showMessage('Cancelar Item', `Cancelar item?`, 'confirm', async () => {
        try {
            setLoading(true)
            await request.post(`/mesas/${mesaId}/remover_pedido/`, { item_id: itemId })
            await loadConta()
            showMessage('Sucesso', 'Item cancelado', 'success')
        } catch (e: any) {
            showMessage('Erro', 'Erro ao cancelar item: ' + (e.response?.data?.error || e.message), 'error')
        } finally {
            setLoading(false)
        }
    })
  }

  const handlePaymentConfirm = async (paymentData: { 
    tipo_pagamento: string; 
    deposito_id: string; 
    valor_pago: number;
    colaborador_id?: string;
    cpf?: string;
    emitir_nfe?: boolean;
  }) => {
    if (!currentMesa) return
    
    try {
      const res = await request.post<{ success: boolean; venda_id: string }>(`/mesas/${currentMesa.id}/fechar/`, {
        deposito_id: paymentData.deposito_id,
        tipo_pagamento: paymentData.tipo_pagamento,
        valor_pago: paymentData.valor_pago,
        colaborador_id: paymentData.colaborador_id,
        cpf_cliente: paymentData.cpf
      })
      
      let msg = 'Conta fechada com sucesso'
      
      if (paymentData.emitir_nfe && res.venda_id) {
           try {
             await request.post(`/nfe/emissao/gerar-de-venda/`, {
                 venda_id: res.venda_id,
                 modelo: '65',
                 serie: '1'
             })
             msg += ' e NFC-e gerada.'
          } catch (e: any) {
             console.error('Erro NFe:', e)
             showMessage('Atenção', `Conta fechada, mas erro na NFC-e: ${e.response?.data?.error || e.message}`, 'error')
          }
      }
      
      showMessage('Sucesso', msg, 'success')
      clearItems()
      loadConta()
      setShowPaymentModal(false)
    } catch (e: any) {
      console.error('Erro ao fechar conta (RAW):', e.response?.data)
      const data = e.response?.data
      let errorMsg = ''
      
      if (data) {
          if (typeof data === 'string') {
              errorMsg = data
          } else if (data.error) {
              errorMsg = Array.isArray(data.error) ? data.error.join('\n') : data.error
          } else if (data.detail) {
              errorMsg = data.detail
          } else {
              // Objeto de erros de validação (ex: { campo: ['erro'] })
              try {
                  errorMsg = Object.entries(data)
                    .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
                    .join('\n')
              } catch {
                  errorMsg = JSON.stringify(data)
              }
          }
      } else {
          errorMsg = e.message || 'Erro de conexão'
      }

      showMessage('Erro', `Erro ao fechar conta:\n${errorMsg}`, 'error')
    }
  }

  const fecharContaMesa = async () => {
    if (!mesaId) return
    
    if (!sessaoAberta) {
        showMessage('Caixa Fechado', 'É necessário abrir o caixa antes de realizar recebimentos.', 'error')
        return
    }
    
    // Apenas abre o modal
    setShowPaymentModal(true)
  }

  const liberarMesa = async () => {
    if (!mesaId) return
    showMessage('Liberar Mesa', 'Liberar mesa?', 'confirm', async () => {
        setLoading(true)
        try {
            await request.post(`/mesas/${mesaId}/liberar/`)
            showMessage('Sucesso', 'Mesa liberada', 'success')
            clearItems()
            loadConta()
        } catch (e: any) {
            showMessage('Erro', 'Erro ao liberar mesa: ' + (e.response?.data?.error || e.message), 'error')
        } finally {
            setLoading(false)
        }
    })
  }

  // Se não tiver itens e tiver histórico, mostra histórico por padrão
  useEffect(() => {
    if (items.length === 0 && contaMesa && contaMesa.itens.length > 0) {
        setShowHistory(true)
    } else if (items.length > 0) {
        setShowHistory(false)
    }
  }, [items.length, contaMesa])

  if (!currentMesa) return <div className="p-4 text-center text-gray-500">Nenhuma mesa selecionada</div>

  return (
    <div className="h-full flex flex-col bg-white md:rounded-2xl md:shadow-sm md:border border-gray-100 overflow-hidden relative">
      <MessageModal 
        isOpen={messageModal.isOpen}
        title={messageModal.title}
        message={messageModal.message}
        type={messageModal.type}
        onClose={closeMessage}
        onConfirm={messageModal.onConfirm}
      />

      <PaymentModal 
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        total={contaMesa?.total_liquido || 0}
        onConfirm={handlePaymentConfirm}
      />

      {/* Header Mesa */}
      <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-white shadow-sm z-10">
        <div className="flex items-center gap-2">
            <h2 className="font-bold text-gray-800 flex items-center gap-2">
              <Utensils className="w-5 h-5 text-primary" />
              {showHistory ? `Conta Mesa ${currentMesa.numero}` : `Novo Pedido (${items.length})`}
            </h2>
        </div>
        
        <div className="flex gap-2">
            {contaMesa && contaMesa.itens.length > 0 && (
                <button
                    onClick={() => setShowHistory(!showHistory)}
                    className={`p-2 rounded-lg transition-colors flex items-center gap-1 text-xs font-bold ${
                        showHistory 
                        ? 'bg-primary text-white' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                >
                    <Receipt className="w-4 h-4" />
                    {showHistory ? 'Voltar' : 'Ver Conta'}
                </button>
            )}

            {!showHistory && items.length > 0 && (
              <button 
                onClick={clearItems} 
                className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-1"
              >
                <Trash2 size={14} />
              </button>
            )}
        </div>
      </div>

      {/* Lista */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {showHistory ? (
            // HISTÓRICO
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                {contaMesa?.itens.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-red-50 transition-colors group">
                        <div className="flex-1">
                            <div className="font-medium text-gray-800">
                                <span className="font-bold text-primary mr-2">{item.quantidade}x</span> 
                                {item.produto}
                            </div>
                            {item.complementos.length > 0 && (
                                <ul className="text-xs text-gray-500 mt-1 pl-4 list-disc">
                                    {item.complementos.map((c, i) => (
                                        <li key={i}>{c.quantidade}x {c.nome}</li>
                                    ))}
                                </ul>
                            )}
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="font-bold text-gray-700">{formatBRL(item.subtotal)}</div>
                            <button 
                                onClick={() => cancelarItem(item.id, item.produto, item.quantidade)}
                                className="p-1 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Cancelar Item"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
                
                <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 mt-4">
                    <div className="flex justify-between text-sm text-blue-800 mb-1">
                        <span>Total Consumido</span>
                        <span className="font-bold">{formatBRL(contaMesa?.total_liquido ?? 0)}</span>
                    </div>
                </div>
            </div>
        ) : (
            // NOVO PEDIDO
            items.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
                    <Utensils className="w-16 h-16 mb-4 text-gray-300" />
                    <p className="text-center font-medium">Nenhum item novo</p>
                    <p className="text-sm text-center px-8">Adicione itens para enviar à cozinha</p>
                </div>
            ) : (
                items.map((i) => (
                    <div key={i.produto_id} className="flex flex-col gap-2 p-3 rounded-xl border border-gray-100 hover:border-red-100 bg-white transition-colors shadow-sm animate-in fade-in zoom-in-95 duration-200">
                    <div className="flex justify-between items-start">
                        <div>
                        <div className="font-semibold text-gray-800 line-clamp-2">{i.produto?.nome}</div>
                        <div className="text-sm text-primary font-bold mt-1">
                            {formatBRL(i.produto?.preco_venda ?? 0)}
                        </div>
                        </div>
                        <button 
                  className="text-gray-400 hover:text-red-500 p-2 rounded-full hover:bg-red-50 transition-colors z-20 relative" 
                  onClick={(e) => {
                    e.stopPropagation()
                    removeItem(i.produto_id)
                  }}
                >
                  <Trash2 size={18} />
                </button>
                    </div>
                    
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-50">
                        <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-1">
                        <button 
                            className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all disabled:opacity-50" 
                            onClick={() => decrement(i.produto_id)}
                            disabled={i.quantidade <= 1}
                        >
                            <Minus size={14} />
                        </button>
                        <span className="w-8 text-center font-bold text-gray-800">{i.quantidade}</span>
                        <button 
                            className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all" 
                            onClick={() => increment(i.produto_id)}
                        >
                            <Plus size={14} />
                        </button>
                        </div>
                        <div className="font-bold text-gray-800">
                        {formatBRL(((i.produto?.preco_venda ?? 0) * i.quantidade) || 0)}
                        </div>
                    </div>
                    
                    <div className="mt-2">
                        <input 
                            type="text"
                            placeholder="Observações (ex: sem cebola)..."
                            className="w-full text-xs p-2 bg-gray-50 rounded-lg border border-transparent focus:border-primary/20 focus:bg-white focus:ring-2 focus:ring-primary/10 outline-none transition-all placeholder:text-gray-400"
                            value={i.observacoes || ''}
                            onChange={(e) => {
                                const val = e.target.value
                                const { updateObservation } = useCartStore.getState()
                                updateObservation(i.produto_id, val)
                            }}
                        />
                    </div>
                    </div>
                ))
            )
        )}
      </div>

      {/* Footer Mesa */}
      <div className="p-4 border-t border-gray-50 bg-gray-50 space-y-4">
        {!showHistory && items.length > 0 && (
            <div className="flex justify-between items-end mb-4">
                <span className="text-gray-600 font-medium">Total do Pedido</span>
                <span className="text-2xl font-bold text-primary">{formatBRL(total || 0)}</span>
            </div>
        )}

        {/* Botão Principal */}
        {!showHistory && items.length > 0 ? (
             <>
             {currentMesa?.status === 'LIVRE' && (
                 <div className="mb-4 bg-white p-3 rounded-xl border border-gray-200 shadow-sm">
                     <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Garçom / Atendente</label>
                     
                     {canChooseAtendente ? (
                         <select
                            className="w-full p-2.5 border border-gray-200 rounded-lg bg-gray-50 text-gray-800 outline-none focus:border-primary focus:ring-1 focus:ring-primary appearance-none"
                            value={selectedAtendente}
                            onChange={e => setSelectedAtendente(e.target.value)}
                         >
                             <option value="">Eu mesmo ({user?.first_name || 'Login'})</option>
                             {atendentes.map(a => (
                                 <option key={a.id} value={a.id}>{a.first_name || a.username}</option>
                             ))}
                         </select>
                     ) : (
                         <div className="w-full p-2.5 border border-gray-100 rounded-lg bg-gray-50 text-gray-600 font-medium text-sm flex items-center gap-2">
                             <div className="w-2 h-2 rounded-full bg-green-500"></div>
                             {user?.first_name || user?.username} (Você)
                         </div>
                     )}
                 </div>
             )}

             <button
             className="w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg shadow-red-200 flex items-center justify-center gap-2 transition-all bg-primary hover:bg-primary-dark active:scale-95"
             onClick={enviarPedido}
             disabled={loading}
           >
             {loading ? (
               <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
             ) : (
               <>
                 <Check size={24} /> Enviar Pedido
               </>
             )}
           </button>
           </>
        ) : (
            // Se não tem itens novos, mostra opções de fechamento se estiver ocupada/suja
            <div className="space-y-3">
                {currentMesa?.status === 'OCUPADA' && (
                    <div className="flex gap-2">
                        {contaMesa && contaMesa.itens.length > 0 && (
                            <button
                                onClick={handlePrintConferencia}
                                className="w-14 rounded-xl bg-gray-200 text-gray-700 hover:bg-gray-300 font-bold flex items-center justify-center shadow-sm active:scale-95 transition-all"
                                title="Imprimir Conferência"
                            >
                                <Receipt size={24} />
                            </button>
                        )}
                        <button
                            className={`flex-1 py-3.5 rounded-xl font-bold text-white shadow-lg flex items-center justify-center gap-2 transition-all
                                ${loading ? 'bg-gray-300 cursor-not-allowed' : 
                                  (contaMesa?.itens.length === 0 ? 'bg-amber-500 hover:bg-amber-600 shadow-amber-200' : 'bg-green-600 hover:bg-green-700 shadow-green-200')
                                } active:scale-95
                            `}
                            onClick={contaMesa?.itens.length === 0 ? liberarMesa : fecharContaMesa}
                            disabled={loading}
                        >
                                {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : 
                                    (contaMesa?.itens.length === 0 ? <><Utensils size={20} /> Liberar Mesa</> : <><Check size={20} /> Fechar Conta</>)
                                }
                        </button>
                    </div>
                )}

                {currentMesa?.status === 'SUJA' && (
                    <button
                        className="w-full py-3.5 rounded-xl font-bold text-white shadow-lg bg-amber-500 hover:bg-amber-600 active:scale-95 flex items-center justify-center gap-2 transition-all"
                        onClick={liberarMesa}
                        disabled={loading}
                    >
                         {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <><Utensils size={20} /> Liberar Mesa</>}
                    </button>
                )}
            </div>
        )}
      </div>
    </div>
  )
}