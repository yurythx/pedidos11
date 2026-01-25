'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateMovimentacao } from '../hooks/useStock'
import { useDepositos } from '../hooks/useStock'
import { useProducts } from '@/features/catalog/hooks/useProducts'
import { TipoMovimentacao } from '../types'
import { Loader2, ArrowDownCircle, ArrowUpCircle, ArrowRightLeft, Settings } from 'lucide-react'
import { useRouter } from 'next/navigation'

const movimentacaoSchema = z.object({
    tipo: z.nativeEnum(TipoMovimentacao),
    produto_id: z.string().min(1, 'Selecione um produto'),
    deposito_origem_id: z.string().optional(),
    deposito_destino_id: z.string().optional(),
    quantidade: z.number().min(0.01, 'Quantidade deve ser maior que zero'),
    valor_unitario: z.number().min(0).optional(),
    documento: z.string().optional(),
    observacao: z.string().optional(),
}).refine(
    (data) => {
        // Validação: Entrada precisa de destino
        if (data.tipo === TipoMovimentacao.ENTRADA && !data.deposito_destino_id) {
            return false
        }
        // Validação: Saída precisa de origem
        if (data.tipo === TipoMovimentacao.SAIDA && !data.deposito_origem_id) {
            return false
        }
        // Validação: Transferência precisa de ambos
        if (data.tipo === TipoMovimentacao.TRANSFERENCIA) {
            return data.deposito_origem_id && data.deposito_destino_id &&
                data.deposito_origem_id !== data.deposito_destino_id
        }
        return true
    },
    {
        message: 'Depósitos inválidos para o tipo de movimentação',
        path: ['deposito_destino_id'],
    }
)

type MovimentacaoFormData = z.infer<typeof movimentacaoSchema>

export function MovimentacaoForm() {
    const router = useRouter()
    const createMutation = useCreateMovimentacao()
    const { data: depositos } = useDepositos()
    const { data: produtosData } = useProducts({ page_size: 1000 })

    const {
        register,
        handleSubmit,
        watch,
        formState: { errors },
        setValue,
    } = useForm<MovimentacaoFormData>({
        resolver: zodResolver(movimentacaoSchema),
        defaultValues: {
            tipo: TipoMovimentacao.ENTRADA,
            quantidade: 1,
        },
    })

    const tipo = watch('tipo')
    const quantidade = watch('quantidade')
    const valorUnitario = watch('valor_unitario')

    const onSubmit = async (data: MovimentacaoFormData) => {
        try {
            await createMutation.mutateAsync(data)
            alert('Movimentação registrada com sucesso!')
            router.push('/movimentacoes')
        } catch (error) {
            alert('Erro ao registrar movimentação')
        }
    }

    const getTipoConfig = (tipo: TipoMovimentacao) => {
        const configs = {
            [TipoMovimentacao.ENTRADA]: {
                label: 'Entrada de Mercadoria',
                icon: ArrowDownCircle,
                color: 'text-green-600 bg-green-50',
                needsOrigem: false,
                needsDestino: true,
            },
            [TipoMovimentacao.SAIDA]: {
                label: 'Saída de Mercadoria',
                icon: ArrowUpCircle,
                color: 'text-red-600 bg-red-50',
                needsOrigem: true,
                needsDestino: false,
            },
            [TipoMovimentacao.TRANSFERENCIA]: {
                label: 'Transferência entre Depósitos',
                icon: ArrowRightLeft,
                color: 'text-blue-600 bg-blue-50',
                needsOrigem: true,
                needsDestino: true,
            },
            [TipoMovimentacao.AJUSTE]: {
                label: 'Ajuste de Inventário',
                icon: Settings,
                color: 'text-yellow-600 bg-yellow-50',
                needsOrigem: false,
                needsDestino: true,
            },
            [TipoMovimentacao.INVENTARIO]: {
                label: 'Inventário',
                icon: Settings,
                color: 'text-purple-600 bg-purple-50',
                needsOrigem: false,
                needsDestino: true,
            },
        }
        return configs[tipo]
    }

    const config = getTipoConfig(tipo)
    const Icon = config.icon

    const valorTotal = quantidade && valorUnitario ? quantidade * valorUnitario : null

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Nova Movimentação</h1>
                <p className="text-gray-500 text-sm">Registre entradas, saídas e transferências de estoque</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Tipo de Movimentação */}
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h3 className="font-semibold text-lg mb-4">Tipo de Movimentação</h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {Object.values(TipoMovimentacao).map((tipoOption) => {
                            const optionConfig = getTipoConfig(tipoOption)
                            const OptionIcon = optionConfig.icon
                            const isSelected = tipo === tipoOption

                            return (
                                <button
                                    key={tipoOption}
                                    type="button"
                                    onClick={() => setValue('tipo', tipoOption)}
                                    className={`p-4 border-2 rounded-lg transition-all ${isSelected
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${optionConfig.color}`}>
                                            <OptionIcon className="w-5 h-5" />
                                        </div>
                                        <span className="font-medium text-sm text-gray-800">
                                            {optionConfig.label}
                                        </span>
                                    </div>
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Produto e Depósitos */}
                <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                        <Icon className="w-5 h-5" />
                        {config.label}
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Produto */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Produto *
                            </label>
                            <select
                                {...register('produto_id')}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Selecione um produto</option>
                                {produtosData?.results.map((produto) => (
                                    <option key={produto.id} value={produto.id}>
                                        {produto.nome} ({produto.unidade_medida})
                                    </option>
                                ))}
                            </select>
                            {errors.produto_id && (
                                <p className="text-red-500 text-sm mt-1">{errors.produto_id.message}</p>
                            )}
                        </div>

                        {/* Depósito Origem */}
                        {config.needsOrigem && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Depósito Origem *
                                </label>
                                <select
                                    {...register('deposito_origem_id')}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Selecione o depósito</option>
                                    {depositos?.map((dep) => (
                                        <option key={dep.id} value={dep.id}>
                                            {dep.nome}
                                        </option>
                                    ))}
                                </select>
                                {errors.deposito_origem_id && (
                                    <p className="text-red-500 text-sm mt-1">{errors.deposito_origem_id.message}</p>
                                )}
                            </div>
                        )}

                        {/* Depósito Destino */}
                        {config.needsDestino && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Depósito Destino *
                                </label>
                                <select
                                    {...register('deposito_destino_id')}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Selecione o depósito</option>
                                    {depositos?.map((dep) => (
                                        <option key={dep.id} value={dep.id}>
                                            {dep.nome}
                                        </option>
                                    ))}
                                </select>
                                {errors.deposito_destino_id && (
                                    <p className="text-red-500 text-sm mt-1">{errors.deposito_destino_id.message}</p>
                                )}
                            </div>
                        )}

                        {/* Quantidade */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Quantidade *
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('quantidade', { valueAsNumber: true })}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="0.00"
                            />
                            {errors.quantidade && (
                                <p className="text-red-500 text-sm mt-1">{errors.quantidade.message}</p>
                            )}
                        </div>

                        {/* Valor Unitário */}
                        {tipo === TipoMovimentacao.ENTRADA && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Valor Unitário
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('valor_unitario', { valueAsNumber: true })}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="0.00"
                                />
                            </div>
                        )}

                        {/* Valor Total */}
                        {valorTotal !== null && (
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Valor Total
                                </label>
                                <div className="px-4 py-2 bg-green-50 border border-green-200 rounded-lg font-semibold text-green-700">
                                    R$ {valorTotal.toFixed(2)}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Informações Adicionais */}
                <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
                    <h3 className="font-semibold text-lg">Informações Adicionais</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Documento (NFe, Pedido, etc.)
                            </label>
                            <input
                                {...register('documento')}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Ex: NFe 12345"
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Observação
                            </label>
                            <textarea
                                {...register('observacao')}
                                rows={3}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Observações sobre esta movimentação..."
                            />
                        </div>
                    </div>
                </div>

                {/* Ações */}
                <div className="flex justify-end gap-3">
                    <button
                        type="button"
                        onClick={() => router.back()}
                        className="px-6 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={createMutation.isPending}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                        Registrar Movimentação
                    </button>
                </div>
            </form>
        </div>
    )
}
