export type EnvConfig = {
  apiUrl: string
  authRefreshPath: string
}

export const getEnv = (): EnvConfig => {
  const isServer = typeof window === 'undefined'
  // No servidor (SSR), usa a rede interna do Docker se disponível
  const apiUrl = (isServer && process.env.API_URL_INTERNAL) 
    ? process.env.API_URL_INTERNAL 
    : (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8002/api')

  return {
    apiUrl,
    authRefreshPath: process.env.NEXT_PUBLIC_AUTH_REFRESH_PATH ?? '/auth/token/refresh/',
  }
}

