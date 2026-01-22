'use client'
import React, { useEffect, useState, useMemo } from 'react'
import { useCartStore } from '../cartStore'
import { useComandasStore } from '../comandasStore'
import { useCaixaStore } from '@/features/financial/store/caixaStore'
import { useAuthStore } from '@/features/auth/store'
import { userService, User } from '@/features/users/services/userService'
import { formatBRL } from '../../../utils/currency'
import { request } from '../../../lib/http/request'
import { Trash2, Plus, Minus, Check, Utensils, Receipt, X } from 'lucide-react'
import { PaymentModal } from './modals/PaymentModal'
import { MessageModal } from './modals/MessageModal'

interface ResumoConta {
  comanda: string
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

export function CartPanelComanda() {
  const { items, increment, decrement, removeItem, clearItems, subtotal, snapshot, comandaId } = useCartStore()
  const { comandas } = useComandasStore()
  const { sessaoAberta } = useCaixaStore()
  const { user } = useAuthStore()
  const currentComanda = useMemo(() => comandas.find(c => c.id === comandaId), [comandas, comandaId])
  
  const total = useMemo(() => subtotal(), [items])
  const [loading, setLoading] = useState(false)
  const [contaComanda, setContaComanda] = useState<ResumoConta | null>(null)
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
  
  const handlePrintConferencia = () => {
    if (!contaComanda || !currentComanda) return

    const content = `
      <html>
        <head>
          <title>Conferência - Comanda ${currentComanda.codigo}</title>
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
          <div class="text-center bold" style="font-size: 14px">COMANDA ${currentComanda.codigo}</div>
          <div class="divider"></div>
          
          <div style="margin-bottom: 10px;">
          ${contaComanda.itens.map(item => `
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
            <span>${formatBRL(contaComanda.total_liquido)}</span>
          </div>
          
          <div class="text-center" style="margin-top: 30px; font-size: 10px;">
            *** NÃO É DOCUMENTO FISCAL ***
            <br/>Conferência de comanda
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
    if (canChooseAtendente) {
        userService.getAtendentes().then(data => {
            const list = Array.isArray(data) ? data : (data as any).results || []
            setAtendentes(list)
        }).catch(console.error)
    }
  }, [canChooseAtendente])

  const loadConta = async () => {
    if (comandaId && currentComanda?.status === 'EM_USO') {
        try {
            const res = await request.get<ResumoConta>(`/comandas/${comandaId}/conta/`)
            setContaComanda(res)
        } catch (e) {
            console.error(e)
            setContaComanda(null)
        }
    } else {
        setContaComanda(null)
    }
  }

  useEffect(() => {
    loadConta()
    const interval = setInterval(() => {
        if (comandaId && currentComanda?.status === 'EM_USO') {
            loadConta()
        }
    }, 5000)
    return () => clearInterval(interval)
  }, [comandaId, currentComanda?.status])

  const enviarPedido = async () => {
    if (!comandaId) return
    setLoading(true)
    try {
      if (currentComanda?.status === 'LIVRE') {
        await request.post(`/comandas/${comandaId}/abrir/`, { atendente_id: selectedAtendente })
      }

      const payload = snapshot()
      for (const item of payload) {
        await request.post(`/comandas/${comandaId}/adicionar_pedido/`, {
          produto_id: item.produto_id,
          quantidade: item.quantidade,
          observacoes: item.observacoes
        })
      }
      showMessage('Sucesso', 'Pedido enviado', 'success')
      clearItems()
      loadConta()
    } catch (e: any) {
      showMessage('Erro', 'Erro ao enviar pedido: ' + (e.response?.data?.error || e.message), 'error')
    } finally {
      setLoading(false)
    }
  }

  const cancelarItem = (itemId: string, nome: string, qtd: number) => {
    if (!comandaId) return
    showMessage('Cancelar Item', `Cancelar item?`, 'confirm', async () => {
        try {
            setLoading(true)
            await request.post(`/comandas/${comandaId}/remover_pedido/`, { item_id: itemId })
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
    if (!comandaId) return
    
    try {
      const res = await request.post<{ success: boolean; venda_id: string }>(`/comandas/${comandaId}/fechar/`, {
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
             // Não retornamos para limpar a tela, pois a comanda já foi fechada/liberada
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
          if (typeof data === 'string') errorMsg = data
          else if (data.error) errorMsg = Array.isArray(data.error) ? data.error.join('\n') : data.error
          else errorMsg = JSON.stringify(data)
      } else {
          errorMsg = e.message || 'Erro de conexão'
      }
      showMessage('Erro', `Erro ao fechar conta:\n${errorMsg}`, 'error')
    }
  }

  const fecharContaComanda = async () => {
    if (!comandaId) return
    if (!sessaoAberta) {
        showMessage('Caixa Fechado', 'É necessário abrir o caixa antes de realizar recebimentos.', 'error')
        return
    }
    setShowPaymentModal(true)
  }

  const liberarComanda = async () => {
    if (!comandaId) return
    showMessage('Liberar Comanda', 'Liberar comanda? (Isso cancelará o consumo atual se não houver pagamento)', 'confirm', async () => {
        setLoading(true)
        try {
            await request.post(`/comandas/${comandaId}/liberar/`)
            showMessage('Sucesso', 'Comanda liberada', 'success')
            clearItems()
            loadConta()
        } catch (e: any) {
            showMessage('Erro', 'Erro ao liberar comanda: ' + (e.response?.data?.error || e.message), 'error')
        } finally {
            setLoading(false)
        }
    })
  }

  useEffect(() => {
    if (items.length === 0 && contaComanda && contaComanda.itens.length > 0) {
        setShowHistory(true)
    } else if (items.length > 0) {
        setShowHistory(false)
    }
  }, [items.length, contaComanda])

  if (!currentComanda) return <div className="p-4 text-center text-gray-500">Nenhuma comanda selecionada</div>

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
        total={contaComanda?.total_liquido || 0}
        onConfirm={handlePaymentConfirm}
      />

      {/* Header */}
      <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-white shadow-sm z-10">
        <div className="flex items-center gap-2">
            <h2 className="font-bold text-gray-800 flex items-center gap-2">
              <Utensils className="w-5 h-5 text-primary" />
              {showHistory ? `Conta Comanda ${currentComanda.codigo}` : `Novo Pedido (${items.length})`}
            </h2>
        </div>
        
        <div className="flex gap-2">
            {contaComanda && contaComanda.itens.length > 0 && (
                <button
                    onClick={() => setShowHistory(!showHistory)}
                    className={`p-2 rounded-lg transition-colors flex items-center gap-1 text-xs font-bold ${
                        showHistory ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                {contaComanda?.itens.map((item, idx) => (
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
                        <span className="font-bold">{formatBRL(contaComanda?.total_liquido ?? 0)}</span>
                    </div>
                </div>
            </div>
        ) : (
            items.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
                    <Utensils className="w-16 h-16 mb-4 text-gray-300" />
                    <p className="text-center font-medium">Nenhum item novo</p>
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
                            disabled={i.quantity <= 1}
                        >
                            <Minus size={14} />
                        </button>
                        <span className="w-8 text-center font-bold text-gray-800">{i.quantity}</span>
                        <button 
                            className="w-8 h-8 flex items-center justify-center bg-white rounded-md shadow-sm text-gray-600 hover:text-primary active:scale-95 transition-all" 
                            onClick={() => increment(i.produto_id)}
                        >
                            <Plus size={14} />
                        </button>
                        </div>
                        <div className="font-bold text-gray-800">
                        {formatBRL(((i.produto?.preco_venda ?? 0) * i.quantity) || 0)}
                        </div>
                    </div>
                    
                    <div className="mt-2">
                        <input 
                            type="text"
                            placeholder="Observações..."
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

      {/* Footer */}
      <div className="p-4 border-t border-gray-50 bg-gray-50 space-y-4">
        {!showHistory && items.length > 0 && (
            <div className="flex justify-between items-end mb-4">
                <span className="text-gray-600 font-medium">Total do Pedido</span>
                <span className="text-2xl font-bold text-primary">{formatBRL(total || 0)}</span>
            </div>
        )}

        {!showHistory && items.length > 0 ? (
             <>
             {currentComanda?.status === 'LIVRE' && (
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
             {loading ? <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <><Check size={24} /> Enviar Pedido</>}
           </button>
           </>
        ) : (
            <div className="space-y-3">
                {currentComanda?.status === 'EM_USO' && (
                    <div className="flex gap-2">
                         {contaComanda && contaComanda.itens.length > 0 && (
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
                                  (contaComanda?.itens.length === 0 ? 'bg-amber-500 hover:bg-amber-600 shadow-amber-200' : 'bg-green-600 hover:bg-green-700 shadow-green-200')
                                } active:scale-95
                            `}
                            onClick={contaComanda?.itens.length === 0 ? liberarComanda : fecharContaComanda}
                            disabled={loading}
                        >
                                {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : 
                                    (contaComanda?.itens.length === 0 ? <><Utensils size={20} /> Liberar Comanda</> : <><Check size={20} /> Fechar Conta</>)
                                }
                        </button>
                    </div>
                )}
            </div>
        )}
      </div>
    </div>
  )
}
