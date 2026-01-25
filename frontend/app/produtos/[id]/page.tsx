'use client'

import { useParams, useRouter } from 'next/navigation'
import { useProduct, useUpdateProduct } from '@/features/catalog/hooks/useProducts'
import { useCategories } from '@/features/catalog/hooks/useCategories'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { TipoProduto, UnidadeMedida } from '@/features/catalog/types'
import { Loader2 } from 'lucide-react'

const produtoSchema = z.object({
  nome: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  descricao: z.string().optional(),
  tipo: z.nativeEnum(TipoProduto),
  categoria_id: z.string().min(1, 'Selecione uma categoria'),
  preco_custo: z.number().min(0).optional(),
  preco_venda: z.number().min(0.01, 'Preço de venda deve ser maior que zero'),
  unidade_medida: z.nativeEnum(UnidadeMedida),
  codigo_barras: z.string().optional(),
  sku: z.string().optional(),
  ativo: z.boolean().default(true),
  estoque_minimo: z.number().min(0).optional(),
  estoque_maximo: z.number().min(0).optional(),
})

type ProdutoFormData = z.infer<typeof produtoSchema>

export default function EditarProdutoPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const { data: produto, isLoading: loadingProduto } = useProduct(id)
  const { data: categorias } = useCategories()
  const updateMutation = useUpdateProduct()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ProdutoFormData>({
    resolver: zodResolver(produtoSchema),
    values: produto ? {
      nome: produto.nome,
      descricao: produto.descricao || '',
      tipo: produto.tipo,
      categoria_id: produto.categoria.id,
      preco_custo: produto.preco_custo,
      preco_venda: produto.preco_venda,
      unidade_medida: produto.unidade_medida,
      codigo_barras: produto.codigo_barras || '',
      sku: produto.sku || '',
      ativo: produto.ativo,
      estoque_minimo: produto.estoque_minimo,
      estoque_maximo: produto.estoque_maximo,
    } : undefined,
  })

  const onSubmit = async (data: ProdutoFormData) => {
    try {
      await updateMutation.mutateAsync({ id, data })
      router.push('/produtos')
    } catch (error) {
      alert('Erro ao atualizar produto')
    }
  }

  const tipo = watch('tipo')
  const precoCusto = watch('preco_custo')
  const precoVenda = watch('preco_venda')

  const margem = precoCusto && precoVenda
    ? ((precoVenda - precoCusto) / precoCusto * 100).toFixed(1)
    : null

  if (loadingProduto) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  if (!produto) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          Produto não encontrado
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Editar Produto</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <h3 className="font-semibold text-lg">Informações Básicas</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nome do Produto *
              </label>
              <input
                {...register('nome')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Coca-Cola 350ml"
              />
              {errors.nome && (
                <p className="text-red-500 text-sm mt-1">{errors.nome.message}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descrição
              </label>
              <textarea
                {...register('descricao')}
                rows={3}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Descrição detalhada do produto..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo *
              </label>
              <select
                {...register('tipo')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={TipoProduto.SIMPLES}>Produto Simples</option>
                <option value={TipoProduto.COMPOSTO}>Produto Composto</option>
                <option value={TipoProduto.MATERIA_PRIMA}>Matéria Prima</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoria *
              </label>
              <select
                {...register('categoria_id')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Selecione uma categoria</option>
                {categorias?.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.nome}
                  </option>
                ))}
              </select>
              {errors.categoria_id && (
                <p className="text-red-500 text-sm mt-1">{errors.categoria_id.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unidade de Medida *
              </label>
              <select
                {...register('unidade_medida')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={UnidadeMedida.UN}>Unidade (UN)</option>
                <option value={UnidadeMedida.KG}>Quilograma (KG)</option>
                <option value={UnidadeMedida.L}>Litro (L)</option>
                <option value={UnidadeMedida.CX}>Caixa (CX)</option>
              </select>
            </div>

            <div className="flex items-center gap-4">
              <input
                type="checkbox"
                {...register('ativo')}
                id="ativo"
                className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <label htmlFor="ativo" className="text-sm font-medium text-gray-700">
                Produto ativo
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <h3 className="font-semibold text-lg">Precificação</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {tipo !== TipoProduto.COMPOSTO && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preço de Custo
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register('preco_custo', { valueAsNumber: true })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Preço de Venda *
              </label>
              <input
                type="number"
                step="0.01"
                {...register('preco_venda', { valueAsNumber: true })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
              {errors.preco_venda && (
                <p className="text-red-500 text-sm mt-1">{errors.preco_venda.message}</p>
              )}
            </div>

            {margem !== null && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Margem de Lucro
                </label>
                <div className={`px-4 py-2 border rounded-lg bg-gray-50 font-semibold ${Number(margem) >= 30 ? 'text-green-600' :
                    Number(margem) >= 15 ? 'text-yellow-600' :
                      'text-red-600'
                  }`}>
                  {margem}%
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <h3 className="font-semibold text-lg">Códigos e Estoque</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Código de Barras
              </label>
              <input
                {...register('codigo_barras')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: 7891234567890"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SKU
              </label>
              <input
                {...register('sku')}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: PROD-001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estoque Mínimo
              </label>
              <input
                type="number"
                {...register('estoque_minimo', { valueAsNumber: true })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estoque Máximo
              </label>
              <input
                type="number"
                {...register('estoque_maximo', { valueAsNumber: true })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>
          </div>
        </div>

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
            disabled={updateMutation.isPending}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {updateMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Atualizar Produto
          </button>
        </div>
      </form>
    </div>
  )
}
