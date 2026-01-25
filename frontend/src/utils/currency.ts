export function formatBRL(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

export function parseBRL(value: string): number {
  // Remove "R$", espaços e pontos, troca vírgula por ponto
  const cleaned = value
    .replace('R$', '')
    .replace(/\s/g, '')
    .replace(/\./g, '')
    .replace(',', '.')

  return parseFloat(cleaned) || 0
}
