import { describe, it, expect, beforeAll } from 'vitest'
import { apiFetch, getAuthHeaders, login } from '../utils'

describe('Gestão de Usuários e Perfil', () => {
  beforeAll(async () => {
    await login()
  })

  const timestamp = Date.now()
  const novoUsuario = {
    username: `user_${timestamp}`,
    password: 'password123',
    email: `user_${timestamp}@teste.com`,
    first_name: 'Usuario',
    last_name: 'Teste',
    cargo: 'VENDEDOR',
    is_active: true
  }

  let userId: string

  it('deve criar um novo usuário', async () => {
    const res = await apiFetch('/usuarios/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novoUsuario)
    })
    
    if (res.status !== 201) {
        console.error('Create User Error:', JSON.stringify(res.data, null, 2))
    }
    expect(res.status).toBe(201)
    expect(res.data.username).toBe(novoUsuario.username)
    expect(res.data.email).toBe(novoUsuario.email)
    
    userId = res.data.id
  })

  it('deve listar usuários com paginação', async () => {
    const res = await apiFetch('/usuarios/?page=1&page_size=10')
    expect(res.status).toBe(200)
    expect(res.data.results).toBeInstanceOf(Array)
    expect(res.data.count).toBeGreaterThan(0)
    
    // Verifica se o usuário criado está na lista
    const found = res.data.results.find((u: any) => u.id === userId)
    expect(found).toBeDefined()
  })

  it('deve atualizar o usuário criado', async () => {
    const updatePayload = {
      first_name: 'Usuario Editado',
      cargo: 'GERENTE'
    }

    const res = await apiFetch(`/usuarios/${userId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatePayload)
    })

    expect(res.status).toBe(200)
    expect(res.data.first_name).toBe('Usuario Editado')
    expect(res.data.cargo).toBe('GERENTE')
  })

  it('deve obter o perfil do usuário logado', async () => {
    const res = await apiFetch('/usuarios/me/')
    expect(res.status).toBe(200)
    expect(res.data.username).toBe('admin') // Assumindo login como admin
  })

  it('deve atualizar o perfil do usuário logado', async () => {
    const originalRes = await apiFetch('/usuarios/me/')
    const originalName = originalRes.data.first_name

    const updatePayload = {
      first_name: 'Admin Updated'
    }

    const res = await apiFetch('/usuarios/me/', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatePayload)
    })

    expect(res.status).toBe(200)
    expect(res.data.first_name).toBe('Admin Updated')

    // Reverter
    await apiFetch('/usuarios/me/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ first_name: originalName })
    })
  })

  it('deve excluir o usuário criado', async () => {
    const res = await apiFetch(`/usuarios/${userId}/`, {
      method: 'DELETE'
    })
    expect(res.status).toBe(204)

    // Verificar que sumiu
    const getRes = await apiFetch(`/usuarios/${userId}/`)
    expect(getRes.status).toBe(404)
  })
})
