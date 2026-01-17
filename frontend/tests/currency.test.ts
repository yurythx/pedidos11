import { describe, it, expect } from 'vitest'
import { formatBRL } from '../src/utils/currency'

describe('formatBRL', () => {
  it('formata valores em BRL', () => {
    expect(formatBRL(0)).toContain('R$')
    expect(formatBRL(1234.56)).toContain('1.234,56')
  })
})
