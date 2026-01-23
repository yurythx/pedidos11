export type EnvConfig = {
  apiUrl: string
  authRefreshPath: string
}

export const getEnv = (): EnvConfig => ({
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8002/api',
  authRefreshPath: process.env.NEXT_PUBLIC_AUTH_REFRESH_PATH ?? '/auth/token/refresh/',
})

