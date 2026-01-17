import { describe, it, expect } from 'vitest'
import { getMenuForRole, baseMenu } from '../src/features/rbac/menu'

describe('RBAC menu', () => {
  it('retorna itens para cargo ADMIN', () => {
    const items = getMenuForRole('ADMIN')
    expect(items.length).toBeGreaterThan(0)
    expect(items.every((i) => i.roles.includes('ADMIN'))).toBe(true)
  })
  it('retorna vazio quando role é nulo', () => {
    expect(getMenuForRole(null)).toEqual([])
  })
  it('inclui Perfil para todos os cargos', () => {
    const cargos = ['ADMIN', 'GERENTE', 'ATENDENTE', 'COZINHA']
    const perfil = baseMenu.find((m) => m.id === 'perfil')
    expect(perfil).toBeTruthy()
    cargos.forEach((c) => {
      expect(perfil?.roles.includes(c)).toBe(true)
    })
  })
})
