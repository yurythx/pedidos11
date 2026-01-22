'use client'
import React from 'react'
import { ProductGrid } from '../../../../src/features/pos/components/ProductGrid'
import { CartPanelComanda } from '../../../../src/features/pos/components/CartPanelComanda'

export default function ComandaDetailsPage() {
  return (
    <div className="flex h-full gap-4 p-4">
      {/* Esquerda: Grid de Produtos */}
      <div className="flex-1 overflow-hidden bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col">
        <div className="p-4 border-b border-gray-50">
           <h2 className="font-bold text-gray-800">Catálogo de Produtos</h2>
        </div>
        <div className="flex-1 overflow-hidden">
            <ProductGrid />
        </div>
      </div>
      
      {/* Direita: Painel da Comanda */}
      <div className="w-[400px] flex-shrink-0 h-full">
        <CartPanelComanda />
      </div>
    </div>
  )
}
