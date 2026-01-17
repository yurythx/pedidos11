import { describe, it, expect } from 'vitest'
import { useCartStore } from './cartStore'

describe('cartStore', () => {
  it('adds and snapshots items', () => {
    const produto = { id: 5, nome: 'Teste', preco_venda: 10, tipo: 'COMUM' } as any
    useCartStore.getState().clear()
    useCartStore.getState().addItem(produto)
    useCartStore.getState().addItem(produto)
    const snap = useCartStore.getState().snapshot()
    expect(snap).toEqual([{ produto_id: 5, quantidade: 2 }])
    const subtotal = useCartStore.getState().subtotal()
    expect(subtotal).toBe(20)
  })
})

