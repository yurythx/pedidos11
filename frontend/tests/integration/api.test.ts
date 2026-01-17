import { describe, it, expect, beforeAll } from 'vitest'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api'

let access: string | null = null
let userId: string | null = null

const apiFetch = async (path: string, init: any = {}) => {
  const headers = { ...(init.headers || {}) }
  if (access) headers['Authorization'] = `Bearer ${access}`
  const res = await fetch(`${API}${path}`, { ...init, headers })
  const data = await res.json().catch(() => null)
  return { status: res.status, data }
}

describe('API integração básica', () => {
  beforeAll(async () => {
  const res = await fetch(`${API}/auth/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'admin', password: 'admin123' }),
    })
    const txt = await res.text()
    try {
      const json = JSON.parse(txt)
      access = json.access
    } catch {
      throw new Error(`Login falhou: status ${res.status} body: ${txt.slice(0,200)}`)
    }
  })

  it('perfil do usuário', async () => {
    const res = await apiFetch('/usuarios/me/')
    expect(res.status).toBe(200)
    expect(res.data.username).toBe('admin')
    userId = res.data.id
  })

  it('lista categorias', async () => {
    const res = await apiFetch('/categorias/?page_size=5')
    expect(res.status).toBe(200)
  })

  it('lista produtos', async () => {
    const res = await apiFetch('/produtos/?page_size=5')
    expect(res.status).toBe(200)
  })

  it('lista depósitos', async () => {
    const res = await apiFetch('/depositos/?page_size=5')
    expect(res.status).toBe(200)
  })

  it('lista lotes', async () => {
    const res = await apiFetch('/lotes/?page_size=5')
    expect(res.status).toBe(200)
  })

  it('cria venda e adiciona item', async () => {
    const clientes = await apiFetch('/clientes/?page_size=1')
    const clienteId = clientes.data?.results?.[0]?.id ?? null
    const venda = await apiFetch('/vendas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cliente: clienteId,
        vendedor: userId,
        tipo_pagamento: 'DINHEIRO',
        observacoes: 'Teste integração',
      }),
    })
    expect(venda.status).toBe(201)
    const vendaId = venda.data.id
    const produtos = await apiFetch('/produtos/?page_size=1')
    const produto = (produtos.data?.results ?? produtos.data)?.[0]
    const produtoId = produto?.id
    const item = await apiFetch(`/vendas/${vendaId}/adicionar_item/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        produto: produtoId,
        quantidade: 1,
        preco_unitario: Number(produto?.preco_venda ?? 0),
        desconto: 0,
      }),
    })
    expect(item.status).toBe(201)
  })
})
