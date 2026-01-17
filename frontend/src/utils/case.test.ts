import { describe, it, expect } from 'vitest'
import { toCamel, toSnake } from './case'

describe('case utils', () => {
  it('toCamel converts snake keys', () => {
    const input = { produto_id: 1, preco_venda: 10, itens: [{ quantidade_total: 2 }] }
    const out = toCamel(input)
    expect(out).toEqual({ produtoId: 1, precoVenda: 10, itens: [{ quantidadeTotal: 2 }] })
  })
  it('toSnake converts camel keys', () => {
    const input = { produtoId: 1, precoVenda: 10, itens: [{ quantidadeTotal: 2 }] }
    const out = toSnake(input)
    expect(out).toEqual({ produto_id: 1, preco_venda: 10, itens: [{ quantidade_total: 2 }] })
  })
})

