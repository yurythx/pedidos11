'use client'
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus } from 'lucide-react'
import { request } from '../../../src/lib/http/request'
import { MesasGrid } from '../../../src/features/pos/components/MesasGrid'
import type { Mesa } from '../../../src/types'
import { useCartStore } from '../../../src/features/pos/cartStore'

export default function SalaoPage() {
  const router = useRouter()
  const { setMesaId, clear } = useCartStore()
  const [loading, setLoading] = useState(false)
  const [showInputModal, setShowInputModal] = useState(false)

  const handleSelectMesa = (mesa: Mesa) => {
    // Agora vai para a rota dedicada da mesa
    // Mas antes, limpa o carrinho para garantir estado limpo
    clear()
    setMesaId(mesa.id)
    router.push(`/pos/salao/${mesa.id}`)
  }

  const handleNovaComanda = () => setShowInputModal(true)

  const confirmNovaComanda = async (numero: string) => {
    if (!numero) return

    setLoading(true)
    try {
        const res = await request.post<Mesa>('/mesas/', {
            numero: parseInt(numero),
            capacidade: 4,
            status: 'LIVRE'
        })
        
        if (res.id) {
            handleSelectMesa(res)
        } else {
            window.location.reload()
        }

    } catch (err: any) {
        if (err.response?.status === 400 || err.message?.includes('existe')) {
            alert(`A Mesa ${numero} já existe!`)
        } else {
            alert('Erro ao criar mesa: ' + (err.message || 'Erro desconhecido'))
        }
    } finally {
        setLoading(false)
        setShowInputModal(false)
    }
  }

  return (
    <div className="p-4 h-full flex flex-col relative">
      {showInputModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center animate-in fade-in duration-200">
            <div className="bg-white p-6 rounded-xl shadow-xl w-80">
                <h3 className="text-lg font-bold mb-4 text-gray-800">Nova Mesa / Comanda</h3>
                <input 
                    autoFocus
                    type="number" 
                    placeholder="Número"
                    className="w-full border rounded-lg p-3 text-lg mb-4 focus:ring-2 focus:ring-primary/20 outline-none"
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') confirmNovaComanda(e.currentTarget.value)
                    }}
                />
                <div className="flex justify-end gap-2">
                    <button 
                        onClick={() => setShowInputModal(false)}
                        className="btn btn-ghost btn-sm"
                    >
                        Cancelar
                    </button>
                    <button 
                        className="btn btn-primary btn-sm"
                        onClick={(e) => {
                            const input = e.currentTarget.parentElement?.previousElementSibling as HTMLInputElement
                            confirmNovaComanda(input.value)
                        }}
                    >
                        Criar
                    </button>
                </div>
            </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Gestão de Mesas</h1>
          <div className="flex gap-4">
              <button 
                onClick={handleNovaComanda}
                disabled={loading}
                className="btn btn-primary gap-2 shadow-lg shadow-primary/20"
              >
                <Plus className="w-4 h-4" />
                Nova Mesa/Comanda
              </button>

              <div className="flex gap-2">
                  <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-full border border-gray-200 text-sm shadow-sm">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      <span>Livre</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-full border border-gray-200 text-sm shadow-sm">
                      <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                      <span>Ocupada</span>
                  </div>
              </div>
          </div>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Usamos o MesasGrid, mas precisamos adaptá-lo para remover a parte de Balcão que agora tem página própria */}
        {/* Por enquanto, vamos renderizar o MesasGrid e depois podemos refatorá-lo para ser puro */}
        <MesasGrid onSelectMesa={handleSelectMesa} />
      </div>
    </div>
  )
}