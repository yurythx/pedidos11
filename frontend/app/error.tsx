'use client'

import React, { useEffect } from 'react'
import { AlertTriangle, RefreshCcw } from 'lucide-react'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        // Aqui você integraria com o Sentry no futuro
        console.error('Erro detectado pela UI:', error)
    }, [error])

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="max-w-md w-full text-center">
                <div className="inline-flex p-4 bg-red-100 rounded-2xl text-red-600 mb-6">
                    <AlertTriangle size={48} />
                </div>

                <h1 className="text-3xl font-bold text-gray-900 mb-3">
                    Algo deu errado
                </h1>
                <p className="text-gray-500 mb-8">
                    O sistema encontrou uma instabilidade inesperada. Nossos técnicos foram notificados (se o Sentry estivesse ativo).
                </p>

                <div className="bg-white border border-red-100 p-4 rounded-xl mb-8 text-left">
                    <p className="text-xs font-mono text-red-500 overflow-auto max-h-32">
                        {error.message || 'Erro interno do sistema'}
                    </p>
                </div>

                <button
                    onClick={() => reset()}
                    className="w-full flex items-center justify-center gap-2 bg-gray-900 text-white px-6 py-4 rounded-xl font-bold hover:bg-black transition-all shadow-xl"
                >
                    <RefreshCcw size={20} />
                    Tentar novamente
                </button>
            </div>
        </div>
    )
}
