import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { Usuario } from '../../types'

export interface Tokens {
  access: string | null
  refresh: string | null
}

interface AuthState {
  user: Usuario | null
  tokens: Tokens
  tenantId: string | null
  login: (user: Usuario, tokens: Tokens) => void
  logout: () => void
  setTenantId: (tenantId: number | null) => void
  setTokens: (tokens: Tokens) => void
  setUser: (user: Usuario | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: { access: null, refresh: null },
      tenantId: null,
      login: (user, tokens) => set({ user, tokens, tenantId: user.empresa_id }),
      logout: () =>
        set({ user: null, tokens: { access: null, refresh: null }, tenantId: null }),
      setTenantId: (tenantId) => set({ tenantId }),
      setTokens: (tokens) => set({ tokens }),
      setUser: (user) => set({ user }),
    }),
    {
      name: 'nix-auth',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
)

