const brFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

export const formatBRL = (value: number): string => brFormatter.format(value)

