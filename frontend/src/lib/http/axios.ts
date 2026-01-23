import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { getEnv } from '../../config/env'
import { useAuthStore } from '../../features/auth/store'

const env = getEnv()

const api = axios.create({
  baseURL: env.apiUrl,
})

let isRefreshing = false
let pendingRequests: Array<(token: string | null) => void> = []

const subscribeTokenRefresh = (cb: (token: string | null) => void) => {
  pendingRequests.push(cb)
}

const onRefreshed = (token: string | null) => {
  pendingRequests.forEach((cb) => cb(token))
  pendingRequests = []
}

// Helper para ler o localStorage com segurança (evita erro no SSR)
const getStorageItem = (key: string) => {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

api.interceptors.request.use((config: any) => {
  let { tokens, tenantId } = useAuthStore.getState()
  
  // FIX: Se o token for null, tenta ler do localStorage manualmente.
  // Isso resolve o problema de delay na hidratação do Zustand no reload.
  if (!tokens.access) {
    const stored = getStorageItem('nix-auth')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        // A estrutura do persist é { state: { tokens: ... }, version: number }
        if (parsed.state?.tokens?.access) {
          tokens = parsed.state.tokens
        }
        if (parsed.state?.tenantId) {
          tenantId = parsed.state.tenantId
        }
      } catch (e) {
        // Falha silenciosa no parse, mantém tokens como null
      }
    }
  }

  const access = tokens.access
  if (access) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${access}`
  }
  if (tenantId) {
    config.headers = config.headers ?? {}
    config.headers['X-Tenant-ID'] = String(tenantId)
  }
  return config
})

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    
    // Tratamento de Rate Limit (429)
    if (error.response?.status === 429) {
      const attempt = (originalRequest as any)._retry429 ?? 0
      if (attempt < 3) {
        ;(originalRequest as any)._retry429 = attempt + 1
        const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
        await wait(500 * Math.pow(2, attempt))
        return api(originalRequest)
      }
    }

    // Tratamento de Token Expirado (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      let { tokens } = useAuthStore.getState()

      // Fallback: Tenta recuperar o refresh token do storage se a store estiver vazia
      if (!tokens.refresh) {
         const stored = getStorageItem('nix-auth')
         if (stored) {
           try {
             const parsed = JSON.parse(stored)
             if (parsed.state?.tokens?.refresh) {
               tokens = parsed.state.tokens
             }
           } catch {}
         }
      }

      const refresh = tokens.refresh
      if (!refresh) {
        useAuthStore.getState().logout()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(error)
      }
      
      originalRequest._retry = true
      
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            if (token) {
              originalRequest.headers = originalRequest.headers ?? {}
              originalRequest.headers['Authorization'] = `Bearer ${token}`
              resolve(api(originalRequest))
            } else {
              resolve(Promise.reject(error))
            }
          })
        })
      }

      isRefreshing = true
      try {
        const res = await axios.post(
          `${env.apiUrl}${env.authRefreshPath}`,
          { refresh },
          { headers: { 'Content-Type': 'application/json' } }
        )
        // SimpleJWT retorna apenas { access } por padrão, mas pode retornar { access, refresh } se ROTATE_REFRESH_TOKENS=True
        const newAccess = (res.data as any)?.access ?? null
        // Se a rotação de token estiver ativa, pegamos o novo refresh. Se não, mantemos o antigo.
        const newRefresh = (res.data as any)?.refresh ?? refresh
        
        useAuthStore.getState().setTokens({ access: newAccess, refresh: newRefresh })
        onRefreshed(newAccess)
        
        isRefreshing = false
        originalRequest.headers = originalRequest.headers ?? {}
        if (newAccess) originalRequest.headers['Authorization'] = `Bearer ${newAccess}`
        return api(originalRequest)
      } catch (refreshError: any) {
        // Se o erro for 401 no refresh, o token realmente expirou
        isRefreshing = false
        useAuthStore.getState().logout()
        onRefreshed(null)
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export { api }
