'use client'

import React from 'react'
import Link from 'next/link'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="max-w-md w-full text-center">
                <div className="mb-8">
                    <h1 className="text-9xl font-black text-blue-100 relative">
                        404
                        <span className="absolute inset-0 flex items-center justify-center text-3xl text-blue-600 font-bold">
                            Mesa não encontrada
                        </span>
                    </h1>
                </div>

                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    Ops! Esta página não está no cardápio.
                </h2>
                <p className="text-gray-500 mb-10">
                    O link que você seguiu pode estar quebrado ou a página pode ter sido removida do sistema.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        href="/"
                        className="flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-200"
                    >
                        <Home size={20} />
                        Início
                    </Link>
                    <button
                        onClick={() => window.history.back()}
                        className="flex items-center justify-center gap-2 bg-white text-gray-700 border border-gray-200 px-6 py-3 rounded-xl font-bold hover:bg-gray-50 transition-all"
                    >
                        <ArrowLeft size={20} />
                        Voltar
                    </button>
                </div>
            </div>
        </div>
    )
}
