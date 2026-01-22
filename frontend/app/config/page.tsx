'use client'
import React from 'react'
import Link from 'next/link'
import { Settings, Printer, Bell, Shield, Database, Store, Monitor, UserCog, Users } from 'lucide-react'

export default function ConfigPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Configurações</h1>
          <p className="text-gray-500 mt-1">Gerencie as preferências globais do sistema</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Card: Caixas (PDV) */}
        <Link href="/config/caixas" className="card hover:shadow-md transition-all cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100 transition-colors">
              <Monitor className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Caixas (PDV)</h3>
              <p className="text-sm text-gray-500">Gerenciar terminais de caixa</p>
            </div>
          </div>
        </Link>

        {/* Card: Usuários */}
        <Link href="/config/usuarios" className="card hover:shadow-md transition-all cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-blue-50 text-blue-600 group-hover:bg-blue-100 transition-colors">
              <UserCog className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Usuários e Permissões</h3>
              <p className="text-sm text-gray-500">Logins, senhas e funções (Caixa/Garçom)</p>
            </div>
          </div>
        </Link>

        {/* Card: Dados da Empresa */}
        <div className="card hover:shadow-md transition-all cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-red-50 text-red-600 group-hover:bg-red-100 transition-colors">
              <Store className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Dados da Empresa</h3>
              <p className="text-sm text-gray-500">CNPJ, endereço e informações fiscais</p>
            </div>
          </div>
        </div>

        {/* Card: Impressão */}
        <div className="card hover:shadow-md transition-all cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-purple-50 text-purple-600 group-hover:bg-purple-100 transition-colors">
              <Printer className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Impressão e PDV</h3>
              <p className="text-sm text-gray-500">Configurar impressoras térmicas e recibos</p>
            </div>
          </div>
        </div>

        {/* Card: Segurança */}
        <div className="card hover:shadow-md transition-all cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-gray-50 text-gray-600 group-hover:bg-gray-100 transition-colors">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Segurança</h3>
              <p className="text-sm text-gray-500">Permissões de acesso e logs</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
