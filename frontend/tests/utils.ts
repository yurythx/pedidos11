export const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://api.projetohavoc.shop:8002/api'

let access: string | null = null

export const apiFetch = async (path: string, init: any = {}) => {
  const headers = { ...(init.headers || {}) }
  if (access) headers['Authorization'] = `Bearer ${access}`
  const res = await fetch(`${API}${path}`, { ...init, headers })
  const data = await res.json().catch(() => null)
  return { status: res.status, data }
}

export const login = async () => {
  if (access) return
  const res = await fetch(`${API}/auth/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'admin123' }),
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`Login falhou: ${res.status} ${txt}`)
  }
  const json = await res.json()
  access = json.access
}

export const getAuthHeaders = () => {
    return access ? { 'Authorization': `Bearer ${access}` } : {}
}
