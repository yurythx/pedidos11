# 🎨 Componentes Completos - CRUD Produtos

**Complemento ao:** SPRINT_2_FRONTEND_CORE.md  
**Semana:** 5

---

## 📦 Componentes Faltantes

### ProductFilters.tsx

**Criar:** `frontend/src/features/catalog/components/ProductFilters.tsx`

```typescript
'use client'

import React from 'react'
import { ProductFilters as Filters, TipoProduto } from '../types'
import { useCategories } from '../hooks/useCategories'
import { Search, Filter } from 'lucide-react'

interface Props {
  filters: Filters
  onChange: (filters: Filters) => void
}

export function ProductFilters({ filters, onChange }: Props) {
  const { data: categorias } = useCategories()

  const handleChange = (key: keyof Filters, value: any) => {
    onChange({ ...filters, [key]: value, page: 1 }) // Reset página ao filtrar
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
      <div className="flex items-center gap-2 text-gray-700 font-medium">
        <Filter className="w-5 h-5" />
        Filtros
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Busca */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar produto..."
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Categoria */}
        <select
          value={filters.categoria_id || ''}
          onChange={(e) => handleChange('categoria_id', e.target.value || undefined)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todas as categorias</option>
          {categorias?.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nome}
            </option>
          ))}
        </select>

        {/* Tipo */}
        <select
          value={filters.tipo || ''}
          onChange={(e) => handleChange('tipo', e.target.value as TipoProduto || undefined)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos os tipos</option>
          <option value={TipoProduto.SIMPLES}>Simples</option>
          <option value={TipoProduto.COMPOSTO}>Composto</option>
          <option value={TipoProduto.MATERIA_PRIMA}>Matéria Prima</option>
        </select>

        {/* Preço Mínimo */}
        <input
          type="number"
          placeholder="Preço mín"
          value={filters.preco_min || ''}
          onChange={(e) => handleChange('preco_min', e.target.value ? Number(e.target.value) : undefined)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />

        {/* Preço Máximo */}
        <input
          type="number"
          placeholder="Preço máx"
          value={filters.preco_max || ''}
          onChange={(e) => handleChange('preco_max', e.target.value ? Number(e.target.value) : undefined)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />

        {/* Ativo */}
        <select
          value={filters.ativo === undefined ? '' : filters.ativo.toString()}
          onChange={(e) => handleChange('ativo', e.target.value === '' ? undefined : e.target.value === 'true')}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos status</option>
          <option value="true">Ativos</option>
          <option value="false">Inativos</option>
        </select>

        {/* Ordenação */}
        <select
          value={filters.ordering || ''}
          onChange={(e) => handleChange('ordering', e.target.value || undefined)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Ordenar por...</option>
          <option value="nome">Nome (A-Z)</option>
          <option value="-nome">Nome (Z-A)</option>
          <option value="preco_venda">Preço (Menor)</option>
          <option value="-preco_venda">Preço (Maior)</option>
          <option value="-created_at">Mais recentes</option>
        </select>

        {/* Limpar filtros */}
        <button
          onClick={() => onChange({ page: 1, page_size: 20 })}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Limpar
        </button>
      </div>
    </div>
  )
}
```

---

### ProductCard.tsx

**Criar:** `frontend/src/features/catalog/components/ProductCard.tsx`

```typescript
'use client'

import React from 'react'
import { Produto, TipoProduto } from '../types'
import { formatBRL } from '@/utils/currency'
import { Edit, Trash2, Package, FileText } from 'lucide-react'
import Image from 'next/image'

interface Props {
  produto: Produto
  onEdit: () => void
  onDelete: () => void
}

export function ProductCard({ produto, onEdit, onDelete }: Props) {
  const getTipoBadge = (tipo: TipoProduto) => {
    const colors = {
      [TipoProduto.SIMPLES]: 'bg-blue-100 text-blue-700',
      [TipoProduto.COMPOSTO]: 'bg-purple-100 text-purple-700',
      [TipoProduto.MATERIA_PRIMA]: 'bg-green-100 text-green-700',
    }
    
    const labels = {
      [TipoProduto.SIMPLES]: 'Simples',
      [TipoProduto.COMPOSTO]: 'Composto',
      [TipoProduto.MATERIA_PRIMA]: 'Matéria Prima',
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[tipo]}`}>
        {labels[tipo]}
      </span>
    )
  }

  return (
    <div className="bg-white border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
      {/* Imagem */}
      <div className="relative h-48 bg-gray-100">
        {produto.foto ? (
          <Image
            src={produto.foto}
            alt={produto.nome}
            fill
            className="object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Package className="w-16 h-16 text-gray-300" />
          </div>
        )}
        
        {/* Badge Status */}
        {!produto.ativo && (
          <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-medium">
            Inativo
          </div>
        )}
      </div>

      {/* Conteúdo */}
      <div className="p-4 space-y-3">
        {/* Nome e Tipo */}
        <div>
          <h3 className="font-semibold text-gray-800 text-lg truncate" title={produto.nome}>
            {produto.nome}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            {getTipoBadge(produto.tipo)}
            <span className="text-xs text-gray-500">{produto.categoria.nome}</span>
          </div>
        </div>

        {/* Descricão */}
        {produto.descricao && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {produto.descricao}
          </p>
        )}

        {/* Preços */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="text-xs text-gray-500">Preço Venda</p>
            <p className="font-bold text-green-600">
              {formatBRL(produto.preco_venda)}
            </p>
          </div>
          {produto.preco_custo && (
            <div>
              <p className="text-xs text-gray-500">Custo</p>
              <p className="font-medium text-gray-700">
                {formatBRL(produto.preco_custo)}
              </p>
            </div>
          )}
        </div>

        {/* Margem */}
        {produto.margem_lucro !== null && produto.margem_lucro !== undefined && (
          <div className="pt-2 border-t">
            <p className="text-xs text-gray-500">Margem de Lucro</p>
            <p className={`font-semibold ${
              produto.margem_lucro >= 30 ? 'text-green-600' : 
              produto.margem_lucro >= 15 ? 'text-yellow-600' : 
              'text-red-600'
            }`}>
              {produto.margem_lucro.toFixed(1)}%
            </p>
          </div>
        )}

        {/* Ações */}
        <div className="flex gap-2 pt-3 border-t">
          <button
            onClick={onEdit}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Edit className="w-4 h-4" />
            Editar
          </button>
          
          {produto.tipo === TipoProduto.COMPOSTO && (
            <button
              onClick={() => window.location.href = `/produtos/${produto.id}/ficha-tecnica`}
              className="px-3 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors"
              title="Ficha Técnica"
            >
              <FileText className="w-4 h-4" />
            </button>
          )}
          
          <button
            onClick={onDelete}
            className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
            title="Excluir"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

### ProductForm.tsx

**Criar:** `frontend/src/features/catalog/components/ProductForm.tsx`

```typescript
'use client'

import React, { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCategories } from '../hooks/useCategories'
import { TipoProduto, UnidadeMedida, Produto } from '../types'
import { Loader2 } from 'lucide-react'

const produtoSchema = z.object({
  nome: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  descricao: z.string().optional(),
  tipo: z.nativeEnum(TipoProduto),
  categoria_id: z.string().min(1, 'Selecione uma categoria'),
  preco_custo: z.number().min(0, 'Preço de custo deve ser positivo').optional(),
  preco_venda: z.number().min(0.01, 'Preço de venda deve ser maior que zero'),
  unidade_medida: z.nativeEnum(UnidadeMedida),
  codigo_barras: z.string().optional(),
  sku: z.string().optional(),
  ativo: z.boolean().default(true),
  estoque_minimo: z.number().min(0).optional(),
  estoque_maximo: z.number().min(0).optional(),
})

type ProdutoFormData = z.infer<typeof produtoSchema>

interface Props {
  produto?: Produto
  onSubmit: (data: ProdutoFormData) => Promise<void>
  isLoading?: boolean
}

export function ProductForm({ produto, onSubmit, isLoading }: Props) {
  const { data: categorias } = useCategories()
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProdutoFormData>({
    resolver: zodResolver(produtoSchema),
    defaultValues: produto ? {
      nome: produto.nome,
      descricao: produto.descricao,
      tipo: produto.tipo,
      categoria_id: produto.categoria.id,
      preco_custo: produto.preco_custo,
      preco_venda: produto.preco_venda,
      unidade_medida: produto.unidade_medida,
      codigo_barras: produto.codigo_barras,
      sku: produto.sku,
      ativo: produto.ativo,
      estoque_minimo: produto.estoque_minimo,
      estoque_maximo: produto.estoque_maximo,
    } : {
      tipo: TipoProduto.SIMPLES,
      unidade_medida: UnidadeMedida.UN,
      ativo: true,
    },
  })

  const tipo = watch('tipo')
  const precoCusto = watch('preco_custo')
  const precoVenda = watch('preco_venda')

  // Calcular margem automaticamente
  const margem = precoCusto && precoVenda 
    ? ((precoVenda - precoCusto) / precoCusto * 100).toFixed(1)
    : null

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
        {/* Informações Básicas */}
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
            {errors.tipo && (
              <p className="text-red-500 text-sm mt-1">{errors.tipo.message}</p>
            )}
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

      {/* Preços */}
      <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
        <h3 className="font-semibold text-lg text-gray-800">Precificação</h3>
        
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
              {errors.preco_custo && (
                <p className="text-red-500 text-sm mt-1">{errors.preco_custo.message}</p>
              )}
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
              <div className={`px-4 py-2 border rounded-lg bg-gray-50 font-semibold ${
                Number(margem) >= 30 ? 'text-green-600' : 
                Number(margem) >= 15 ? 'text-yellow-600' : 
                'text-red-600'
              }`}>
                {margem}%
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Códigos e Estoque */}
      <div className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
        <h3 className="font-semibold text-lg text-gray-800">Códigos e Estoque</h3>
        
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

      {/* Ações */}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-6 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
          {produto ? 'Atualizar' : 'Criar'} Produto
        </button>
      </div>
    </form>
  )
}
```

---

**Próximo arquivo:** Páginas do Next.js para integrar esses componentes!
