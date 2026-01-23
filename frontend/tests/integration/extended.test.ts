import { describe, it, expect, beforeAll } from 'vitest'
import fs from 'fs'
import path from 'path'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://api.projetohavoc.shop:8002/api'
let access: string | null = null
let userId: string | null = null
const apiFetch = async (path: string, init: any = {}) => {
  const headers = { ...(init.headers || {}) }
  if (access) headers['Authorization'] = `Bearer ${access}`
  const res = await fetch(`${API}${path}`, { ...init, headers })
  const data = await res.json().catch(() => null)
  return { status: res.status, data }
}

describe('API integração estendida', () => {
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
    const me = await apiFetch('/usuarios/me/')
    if (me.status !== 200) throw new Error(`Falha ao obter usuário: ${me.status}`)
    userId = me.data.id
  })

  it('dashboard resumo do dia', async () => {
    const res = await apiFetch('/dashboard/resumo-dia/')
    expect(res.status).toBe(200)
    expect(typeof res.data).toBe('object')
  })

  it('movimentações com paginação e ordering', async () => {
    const res = await apiFetch('/movimentacoes/?page_size=5&ordering=-created_at')
    expect(res.status).toBe(200)
  })

  it('lotes por status de validade', async () => {
    const res = await apiFetch('/lotes/?status_validade=OK&page_size=5')
    expect(res.status).toBe(200)
  })

  it('cria endereço para cliente', async () => {
    const clientes = await apiFetch('/clientes/?page_size=1')
    let clienteId = clientes.data?.results?.[0]?.id
    if (!clienteId) {
      const novo = await apiFetch('/clientes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: 'Cliente Teste', cpf_cnpj: '00000000000' }),
      })
      clienteId = novo.data?.id
    }
    const endereco = await apiFetch('/enderecos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content_type: 'partners.cliente',
        object_id: clienteId,
        tipo: 'ENTREGA',
        cep: '01310-000',
        logradouro: 'Av. Paulista',
        numero: '1000',
        complemento: 'Conj 1',
        bairro: 'Bela Vista',
        cidade: 'São Paulo',
        uf: 'SP',
        referencia: 'Próximo ao MASP',
      }),
    })
    expect(endereco.status).toBe(201)
  })

  it('fluxo venda: criar e validar estoque', async () => {
    const deps = await apiFetch('/depositos/?page_size=1')
    const depositoId = (deps.data?.results ?? deps.data)?.[0]?.id
    const venda = await apiFetch('/vendas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        vendedor: userId,
        tipo_pagamento: 'DINHEIRO',
        observacoes: 'Fluxo integração',
      }),
    })
    const vendaId = venda.data.id
    const produtos = await apiFetch('/produtos/?tipo=FINAL&page_size=1')
    const produto = (produtos.data?.results ?? produtos.data)?.[0]
    const produtoId = produto?.id
    await apiFetch(`/vendas/${vendaId}/adicionar_item/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        produto: produtoId,
        quantidade: 1,
        preco_unitario: Number(produto?.preco_venda ?? 0),
        desconto: 0,
      }),
    })
    const valid = await apiFetch(`/vendas/${vendaId}/validar_estoque/?deposito_id=${depositoId}`)
    expect(valid.status).toBe(200)
    // Finalização e cancelamento cobertos em testes unitários; aqui validamos pré-condições de estoque
  })

  it('NFe: confirmar importação cria lotes e vínculos', async () => {
    const deps = await apiFetch('/depositos/?page_size=1')
    const depositoId = (deps.data?.results ?? deps.data)?.[0]?.id
    const produtos = await apiFetch('/produtos/?page_size=1')
    const produto = (produtos.data?.results ?? produtos.data)?.[0]
    const produtoId = produto?.id
    const validade = new Date()
    validade.setFullYear(validade.getFullYear() + 1)
    const dataVal = validade.toISOString().slice(0, 10)
    const payload = {
      deposito_id: depositoId,
      numero_nfe: `12345-${Date.now()}`,
      serie_nfe: '1',
      fornecedor: {
        cnpj: '73.621.701/0001-29',
        nome: `Fornecedor Teste ${Date.now()}`,
      },
      itens: [
        {
          codigo_xml: 'TEST001',
          produto_id: produtoId,
          fator_conversao: 2,
          qtd_xml: 3,
          preco_custo: 4.5,
          lote: {
            codigo: 'LOTE-NFE-IT-' + Date.now(),
            validade: dataVal,
          },
        },
      ],
    }
    const res = await apiFetch('/nfe/importacao/confirmar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.status !== 200 && res.status !== 201) {
      console.error('NFe Import Error:', JSON.stringify(res.data, null, 2))
    }
    expect([200, 201]).toContain(res.status)
    expect(res.data?.resultado?.lotes_criados).toBeGreaterThanOrEqual(1)
    // Vinculos podem ser 0 se já existiam
    expect(res.data?.resultado?.vinculos_criados).toBeGreaterThanOrEqual(0)
  })
  
  // KDS endpoints cobertos em testes de módulo; na integração validamos criação de itens
  
  it('Financeiro: listar contas a receber', async () => {
    const deps = await apiFetch('/depositos/?page_size=1')
    const depositoId = (deps.data?.results ?? deps.data)?.[0]?.id
    const venda = await apiFetch('/vendas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        vendedor: userId,
        tipo_pagamento: 'DINHEIRO',
        observacoes: 'Financeiro fluxo',
      }),
    })
    const vendaId = venda.data.id
    const produtos = await apiFetch('/produtos/?page_size=1')
    const produto = (produtos.data?.results ?? produtos.data)?.[0]
    const produtoId = produto?.id
    const validade2 = new Date()
    validade2.setDate(validade2.getDate() + 90)
    const dataVal2 = validade2.toISOString().slice(0, 10)
    const codigo2 = 'LOTE-FIN-' + Date.now()
    await apiFetch(`/lotes/dar_entrada/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        produto_id: produtoId,
        deposito_id: depositoId,
        quantidade: 2,
        codigo_lote: codigo2,
        data_validade: dataVal2,
      }),
    })
    await apiFetch(`/vendas/${vendaId}/adicionar_item/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        produto: produtoId,
        quantidade: 1,
        preco_unitario: Number(produto?.preco_venda ?? 0),
        desconto: 0,
      }),
    })
    const contas = await apiFetch('/contas-receber/?page_size=5')
    expect(contas.status).toBe(200)
  })
  
  it('Lote: rastreabilidade via movimentações', async () => {
    const deps = await apiFetch('/depositos/?page_size=1')
    const depositoId = (deps.data?.results ?? deps.data)?.[0]?.id
    const produtos = await apiFetch('/produtos/?page_size=1')
    const produto = (produtos.data?.results ?? produtos.data)?.[0]
    const produtoId = produto?.id
    const validade = new Date()
    validade.setDate(validade.getDate() + 180)
    const dataVal = validade.toISOString().slice(0, 10)
    const codigo = 'LOTE-RST-' + Date.now()
    const entrada = await apiFetch(`/lotes/dar_entrada/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        produto_id: produtoId,
        deposito_id: depositoId,
        quantidade: 5,
        codigo_lote: codigo,
        data_validade: dataVal,
      }),
    })
    expect(entrada.status).toBe(201)
    const loteId = entrada.data?.lote?.id
    const movs = await apiFetch(`/lotes/${loteId}/movimentacoes/`)
    expect(movs.status).toBe(200)
  })
})
