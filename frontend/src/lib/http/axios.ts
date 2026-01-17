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

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const { tokens, tenantId } = useAuthStore.getState()
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
    if (error.response?.status === 429) {
      const attempt = (originalRequest as any)._retry429 ?? 0
      if (attempt < 3) {
        ;(originalRequest as any)._retry429 = attempt + 1
        const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
        await wait(500 * Math.pow(2, attempt))
        return api(originalRequest)
      }
    }
    if (error.response?.status === 401 && !originalRequest._retry) {
      const { tokens } = useAuthStore.getState()
      const refresh = tokens.refresh
      if (!refresh) {
        useAuthStore.getState().logout()
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
        const newAccess = (res.data as any)?.access ?? null
        const newRefresh = (res.data as any)?.refresh ?? refresh
        useAuthStore.getState().setTokens({ access: newAccess, refresh: newRefresh })
        onRefreshed(newAccess)
        isRefreshing = false
        originalRequest.headers = originalRequest.headers ?? {}
        if (newAccess) originalRequest.headers['Authorization'] = `Bearer ${newAccess}`
        return api(originalRequest)
      } catch {
        isRefreshing = false
        useAuthStore.getState().logout()
        onRefreshed(null)
        return Promise.reject(error)
      }
    }
    return Promise.reject(error)
  }
)

export { api }

