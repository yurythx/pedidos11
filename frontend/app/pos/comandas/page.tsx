'use client'
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus } from 'lucide-react'
import { request } from '../../../src/lib/http/request'
import { ComandasGrid } from '../../../src/features/pos/components/ComandasGrid'
import type { Comanda } from '../../../src/types'
import { useCartStore } from '../../../src/features/pos/cartStore'

export default function ComandasPage() {
  const router = useRouter()
  const { setComandaId, clear } = useCartStore()
  const [loading, setLoading] = useState(false)
  const [showInputModal, setShowInputModal] = useState(false)

  const handleSelectComanda = (comanda: Comanda) => {
    if (comanda.status === 'LIVRE') {
        clear()
    }
    setComandaId(comanda.id)
    router.push('/pos/comandas/' + comanda.id)
  }

  const handleNovaComanda = () => setShowInputModal(true)

  const confirmNovaComanda = async (codigo: string) => {
    if (!codigo) return
    setLoading(true)
    try {
        const res = await request.post<Comanda>('/comandas/', {
            codigo: codigo,
            status: 'LIVRE'
        })
        if (res.id) {
            handleSelectComanda(res)
        } else {
            window.location.reload()
        }
    } catch (err: any) {
        if (err.response?.status === 400) {
            alert(`Comanda ${codigo} já existe ou erro de validação.`)
        } else {
            alert('Erro ao criar comanda: ' + (err.message || 'Erro desconhecido'))
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
                <h3 className="text-lg font-bold mb-4 text-gray-800">Nova Comanda</h3>
                <input 
                    autoFocus
                    type="text" 
                    placeholder="Código (ex: 100)"
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
          <h1 className="text-2xl font-bold text-gray-800">Gestão de Comandas</h1>
          <div className="flex gap-4">
              <button 
                onClick={handleNovaComanda}
                disabled={loading}
                className="btn btn-primary gap-2 shadow-lg shadow-primary/20"
              >
                <Plus className="w-4 h-4" />
                Nova Comanda
              </button>

              <div className="flex gap-2">
                  <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-full border border-gray-200 text-sm shadow-sm">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      <span>Livre</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-full border border-gray-200 text-sm shadow-sm">
                      <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
                      <span>Em Uso</span>
                  </div>
              </div>
          </div>
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <ComandasGrid onSelectComanda={handleSelectComanda} />
      </div>
    </div>
  )
}
