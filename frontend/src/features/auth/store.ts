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
  _hasHydrated: boolean
  login: (user: Usuario, tokens: Tokens) => void
  logout: () => void
  setTenantId: (tenantId: string | null) => void
  setTokens: (tokens: Tokens) => void
  setUser: (user: Usuario | null) => void
  setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: { access: null, refresh: null },
      tenantId: null,
      _hasHydrated: false,
      login: (user: Usuario, tokens: Tokens) => set({ user, tokens, tenantId: user.empresa_id }),
      logout: () =>
        set({ user: null, tokens: { access: null, refresh: null }, tenantId: null }),
      setTenantId: (tenantId: string | null) => set({ tenantId }),
      setTokens: (tokens: Tokens) => set({ tokens }),
      setUser: (user: Usuario | null) => set({ user }),
      setHasHydrated: (state: boolean) => set({ _hasHydrated: state }),
    }),
    {
      name: 'nix-auth',
      storage: createJSONStorage(() => localStorage),
      version: 1,
      onRehydrateStorage: () => (state: AuthState | undefined) => {
        state?.setHasHydrated(true)
      },
    }
  )
)

