'use client'
import React, { useState, useEffect } from 'react'
import { request } from '@/lib/http/request'
import { formatBRL } from '@/utils/currency'
import { Calendar, User, Search, DollarSign } from 'lucide-react'

interface ComissaoRow {
  colaborador_id: string
  colaborador_nome: string | null
  colaborador_username: string
  total_vendas: number
  valor_vendas: number
  total_comissao: number
}

export default function ComissoesPage() {
  const [dataInicio, setDataInicio] = useState(new Date().toISOString().split('T')[0])
  const [dataFim, setDataFim] = useState(new Date().toISOString().split('T')[0])
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<ComissaoRow[]>([])

  const fetchComissoes = async () => {
    setLoading(true)
    try {
        const res = await request.get<ComissaoRow[]>(`/vendas/comissoes/?start_date=${dataInicio}&end_date=${dataFim}`)
        setData(res)
    } catch (e) {
        console.error(e)
        alert('Erro ao carregar comissões')
    } finally {
        setLoading(false)
    }
  }

  useEffect(() => {
    fetchComissoes()
  }, [])

  const totalGeralComissao = data.reduce((acc, curr) => acc + (curr.total_comissao || 0), 0)

  return (
    <div className="space-y-6 p-6">
        <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <DollarSign className="text-primary" /> Relatório de Comissões
            </h1>
        </div>

        {/* Filtros */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-end gap-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Início</label>
                <input 
                    type="date" 
                    value={dataInicio} 
                    onChange={e => setDataInicio(e.target.value)}
                    className="input"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Fim</label>
                <input 
                    type="date" 
                    value={dataFim} 
                    onChange={e => setDataFim(e.target.value)}
                    className="input"
                />
            </div>
            <button 
                onClick={fetchComissoes}
                disabled={loading}
                className="btn btn-primary flex items-center gap-2 h-[42px]"
            >
                <Search size={18} /> Filtrar
            </button>
        </div>

        {/* Resumo Cards */}
        <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <div className="text-sm text-blue-600 mb-1">Total Comissões</div>
                <div className="text-2xl font-bold text-blue-800">{formatBRL(totalGeralComissao)}</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-xl border border-purple-100">
                <div className="text-sm text-purple-600 mb-1">Atendentes Ativos</div>
                <div className="text-2xl font-bold text-purple-800">{data.length}</div>
            </div>
        </div>

        {/* Tabela */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <table className="w-full">
                <thead className="bg-gray-50">
                    <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        <th className="p-4">Colaborador</th>
                        <th className="p-4 text-center">Qtd Vendas</th>
                        <th className="p-4 text-right">Total Vendido</th>
                        <th className="p-4 text-right">Comissão a Pagar</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {loading ? (
                        <tr><td colSpan={4} className="p-8 text-center text-gray-500">Carregando...</td></tr>
                    ) : data.length === 0 ? (
                        <tr><td colSpan={4} className="p-8 text-center text-gray-500">Nenhuma comissão encontrada no período.</td></tr>
                    ) : (
                        data.map((row) => (
                            <tr key={row.colaborador_id} className="hover:bg-gray-50 transition-colors">
                                <td className="p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-500">
                                            <User size={16} />
                                        </div>
                                        <div>
                                            <div className="font-medium text-gray-900">{row.colaborador_nome || row.colaborador_username}</div>
                                            <div className="text-xs text-gray-500">@{row.colaborador_username}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="p-4 text-center text-gray-600">
                                    {row.total_vendas}
                                </td>
                                <td className="p-4 text-right text-gray-600">
                                    {formatBRL(row.valor_vendas)}
                                </td>
                                <td className="p-4 text-right">
                                    <span className="font-bold text-green-600 bg-green-50 px-2 py-1 rounded-lg border border-green-100">
                                        {formatBRL(row.total_comissao)}
                                    </span>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    </div>
  )
}
