'use client'
import React, { useEffect, useState } from 'react'
import { useCaixaStore } from '@/features/financial/store/caixaStore'
import { useAuthStore } from '@/features/auth/store'
import { AberturaCaixaModal } from '@/features/financial/components/AberturaCaixaModal'
import { Lock, Store, Clock } from 'lucide-react'

export default function PosLayout({ children }: { children: React.ReactNode }) {
  const { sessaoAberta, checkSessao, isLoading } = useCaixaStore()
  const { user } = useAuthStore()
  const [showModal, setShowModal] = useState(false)

  const canOpenCaixa = user?.role_caixa || ['ADMIN', 'GERENTE'].includes(user?.cargo || '')

  useEffect(() => {
    checkSessao()
  }, [])

  if (isLoading) {
    return (
        <div className="h-full flex items-center justify-center bg-gray-50">
            <div className="animate-pulse flex flex-col items-center">
                <div className="w-12 h-12 bg-gray-200 rounded-full mb-4"></div>
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
            </div>
        </div>
    )
  }

  if (!sessaoAberta) {
    return (
      <div className="h-full min-h-[80vh] flex flex-col items-center justify-center bg-gray-50 p-6 animate-in fade-in duration-500">
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 max-w-md w-full text-center">
            <div className="w-24 h-24 bg-red-50 text-primary rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
                <Lock size={48} />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">Caixa Fechado</h1>
            <p className="text-gray-500 mb-8 leading-relaxed">
                O acesso ao PDV está bloqueado. Para iniciar as vendas e acessar as mesas, é necessário ter uma sessão de caixa aberta.
            </p>
            
            {canOpenCaixa ? (
                <button 
                    onClick={() => setShowModal(true)}
                    className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-xl shadow-lg shadow-red-200 hover:shadow-xl transform hover:-translate-y-1 transition-all active:scale-95 flex items-center justify-center gap-3"
                >
                    <Store size={24} />
                    Abrir Caixa Agora
                </button>
            ) : (
                <div className="bg-amber-50 text-amber-800 p-6 rounded-2xl border border-amber-100 flex flex-col items-center animate-in zoom-in-95">
                    <Clock size={32} className="mb-2 text-amber-600" />
                    <h3 className="font-bold text-lg mb-1">Aguardando Abertura</h3>
                    <p className="text-sm opacity-80">Solicite a um Operador de Caixa ou Gerente para abrir a sessão.</p>
                </div>
            )}
            
            <div className="mt-6 text-xs text-gray-400">
                Necessário permissão de operador ou gerente
            </div>
        </div>
        {showModal && <AberturaCaixaModal onClose={() => setShowModal(false)} />}
      </div>
    )
  }

  return <>{children}</>
}
