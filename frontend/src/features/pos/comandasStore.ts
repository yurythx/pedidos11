import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { Comanda } from '../../types'

type ComandasState = {
  comandas: Comanda[]
  setComandas: (c: Comanda[]) => void
  setStatus: (id: string, status: Comanda['status']) => void
}

export const useComandasStore = create<ComandasState>()(
  persist(
    (set) => ({
      comandas: [],
      setComandas: (c) => set({ comandas: c }),
      setStatus: (id, status) =>
        set((s) => ({
          comandas: s.comandas.map((c) => (c.id === id ? { ...c, status } : c)),
        })),
    }),
    {
      name: 'nix-comandas',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
)
