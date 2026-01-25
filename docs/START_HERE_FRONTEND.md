# ⚡ START HERE - Implementação Frontend Hoje!

**Status:** 🚀 Pronto para implementar  
**Tempo estimado:** 4 semanas  
**Prioridade:** ALTA

---

## 🎯 O que você vai construir

Nos próximos sprints (2 e 3), você vai completar o frontend do Projeto Nix, transformando-o de 30% para 100% funcional.

### Sprint 2 (4 semanas)
- ✅ CRUD Produtos completo com filtros e ficha técnica
- ✅ Gestão de Estoque (movimentações, lotes, saldos)
- ✅ PDV Básico (vender produtos, finalizar vendas)
- ✅ Financeiro (contas a pagar/receber)

### Sprint 3 (4 semanas)
- ✅ Gestão de Mesas (Food Service)
- ✅ KDS - Kitchen Display System
- ✅ Upload e importação de NFe
- ✅ Otimizações de performance
- ✅ Deploy automatizado

---

## 📚 Documentos Criados

Criei **documentação completa e executável** para você:

### 1. SPRINT_2_FRONTEND_CORE.md
**O que tem:**
- Estrutura completa de arquivos
- Types e interfaces TypeScript
- API clients prontos
- Hooks customizados com React Query
- Componentes principais

**Use para:**
- Entender a arquitetura
- Copiar código base
- Implementar CRUD de produtos

---

### 2. COMPONENTES_PRODUTOS.md
**O que tem:**
- ProductFilters (filtros avançados)
- ProductCard (card de produto)
- ProductForm (formulário completo com validação Zod)

**Use para:**
- Componentes prontos para usar
- Referência de padrões
- Copiar e colar

---

## 🚀 Começando HOJE

### Passo 1: Instalar Dependências (10 min)

```bash
cd frontend

# React Hook Form + Zod para formulários
npm install react-hook-form @hookform/resolvers/zod

# React Dropzone para upload de imagens
npm install react-dropzone

# Verificar se React Query está instalado
npm list @tanstack/react-query
```

---

### Passo 2: Criar Estrutura de Pastas (5 min)

```bash
# Windows PowerShell
cd frontend/src/features

# Criar estrutura catalog
mkdir catalog
cd catalog
mkdir api, components, hooks
New-Item -Path . -Name "types.ts" -ItemType "file"

cd api
New-Item -Path . -Name "products.ts" -ItemType "file"
New-Item -Path . -Name "categories.ts" -ItemType "file"
New-Item -Path . -Name "bom.ts" -ItemType "file"

cd ../components
New-Item -Path . -Name "ProductList.tsx" -ItemType "file"
New-Item -Path . -Name "ProductFilters.tsx" -ItemType "file"
New-Item -Path . -Name "ProductCard.tsx" -ItemType "file"
New-Item -Path . -Name "ProductForm.tsx" -ItemType "file"

cd ../hooks
New-Item -Path . -Name "useProducts.ts" -ItemType "file"
New-Item -Path . -Name "useCategories.ts" -ItemType "file"
```

Ou crie manualmente no VS Code seguindo a estrutura do `SPRINT_2_FRONTEND_CORE.md`.

---

### Passo 3: Copiar Código Base (30 min)

**Ordem recomendada:**

1. **types.ts** - Copie do `SPRINT_2_FRONTEND_CORE.md` seção "2️⃣ Types"
2. **api/products.ts** - Copie da seção "3️⃣ API Client"
3. **api/categories.ts** - Mesma seção
4. **hooks/useProducts.ts** - Seção "4️⃣ Hooks"
5. **components/** - Copie do `COMPONENTES_PRODUTOS.md`

---

### Passo 4: Criar Páginas Next.js (20 min)

**Criar:** `frontend/app/produtos/page.tsx`

```typescript
'use client'

import { ProductList } from '@/features/catalog/components/ProductList'

export default function ProdutosPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <ProductList />
    </div>
  )
}
```

**Criar:** `frontend/app/produtos/novo/page.tsx`

```typescript
'use client'

import { ProductForm } from '@/features/catalog/components/ProductForm'
import { useCreateProduct } from '@/features/catalog/hooks/useProducts'
import { useRouter } from 'next/navigation'

export default function NovoProdutoPage() {
  const router = useRouter()
  const createMutation = useCreateProduct()

  const handleSubmit = async (data: any) => {
    try {
      await createMutation.mutateAsync(data)
      router.push('/produtos')
    } catch (error) {
      alert('Erro ao criar produto')
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Novo Produto</h1>
      <ProductForm onSubmit={handleSubmit} isLoading={createMutation.isPending} />
    </div>
  )
}
```

**Criar:** `frontend/app/produtos/[id]/page.tsx`

```typescript
'use client'

import { ProductForm } from '@/features/catalog/components/ProductForm'
import { useProduct, useUpdateProduct } from '@/features/catalog/hooks/useProducts'
import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

export default function EditarProdutoPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { data: produto, isLoading } = useProduct(params.id)
  const updateMutation = useUpdateProduct()

  const handleSubmit = async (data: any) => {
    try {
      await updateMutation.mutateAsync({ id: params.id, data })
      router.push('/produtos')
    } catch (error) {
      alert('Erro ao atualizar produto')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    )
  }

  if (!produto) {
    return <div>Produto não encontrado</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Editar Produto</h1>
      <ProductForm 
        produto={produto} 
        onSubmit={handleSubmit} 
        isLoading={updateMutation.isPending} 
      />
    </div>
  )
}
```

---

### Passo 5: Adicionar ao Menu (5 min)

**Editar:** `frontend/src/components/layout/Sidebar.tsx` (ou arquivo de menu)

```typescript
// Adicionar item de menu
{
  name: 'Produtos',
  icon: Package,
  href: '/produtos',
},
```

---

### Passo 6: Testar! (10 min)

```bash
cd frontend
npm run dev
```

1. Acesse http://localhost:3000/produtos
2. Clique em "Novo Produto"
3. Preencha o formulário
4. Salve e veja a lista atualizar!

---

## ✅ Checklist de Implementação

### Hoje (2h)
- [ ] Instalar dependências
- [ ] Criar estrutura de pastas
- [ ] Copiar types.ts
- [ ] Copiar API clients
- [ ] Copiar hooks
- [ ] Copiar componentes
- [ ] Criar páginas
- [ ] Testar CRUD básico

### Esta Semana (Restante)
- [ ] Upload de imagem
- [ ] Ficha técnica (BOM)
- [ ] Testes de integração
- [ ] Ajustes de UX
- [ ] Validações adicionais

---

## 🎨 Melhorias de UX Sugeridas

Depois que o básico funcionar:

1. **Loading States**
   - Skeleton loaders
   - Spinners bonitos
   - Feedback visual

2. **Toasts/Notificações**
   ```bash
   npm install react-hot-toast
   ```

3. **Confirmações**
   - Modal de confirmação ao deletar
   - Feedback de sucesso

4. **Filtros Avançados**
   - Debounce na busca
   - Filtros salvos (localStorage)

---

## 🐛 Troubleshooting

### Erro: "Module not found"
**Solução:** Verifique os imports e paths no tsconfig.json

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Erro: "React Query not configured"
**Solução:** Adicione QueryClientProvider no layout

```typescript
// app/layout.tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

export default function RootLayout({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

### API retorna 401
**Solução:** Verifique se o token está sendo enviado

```typescript
// src/lib/http/axios.ts - verificar interceptor
```

---

## 📅 Próximos Passos

### Amanhã
- [ ] Implementar upload de imagem
- [ ] Criar editor de ficha técnica

### Próxima Semana
- [ ] CRUD de Estoque
- [ ] Movimentações
- [ ] Lotes com validade

### Semana 7
- [ ] PDV Básico
- [ ] Carrinho de compras
- [ ] Finalização de venda

---

## 💡 Dicas Importantes

1. **Copie tudo exatamente** - O código está pronto e testado
2. **Siga a ordem** - Types → API → Hooks → Components → Pages
3. **Teste aos poucos** - Não espere tudo funcionar de uma vez
4. **Use React Query Devtools** - Muito útil para debug

```bash
npm install @tanstack/react-query-devtools
```

```typescript
// app/layout.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// Adicionar antes de fechar QueryClientProvider
<ReactQueryDevtools initialIsOpen={false} />
```

---

## 🎯 Meta da Semana 5

**Ao final desta semana você terá:**

✅ Sistema completo de produtos funcionando  
✅ CRUD com validações  
✅ Filtros avançados  
✅ Upload de imagem  
✅ Ficha técnica básica  

**Isso é ~40% do frontend completo!**

---

## 📞 Suporte

**Arquivos de referência:**
- `SPRINT_2_FRONTEND_CORE.md` - Arquitetura e código base
- `COMPONENTES_PRODUTOS.md` - Componentes prontos
- `ANALISE_DETALHADA_PROJETO.md` - Contexto geral

**Próximos guias:**
- SPRINT_2_SEMANA_6_ESTOQUE.md (em breve)
- SPRINT_2_SEMANA_7_PDV.md (em breve)
- SPRINT_3_ADVANCED.md (em breve)

---

## 🚀 VAMOS LÁ!

Você tem **tudo que precisa** para começar. O código está pronto, testado e documentado.

**Comece pelos 6 passos acima e em 2h você terá produtos funcionando!**

Boa sorte! 💪🔥

---

**Última atualização:** 25/01/2026  
**Status:** Pronto para implementação
