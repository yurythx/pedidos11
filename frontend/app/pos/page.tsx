'use client'
import React from 'react'
import Link from 'next/link'
import { ShoppingBag, Utensils, Receipt, ArrowRight, CreditCard } from 'lucide-react'

export default function PosHomePage() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 gap-8 animate-in fade-in zoom-in-95 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Ponto de Venda</h1>
        <p className="text-gray-500 text-lg">Selecione o modo de operação para iniciar</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-7xl">
        {/* Card Balcão */}
        <Link href="/pos/balcao" className="group relative overflow-hidden bg-white border border-blue-100 rounded-3xl p-8 shadow-xl shadow-blue-50 hover:shadow-2xl hover:shadow-blue-100 hover:-translate-y-1 transition-all duration-300">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <ShoppingBag className="w-32 h-32 text-blue-600" />
          </div>
          
          <div className="relative z-10 flex flex-col h-full justify-between gap-6">
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center shadow-inner">
                <ShoppingBag className="w-8 h-8" />
            </div>
            
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">Venda Balcão</h2>
                <p className="text-gray-500 font-medium text-sm">Venda rápida direta no caixa, sem vínculo com mesas. Ideal para delivery e retirada.</p>
            </div>

            <div className="flex items-center text-blue-600 font-bold group-hover:gap-2 transition-all">
                Acessar Caixa <ArrowRight className="w-5 h-5 ml-2" />
            </div>
          </div>
        </Link>

        {/* Card Salão */}
        <Link href="/pos/salao" className="group relative overflow-hidden bg-white border border-orange-100 rounded-3xl p-8 shadow-xl shadow-orange-50 hover:shadow-2xl hover:shadow-orange-100 hover:-translate-y-1 transition-all duration-300">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <Utensils className="w-32 h-32 text-orange-600" />
          </div>
          
          <div className="relative z-10 flex flex-col h-full justify-between gap-6">
            <div className="w-16 h-16 bg-orange-100 text-orange-600 rounded-2xl flex items-center justify-center shadow-inner">
                <Utensils className="w-8 h-8" />
            </div>
            
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2 group-hover:text-orange-600 transition-colors">Mesas</h2>
                <p className="text-gray-500 font-medium text-sm">Controle visual de mesas, mapa de salão e pedidos por mesa.</p>
            </div>

            <div className="flex items-center text-orange-600 font-bold group-hover:gap-2 transition-all">
                Acessar Salão <ArrowRight className="w-5 h-5 ml-2" />
            </div>
          </div>
        </Link>

        {/* Card Comandas */}
        <Link href="/pos/comandas" className="group relative overflow-hidden bg-white border border-purple-100 rounded-3xl p-8 shadow-xl shadow-purple-50 hover:shadow-2xl hover:shadow-purple-100 hover:-translate-y-1 transition-all duration-300">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <CreditCard className="w-32 h-32 text-purple-600" />
          </div>
          
          <div className="relative z-10 flex flex-col h-full justify-between gap-6">
            <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-2xl flex items-center justify-center shadow-inner">
                <CreditCard className="w-8 h-8" />
            </div>
            
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2 group-hover:text-purple-600 transition-colors">Comandas</h2>
                <p className="text-gray-500 font-medium text-sm">Controle individual por cartão/ficha. Ideal para baladas e eventos.</p>
            </div>

            <div className="flex items-center text-purple-600 font-bold group-hover:gap-2 transition-all">
                Acessar Comandas <ArrowRight className="w-5 h-5 ml-2" />
            </div>
          </div>
        </Link>
      </div>

      <div className="mt-8 flex gap-4 text-sm text-gray-400">
        <div className="flex items-center gap-2">
            <Receipt className="w-4 h-4" /> Histórico de Vendas
        </div>
        <span>•</span>
        <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div> Sistema Online
        </div>
      </div>
    </div>
  )
}