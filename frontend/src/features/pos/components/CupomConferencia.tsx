import React from 'react'
import { formatBRL } from '@/utils/currency'

interface CupomProps {
  dados: {
    empresa: string
    mesa_ou_comanda: string
    itens: Array<{
      produto: string
      quantidade: number
      preco_unitario: number
      subtotal: number
    }>
    subtotal: number
    total: number
    data: string
  }
}

export const CupomConferencia = React.forwardRef<HTMLDivElement, CupomProps>(({ dados }, ref) => {
  return (
    <div ref={ref} className="p-2 font-mono text-xs w-[80mm] bg-white text-black hidden print:block print:w-full">
      <div className="text-center mb-2">
        <h1 className="font-bold text-sm uppercase">{dados.empresa}</h1>
        <p className="text-[10px]">CONFERÊNCIA DE CONTA</p>
        <p className="text-[10px]">{dados.data}</p>
      </div>
      
      <div className="border-b border-black border-dashed my-1"></div>
      
      <div className="mb-1 font-bold text-sm text-center uppercase">
        {dados.mesa_ou_comanda}
      </div>
      
      <div className="border-b border-black border-dashed my-1"></div>
      
      <div className="space-y-1">
        {dados.itens.map((item, idx) => (
            <div key={idx} className="flex justify-between items-start">
                <div className="flex flex-col w-full pr-2">
                    <span>{item.quantidade}x {item.produto}</span>
                    <span className="text-[10px] text-gray-600 ml-2">{formatBRL(item.preco_unitario)} un</span>
                </div>
                <span className="whitespace-nowrap font-bold">{formatBRL(item.subtotal)}</span>
            </div>
        ))}
      </div>
      
      <div className="border-b border-black border-dashed my-2"></div>
      
      <div className="flex justify-between font-bold text-sm mt-2">
        <span>TOTAL A PAGAR</span>
        <span>{formatBRL(dados.total)}</span>
      </div>
      
      <div className="mt-6 text-center text-[10px] font-bold">
        *** NÃO É DOCUMENTO FISCAL ***
      </div>
    </div>
  )
})

CupomConferencia.displayName = 'CupomConferencia'
