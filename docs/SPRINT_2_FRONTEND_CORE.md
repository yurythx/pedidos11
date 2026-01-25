# 🚀 Sprint 2 - Frontend Core (Implementação Detalhada)

**Duração:** 4 semanas (Semanas 5-8)  
**Objetivo:** Frontend 30% → 60%  
**Meta:** Funcionalidades essenciais operacionais

---

## 📋 Checklist Geral

- [ ] **Semana 5:** CRUD Produtos Completo
- [ ] **Semana 6:** Gestão de Estoque (Movimentações + Lotes)
- [ ] **Semana 7:** PDV Básico
- [ ] **Semana 8:** Financeiro (Contas a Pagar/Receber)

---

## 🗓️ SEMANA 5 - CRUD Produtos Completo

### Objetivo
Sistema completo de gestão de produtos com:
- Lista paginada com filtros avançados
- Formulário de criação/edição
- Fichas técnicas (BOM - Bill of Materials)
- Upload de imagens
- Recálculo de custos

---

### 1️⃣ Estrutura de Arquivos

```
frontend/src/features/catalog/
├── api/
│   ├── products.ts          # API client
│   ├── categories.ts        # API categorias
│   └── bom.ts              # API ficha técnica
├── components/
│   ├── ProductList.tsx      # Lista de produtos
│   ├── ProductFilters.tsx   # Filtros
│   ├── ProductForm.tsx      # Formulário
│   ├── ProductCard.tsx      # Card do produto
│   ├── BOMEditor.tsx        # Editor de ficha técnica
│   └── ImageUpload.tsx      # Upload de imagem
├── hooks/
│   ├── useProducts.ts       # Hook para produtos
│   ├── useCategories.ts     # Hook para categorias
│   └── useBOM.ts           # Hook para BOM
└── types.ts                # TypeScript types

frontend/app/produtos/
├── page.tsx                # Lista de produtos
├── novo/
│   └── page.tsx           # Criar produto
└── [id]/
    ├── page.tsx           # Detalhes/Editar
    └── ficha-tecnica/
        └── page.tsx       # Editar ficha técnica
```

---

### 2️⃣ Types e Interfaces

**Criar:** `frontend/src/features/catalog/types.ts`

```typescript
export enum TipoProduto {
  SIMPLES = 'SIMPLES',
  COMPOSTO = 'COMPOSTO',
  MATERIA_PRIMA = 'MATERIA_PRIMA'
}

export enum UnidadeMedida {
  UN = 'UN',
  KG = 'KG',
  L = 'L',
  CX = 'CX'
}

export interface Categoria {
  id: string
  nome: string
  descricao?: string
  ativo: boolean
  ordem: number
  created_at: string
}

export interface Produto {
  id: string
  nome: string
  descricao?: string
  tipo: TipoProduto
  categoria: Categoria
  preco_custo?: number
  preco_venda: number
  margem_lucro?: number
  unidade_medida: UnidadeMedida
  codigo_barras?: string
  sku?: string
  ativo: boolean
  estoque_minimo?: number
  estoque_maximo?: number
  foto?: string
  created_at: string
  updated_at: string
}

export interface FichaTecnicaItem {
  id: string
  produto_pai: string
  produto_filho: Produto
  quantidade: number
  custo_unitario: number
  custo_total: number
  created_at: string
}

export interface CreateProdutoDTO {
  nome: string
  descricao?: string
  tipo: TipoProduto
  categoria_id: string
  preco_custo?: number
  preco_venda: number
  unidade_medida: UnidadeMedida
  codigo_barras?: string
  sku?: string
  ativo?: boolean
  estoque_minimo?: number
  estoque_maximo?: number
}

export interface ProductFilters {
  search?: string
  categoria_id?: string
  tipo?: TipoProduto
  preco_min?: number
  preco_max?: number
  ativo?: boolean
  ordering?: string
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  page_size: number
  total_pages: number
  current_page: number
  results: T[]
}
```

---

### 3️⃣ API Client

**Criar:** `frontend/src/features/catalog/api/products.ts`

```typescript
import { request } from '@/lib/http/request'
import { 
  Produto, 
  CreateProdutoDTO, 
  ProductFilters, 
  PaginatedResponse 
} from '../types'

const BASE_URL = '/produtos'

export const productsApi = {
  // Listar produtos com filtros
  async list(filters?: ProductFilters): Promise<PaginatedResponse<Produto>> {
    const params = new URLSearchParams()
    
    if (filters?.search) params.append('search', filters.search)
    if (filters?.categoria_id) params.append('categoria', filters.categoria_id)
    if (filters?.tipo) params.append('tipo', filters.tipo)
    if (filters?.preco_min) params.append('preco_min', filters.preco_min.toString())
    if (filters?.preco_max) params.append('preco_max', filters.preco_max.toString())
    if (filters?.ativo !== undefined) params.append('ativo', filters.ativo.toString())
    if (filters?.ordering) params.append('ordering', filters.ordering)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())
    
    const queryString = params.toString()
    const url = queryString ? `${BASE_URL}/?${queryString}` : `${BASE_URL}/`
    
    return request.get<PaginatedResponse<Produto>>(url)
  },

  // Obter produto por ID
  async get(id: string): Promise<Produto> {
    return request.get<Produto>(`${BASE_URL}/${id}/`)
  },

  // Criar produto
  async create(data: CreateProdutoDTO): Promise<Produto> {
    return request.post<Produto>(`${BASE_URL}/`, data)
  },

  // Atualizar produto
  async update(id: string, data: Partial<CreateProdutoDTO>): Promise<Produto> {
    return request.put<Produto>(`${BASE_URL}/${id}/`, data)
  },

  // Deletar produto
  async delete(id: string): Promise<void> {
    return request.delete(`${BASE_URL}/${id}/`)
  },

  // Recalcular custo (para produtos compostos)
  async recalcularCusto(id: string): Promise<Produto> {
    return request.post<Produto>(`${BASE_URL}/${id}/recalcular_custo/`)
  },

  // Upload de imagem
  async uploadImage(id: string, file: File): Promise<Produto> {
    const formData = new FormData()
    formData.append('foto', file)
    
    return request.patch<Produto>(`${BASE_URL}/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}
```

**Criar:** `frontend/src/features/catalog/api/categories.ts`

```typescript
import { request } from '@/lib/http/request'
import { Categoria } from '../types'

const BASE_URL = '/categorias'

export const categoriesApi = {
  async list(): Promise<Categoria[]> {
    const response = await request.get<Categoria[]>(`${BASE_URL}/`)
    return response
  },

  async get(id: string): Promise<Categoria> {
    return request.get<Categoria>(`${BASE_URL}/${id}/`)
  },

  async create(data: { nome: string; descricao?: string }): Promise<Categoria> {
    return request.post<Categoria>(`${BASE_URL}/`, data)
  },

  async update(id: string, data: Partial<Categoria>): Promise<Categoria> {
    return request.put<Categoria>(`${BASE_URL}/${id}/`, data)
  },

  async delete(id: string): Promise<void> {
    return request.delete(`${BASE_URL}/${id}/`)
  },
}
```

**Criar:** `frontend/src/features/catalog/api/bom.ts`

```typescript
import { request } from '@/lib/http/request'
import { FichaTecnicaItem } from '../types'

const BASE_URL = '/fichas-tecnicas'

export const bomApi = {
  // Listar itens da ficha técnica de um produto
  async list(produtoId: string): Promise<FichaTecnicaItem[]> {
    return request.get<FichaTecnicaItem[]>(`${BASE_URL}/?produto_pai=${produtoId}`)
  },

  // Adicionar item à ficha técnica
  async create(data: {
    produto_pai_id: string
    produto_filho_id: string
    quantidade: number
  }): Promise<FichaTecnicaItem> {
    return request.post<FichaTecnicaItem>(`${BASE_URL}/`, data)
  },

  // Atualizar quantidade
  async update(id: string, quantidade: number): Promise<FichaTecnicaItem> {
    return request.patch<FichaTecnicaItem>(`${BASE_URL}/${id}/`, { quantidade })
  },

  // Remover item
  async delete(id: string): Promise<void> {
    return request.delete(`${BASE_URL}/${id}/`)
  },
}
```

---

### 4️⃣ Hooks Customizados

**Criar:** `frontend/src/features/catalog/hooks/useProducts.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { productsApi } from '../api/products'
import { CreateProdutoDTO, ProductFilters } from '../types'

const QUERY_KEYS = {
  products: (filters?: ProductFilters) => ['products', filters] as const,
  product: (id: string) => ['product', id] as const,
}

export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: QUERY_KEYS.products(filters),
    queryFn: () => productsApi.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
  })
}

export function useProduct(id: string | null) {
  return useQuery({
    queryKey: QUERY_KEYS.product(id!),
    queryFn: () => productsApi.get(id!),
    enabled: !!id,
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: CreateProdutoDTO) => productsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateProdutoDTO> }) =>
      productsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.product(variables.id) })
    },
  })
}

export function useDeleteProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => productsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export function useRecalcularCusto() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => productsApi.recalcularCusto(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.product(id) })
    },
  })
}
```

---

### 5️⃣ Componentes

**Criar:** `frontend/src/features/catalog/components/ProductList.tsx`

```typescript
'use client'

import React, { useState } from 'react'
import { useProducts, useDeleteProduct } from '../hooks/useProducts'
import { ProductFilters as Filters } from '../types'
import { ProductFilters } from './ProductFilters'
import { ProductCard } from './ProductCard'
import { Loader2, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function ProductList() {
  const router = useRouter()
  const [filters, setFilters] = useState<Filters>({
    page: 1,
    page_size: 20,
  })

  const { data, isLoading, error } = useProducts(filters)
  const deleteMutation = useDeleteProduct()

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja excluir este produto?')) {
      try {
        await deleteMutation.mutateAsync(id)
      } catch (err) {
        alert('Erro ao excluir produto')
      }
    }
  }

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg">
        Erro ao carregar produtos
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Produtos</h1>
          <p className="text-gray-500 text-sm">{data?.count || 0} produtos cadastrados</p>
        </div>
        <button
          onClick={() => router.push('/produtos/novo')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus className="w-5 h-5" />
          Novo Produto
        </button>
      </div>

      {/* Filtros */}
      <ProductFilters filters={filters} onChange={setFilters} />

      {/* Grid de Produtos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {data?.results.map((produto) => (
          <ProductCard
            key={produto.id}
            produto={produto}
            onDelete={() => handleDelete(produto.id)}
            onEdit={() => router.push(`/produtos/${produto.id}`)}
          />
        ))}
      </div>

      {/* Paginação */}
      {data && data.total_pages > 1 && (
        <div className="flex justify-center gap-2 mt-6">
          <button
            onClick={() => handlePageChange(filters.page! - 1)}
            disabled={!data.previous}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Anterior
          </button>
          <span className="px-4 py-2">
            Página {data.current_page} de {data.total_pages}
          </span>
          <button
            onClick={() => handlePageChange(filters.page! + 1)}
            disabled={!data.next}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Próxima
          </button>
        </div>
      )}

      {/* Empty State */}
      {data?.results.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Nenhum produto encontrado</p>
          <p className="text-sm">Tente ajustar os filtros ou criar um novo produto</p>
        </div>
      )}
    </div>
  )
}
```

---

**Continua no próximo arquivo com mais componentes...**

---

## 📦 Instalação de Dependências

```bash
cd frontend

# React Query (já instalado)
# Caso não esteja:
npm install @tanstack/react-query

# React Hook Form + Zod (validação)
npm install react-hook-form @hookform/resolvers zod

# Para upload de imagens
npm install react-dropzone
```

---

## ✅ Critérios de Aceitação

### Semana 5 - Produtos
- [ ] Lista de produtos funcional com paginação
- [ ] Filtros funcionando (busca, categoria, preço, tipo)
- [ ] Criar produto com validação
- [ ] Editar produto existente
- [ ] Upload de imagem funcional
- [ ] Deletar produto com confirmação
- [ ] Ficha técnica (BOM) básica

---

**Próximo:** Continue com `SPRINT_2_SEMANA_6_ESTOQUE.md` para a implementação completa do estoque!
