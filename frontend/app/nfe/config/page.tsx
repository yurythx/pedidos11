'use client'

import { CertificadoConfig } from '../../../src/features/nfe'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function NFeConfigPage() {
  return (
    <div className="container mx-auto py-8 max-w-2xl">
      <div className="mb-6">
        <Link href="/nfe" className="flex items-center text-gray-500 hover:text-blue-600 mb-2">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Voltar para NFe
        </Link>
        <h1 className="text-2xl font-bold text-gray-800">Configurações Fiscais</h1>
      </div>
      
      <CertificadoConfig />
    </div>
  )
}
