'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { request } from '../../../src/lib/http/request'
import { useAuthStore } from '../../../src/features/auth/store'
import type { Cliente } from '../../../src/types'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import Link from 'next/link'

export default function NovaVendaPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [clienteId, setClienteId] = useState<string>('')
  const [tipoPagamento, setTipoPagamento] = useState<string>('DINHEIRO')
  const [observacoes, setObservacoes] = useState<string>('')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadClientes = async () => {
      try {
        const res = await request.get<any>('/clientes/?page_size=100')
        const list: Cliente[] = res?.results ?? res ?? []
        setClientes(list)
      } catch {
        setClientes([])
      }
    }
    loadClientes()
  }, [])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const payload: any = {
        vendedor: user?.id,
        tipo_pagamento: tipoPagamento,
        observacoes,
      }
      if (clienteId) payload.cliente = clienteId

      const res = await request.post<any>('/vendas/', payload)
      // Redireciona para a tela de detalhes para adicionar itens
      router.push(`/vendas/${res.id}`)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao criar venda')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/vendas" className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6 text-gray-500" />
        </Link>
        <div>
          <h1 className="heading-1">Nova Venda</h1>
          <p className="text-gray-500">Inicie uma nova venda preenchendo os dados básicos</p>
        </div>
      </div>

      <div className="card">
        <form onSubmit={onSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 text-red-600 rounded-xl text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="label">Cliente</label>
            <select
              className="input"
              value={clienteId}
              onChange={(e) => setClienteId(e.target.value)}
            >
              <option value="">Selecione (Opcional - Balcão)</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome} ({c.cpf_cnpj || 'S/ Doc'})</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Se não selecionar, será considerado venda Balcão.</p>
          </div>

          <div>
            <label className="label">Tipo de Pagamento Preferencial</label>
            <select
              className="input"
              value={tipoPagamento}
              onChange={(e) => setTipoPagamento(e.target.value)}
            >
              <option value="DINHEIRO">Dinheiro</option>
              <option value="CARTAO">Cartão</option>
              <option value="PIX">Pix</option>
              <option value="BOLETO">Boleto</option>
            </select>
          </div>

          <div>
            <label className="label">Observações</label>
            <textarea
              className="input min-h-[100px]"
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Ex: Entregar na portaria..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Link href="/vendas" className="btn btn-ghost">
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary min-w-[150px]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Criando...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  Criar e Adicionar Itens
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
