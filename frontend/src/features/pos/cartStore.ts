import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { VendaSnapshotItem, Produto } from '../../types'
import { useAuthStore } from '../auth/store'

export type CartItem = {
  produto_id: string
  quantidade: number
  observacoes?: string
  produto?: Pick<Produto, 'id' | 'nome' | 'preco_venda' | 'tipo'>
}

type CartState = {
  items: CartItem[]
  mesaId: string | null
  comandaId: string | null
  clienteId: string | null
  setMesaId: (id: string | null) => void
  setComandaId: (id: string | null) => void
  setClienteId: (id: string | null) => void
  addItem: (produto: Produto) => void
  removeItem: (produto_id: string) => void
  updateObservation: (produto_id: string, obs: string) => void
  increment: (produto_id: string) => void
  decrement: (produto_id: string) => void
  clear: () => void
  clearItems: () => void
  resetBalcao: () => void
  snapshot: () => VendaSnapshotItem[]
  subtotal: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      mesaId: null,
      comandaId: null,
      clienteId: null,
      setMesaId: (id) => set({ mesaId: id }),
      setComandaId: (id) => set({ comandaId: id }),
      setClienteId: (id) => set({ clienteId: id }),
      // ... (addItem, removeItem, increment, decrement mantidos iguais) ...
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
        set((s) => ({ items: s.items.filter((i) => String(i.produto_id) !== String(produto_id)) })),
      updateObservation: (produto_id, obs) =>
        set((s) => {
          const idx = s.items.findIndex((i) => String(i.produto_id) === String(produto_id))
          if (idx < 0) return s
          const next = [...s.items]
          next[idx] = { ...next[idx], observacoes: obs }
          return { items: next }
        }),
      increment: (produto_id) =>
        set((s) => {
          const idx = s.items.findIndex((i) => String(i.produto_id) === String(produto_id))
          if (idx < 0) return s
          const next = [...s.items]
          next[idx] = { ...next[idx], quantidade: next[idx].quantidade + 1 }
          return { items: next }
        }),
      decrement: (produto_id) =>
        set((s) => {
          const idx = s.items.findIndex((i) => String(i.produto_id) === String(produto_id))
          if (idx < 0) return s
          const next = [...s.items]
          const q = next[idx].quantidade - 1
          if (q <= 0) return { items: next.filter((i) => String(i.produto_id) !== String(produto_id)) }
          next[idx] = { ...next[idx], quantidade: q }
          return { items: next }
        }),
      clear: () => set({ items: [], mesaId: null, comandaId: null, clienteId: null }),
      clearItems: () => set({ items: [] }),
      resetBalcao: () => set({ items: [], mesaId: null, comandaId: null, clienteId: null }),
      snapshot: () => get().items.map((i) => ({ 
        produto_id: i.produto_id, 
        quantidade: i.quantidade,
        observacoes: i.observacoes 
      })),
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

