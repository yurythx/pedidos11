import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { VendaSnapshotItem, Produto } from '../../types'
import { useAuthStore } from '../auth/store'

type CartItem = {
  produto_id: number
  quantidade: number
  produto?: Pick<Produto, 'id' | 'nome' | 'preco_venda' | 'tipo'>
}

type CartState = {
  items: CartItem[]
  addItem: (produto: Produto) => void
  removeItem: (produto_id: number) => void
  increment: (produto_id: number) => void
  decrement: (produto_id: number) => void
  clear: () => void
  snapshot: () => VendaSnapshotItem[]
  subtotal: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (produto) =>
        set((s) => {
          const idx = s.items.findIndex((i) => i.produto_id === produto.id)
          if (idx >= 0) {
            const next = [...s.items]
            next[idx] = { ...next[idx], quantidade: next[idx].quantidade + 1 }
            return { items: next }
          }
          return {
            items: [
              ...s.items,
              {
                produto_id: produto.id,
                quantidade: 1,
                produto: { id: produto.id, nome: produto.nome, preco_venda: produto.preco_venda, tipo: produto.tipo },
              },
            ],
          }
        }),
      removeItem: (produto_id) =>
        set((s) => ({ items: s.items.filter((i) => i.produto_id !== produto_id) })),
      increment: (produto_id) =>
        set((s) => {
          const idx = s.items.findIndex((i) => i.produto_id === produto_id)
          if (idx < 0) return s
          const next = [...s.items]
          next[idx] = { ...next[idx], quantidade: next[idx].quantidade + 1 }
          return { items: next }
        }),
      decrement: (produto_id) =>
        set((s) => {
          const idx = s.items.findIndex((i) => i.produto_id === produto_id)
          if (idx < 0) return s
          const next = [...s.items]
          const q = next[idx].quantidade - 1
          if (q <= 0) return { items: next.filter((i) => i.produto_id !== produto_id) }
          next[idx] = { ...next[idx], quantidade: q }
          return { items: next }
        }),
      clear: () => set({ items: [] }),
      snapshot: () => get().items.map((i) => ({ produto_id: i.produto_id, quantidade: i.quantidade })),
      subtotal: () =>
        get().items.reduce((acc, i) => acc + (i.produto?.preco_venda ?? 0) * i.quantidade, 0),
    }),
    {
      name: 'nix-pdv-cart',
      storage: createJSONStorage(() => localStorage),
      version: 1,
      migrate: (persisted, _version) => persisted as any,
    }
  )
)

