'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useCartStore } from '../store/cartStore'
import { useCreateVenda, useAddItemVenda, useFinalizarVenda } from '../hooks/useSales'
import { FormaPagamento } from '../types'
import { finalizarVendaSchema, type FinalizarVendaFormData } from '../schemas/finalizarVenda'
import { formatBRL } from '@/utils/currency'
import {
    CreditCard,
    Banknote,
    Smartphone,
    Receipt,
    Loader2,
    CheckCircle2
} from 'lucide-react'

export function FinalizarVendaForm() {
    const router = useRouter()
    const { items, getSubtotal, getDescontoTotal, getTotal, clear } = useCartStore()
    const [vendaId, setVendaId] = useState<string | null>(null)
    const [isProcessing, setIsProcessing] = useState(false)

    const createVenda = useCreateVenda()
    const addItem = useAddItemVenda()
    const finalizar = useFinalizarVenda()

    const {
        register,
        handleSubmit,
        watch,
        formState: { errors },
    } = useForm<FinalizarVendaFormData>({
        resolver: zodResolver(finalizarVendaSchema),
        defaultValues: {
            forma_pagamento: FormaPagamento.DINHEIRO,
            parcelas: 1,
            valor_pago: getTotal(),
        },
    })

    const formaPagamento = watch('forma_pagamento')
    const valorPago = watch('valor_pago') || 0
    const total = getTotal()
    const troco = formaPagamento === FormaPagamento.DINHEIRO ? valorPago - total : 0

    const getFormaPagamentoIcon = (forma: FormaPagamento) => {
        const icons = {
            [FormaPagamento.DINHEIRO]: Banknote,
            [FormaPagamento.CREDITO]: CreditCard,
            [FormaPagamento.DEBITO]: CreditCard,
            [FormaPagamento.PIX]: Smartphone,
            [FormaPagamento.BOLETO]: Receipt,
        }
        return icons[forma]
    }

    const onSubmit = async (data: FinalizarVendaFormData) => {
        if (items.length === 0) {
            alert('Carrinho vazio')
            return
        }

        setIsProcessing(true)

        try {
            // 1. Criar venda
            let venda
            if (!vendaId) {
                venda = await createVenda.mutateAsync({})
                setVendaId(venda.id)
            } else {
                venda = { id: vendaId }
            }

            // 2. Adicionar itens
            for (const item of items) {
                await addItem.mutateAsync({
                    vendaId: venda.id,
                    data: {
                        produto_id: item.produto.id,
                        quantidade: item.quantidade,
                        preco_unitario: item.produto.preco_venda,
                        desconto: item.desconto,
                        observacao: item.observacao,
                    },
                })
            }

            // 3. Finalizar venda
            await finalizar.mutateAsync({
                vendaId: venda.id,
                data: {
                    forma_pagamento: data.forma_pagamento,
                    parcelas: data.parcelas,
                    valor_pago: data.valor_pago,
                },
            })

            // 4. Limpar carrinho e redirecionar
            clear()
            alert('Venda finalizada com sucesso!')
            router.push('/vendas')
        } catch (error) {
            console.error('Erro ao finalizar venda:', error)
            alert('Erro ao finalizar venda. Tente novamente.')
        } finally {
            setIsProcessing(false)
        }
    }

    if (items.length === 0) {
        return (
            <div className="max-w-2xl mx-auto text-center py-12">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <p className="text-yellow-800 mb-4">Carrinho vazio</p>
                    <button
                        onClick={() => router.push('/pdv')}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Voltar ao PDV
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-800">Finalizar Venda</h1>
                <p className="text-gray-500 text-sm">Selecione a forma de pagamento</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Formulário de Pagamento */}
                <div className="lg:col-span-2">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        {/* Formas de Pagamento */}
                        <div className="bg-white p-6 rounded-lg shadow-sm border">
                            <h3 className="font-semibold text-lg mb-4">Forma de Pagamento</h3>

                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {Object.values(FormaPagamento).map((forma) => {
                                    const Icon = getFormaPagamentoIcon(forma)
                                    const isSelected = formaPagamento === forma

                                    return (
                                        <button
                                            key={forma}
                                            type="button"
                                            onClick={() => register('forma_pagamento').onChange({ target: { value: forma } })}
                                            className={`p-4 border-2 rounded-lg transition-all ${isSelected
                                                    ? 'border-blue-500 bg-blue-50'
                                                    : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <Icon className={`w-8 h-8 mx-auto mb-2 ${isSelected ? 'text-blue-600' : 'text-gray-400'
                                                }`} />
                                            <span className="text-sm font-medium text-gray-800">
                                                {forma}
                                            </span>
                                        </button>
                                    )
                                })}
                            </div>
                            <input type="hidden" {...register('forma_pagamento')} />
                        </div>

                        {/* Parcelas (se crédito) */}
                        {formaPagamento === FormaPagamento.CREDITO && (
                            <div className="bg-white p-6 rounded-lg shadow-sm border">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Número de Parcelas
                                </label>
                                <select
                                    {...register('parcelas', { valueAsNumber: true })}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
                                        <option key={n} value={n}>
                                            {n}x de {formatBRL(total / n)}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* Valor Pago (se dinheiro) */}
                        {formaPagamento === FormaPagamento.DINHEIRO && (
                            <div className="bg-white p-6 rounded-lg shadow-sm border">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Valor Pago
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('valor_pago', { valueAsNumber: true })}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-lg"
                                    placeholder="0.00"
                                />
                                {errors.valor_pago && (
                                    <p className="text-red-500 text-sm mt-1">{errors.valor_pago.message}</p>
                                )}

                                {troco > 0 && (
                                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                                        <div className="flex justify-between items-center">
                                            <span className="text-green-700 font-medium">Troco</span>
                                            <span className="text-2xl font-bold text-green-700">
                                                {formatBRL(troco)}
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Ações */}
                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={() => router.back()}
                                className="flex-1 px-6 py-3 border-2 rounded-lg hover:bg-gray-50"
                                disabled={isProcessing}
                            >
                                Voltar
                            </button>
                            <button
                                type="submit"
                                disabled={isProcessing}
                                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {isProcessing ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Processando...
                                    </>
                                ) : (
                                    <>
                                        <CheckCircle2 className="w-5 h-5" />
                                        Confirmar Venda
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Resumo da Venda */}
                <div className="lg:col-span-1">
                    <div className="bg-white p-6 rounded-lg shadow-sm border sticky top-6">
                        <h3 className="font-semibold text-lg mb-4">Resumo da Venda</h3>

                        <div className="space-y-3 mb-4">
                            {items.map((item) => (
                                <div key={item.produto.id} className="flex justify-between text-sm">
                                    <span className="text-gray-600">
                                        {item.quantidade}x {item.produto.nome}
                                    </span>
                                    <span className="font-medium text-gray-800">
                                        {formatBRL(item.produto.preco_venda * item.quantidade - item.desconto)}
                                    </span>
                                </div>
                            ))}
                        </div>

                        <div className="border-t pt-4 space-y-2">
                            <div className="flex justify-between text-gray-600">
                                <span>Subtotal</span>
                                <span>{formatBRL(getSubtotal())}</span>
                            </div>
                            {getDescontoTotal() > 0 && (
                                <div className="flex justify-between text-green-600">
                                    <span>Desconto</span>
                                    <span>-{formatBRL(getDescontoTotal())}</span>
                                </div>
                            )}
                            <div className="flex justify-between text-2xl font-bold text-gray-800 pt-2 border-t">
                                <span>Total</span>
                                <span>{formatBRL(total)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
