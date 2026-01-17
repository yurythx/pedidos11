'use client'
import React, { useEffect } from 'react'
import { useMesasStore } from '../mesasStore'
import type { Mesa, Paginacao } from '../../../types'
import { request } from '../../../lib/http/request'

export function MesasGrid({ onContaParcial }: { onContaParcial: (mesa: Mesa) => void }) {
  const { mesas, setMesas } = useMesasStore()

  useEffect(() => {
    request.get<Paginacao<Mesa>>('/mesas/').then((res) => setMesas(res.results))
  }, [setMesas])

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {mesas.map((m) => (
        <button
          key={m.id}
          onClick={() => onContaParcial(m)}
          className={`rounded p-4 border ${m.status === 'LIVRE' ? 'bg-green-50' : 'bg-red-50'}`}
        >
          <div className="font-semibold">Mesa {m.numero}</div>
          <div className="text-sm">{m.status === 'LIVRE' ? 'Livre' : 'Ocupada'}</div>
        </button>
      ))}
    </div>
  )
}

