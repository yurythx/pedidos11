'use client'

import { useDashboardFinanceiro } from '../hooks/useFinance'
import { formatBRL } from '@/utils/currency'
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    AlertCircle,
    CheckCircle2,
    XCircle,
    Calendar
} from 'lucide-react'

export function DashboardFinanceiro() {
    const { data: dashboard, isLoading } = useDashboardFinanceiro()

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        )
    }

    if (!dashboard) {
        return (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800">Dados do dashboard não disponíveis</p>
            </div>
        )
    }

    const saldoPositivo = dashboard.saldo_mes >= 0

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-800">Dashboard Financeiro</h1>
                <p className="text-gray-500 text-sm">Visão geral das finanças</p>
            </div>

            {/* Saldo do Mês */}
            <div className={`p-6 rounded-lg border-2 ${saldoPositivo ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                }`}>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-gray-600 mb-1">Saldo do Mês</p>
                        <p className={`text-4xl font-bold ${saldoPositivo ? 'text-green-600' : 'text-red-600'
                            }`}>
                            {formatBRL(dashboard.saldo_mes)}
                        </p>
                    </div>
                    <div className={`p-4 rounded-full ${saldoPositivo ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                        {saldoPositivo ? (
                            <TrendingUp className="w-12 h-12 text-green-600" />
                        ) : (
                            <TrendingDown className="w-12 h-12 text-red-600" />
                        )}
                    </div>
                </div>
            </div>

            {/* Contas a Receber */}
            <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Contas a Receber</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-blue-100 rounded-lg">
                                <DollarSign className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Total a Receber</p>
                                <p className="text-xl font-bold text-gray-800">
                                    {formatBRL(dashboard.total_a_receber)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-green-100 rounded-lg">
                                <CheckCircle2 className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Recebido Hoje</p>
                                <p className="text-xl font-bold text-green-600">
                                    {formatBRL(dashboard.recebido_hoje)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-purple-100 rounded-lg">
                                <Calendar className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Recebido no Mês</p>
                                <p className="text-xl font-bold text-purple-600">
                                    {formatBRL(dashboard.recebido_mes)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-red-100 rounded-lg">
                                <XCircle className="w-6 h-6 text-red-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Vencidas</p>
                                <p className="text-xl font-bold text-red-600">
                                    {formatBRL(dashboard.vencidas_receber)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Contas a Pagar */}
            <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Contas a Pagar</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-orange-100 rounded-lg">
                                <DollarSign className="w-6 h-6 text-orange-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Total a Pagar</p>
                                <p className="text-xl font-bold text-gray-800">
                                    {formatBRL(dashboard.total_a_pagar)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-green-100 rounded-lg">
                                <CheckCircle2 className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Pago Hoje</p>
                                <p className="text-xl font-bold text-green-600">
                                    {formatBRL(dashboard.pago_hoje)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-purple-100 rounded-lg">
                                <Calendar className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Pago no Mês</p>
                                <p className="text-xl font-bold text-purple-600">
                                    {formatBRL(dashboard.pago_mes)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-red-100 rounded-lg">
                                <XCircle className="w-6 h-6 text-red-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Vencidas</p>
                                <p className="text-xl font-bold text-red-600">
                                    {formatBRL(dashboard.vencidas_pagar)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Alertas */}
            {(dashboard.vencidas_receber > 0 || dashboard.vencidas_pagar > 0) && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                    <div className="flex items-start">
                        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
                        <div>
                            <h3 className="font-semibold text-yellow-800">Atenção: Contas Vencidas</h3>
                            <p className="text-sm text-yellow-700 mt-1">
                                Você possui contas vencidas. Verifique e regularize a situação.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
