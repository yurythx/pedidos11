import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { Mesa } from '../../types'

type MesasState = {
  mesas: Mesa[]
  setMesas: (m: Mesa[]) => void
  setStatus: (id: string, status: Mesa['status']) => void
}

export const useMesasStore = create<MesasState>()(
  persist(
    (set) => ({
      mesas: [],
      setMesas: (m) => set({ mesas: m }),
      setStatus: (id, status) =>
        set((s) => ({
          mesas: s.mesas.map((m) => (m.id === id ? { ...m, status } : m)),
        })),
    }),
    {
      name: 'nix-mesas',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
)

