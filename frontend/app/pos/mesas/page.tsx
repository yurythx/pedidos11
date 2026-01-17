'use client'
import React, { useState } from 'react'
import { MesasGrid } from '../../../src/features/pos/components/MesasGrid'
import type { Mesa } from '../../../src/types'

export default function MesasPage() {
  const [selecionada, setSelecionada] = useState<Mesa | null>(null)
  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-3">Gestão de Mesas</h1>
      <MesasGrid onContaParcial={setSelecionada} />
      {selecionada && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded p-4 w-full max-w-md">
            <div className="font-semibold mb-2">Conta Parcial - Mesa {selecionada.numero}</div>
            <p className="text-sm mb-4">Selecione itens para fechar parcialmente.</p>
            <div className="flex justify-end gap-2">
              <button className="border rounded px-3 py-2" onClick={() => setSelecionada(null)}>
                Cancelar
              </button>
              <button className="bg-black text-white rounded px-3 py-2">Confirmar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

