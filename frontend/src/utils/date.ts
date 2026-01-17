export const formatDate = (
  value: string | number | Date,
  options: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit', year: 'numeric' }
): string => {
  const d = value instanceof Date ? value : new Date(value)
  return new Intl.DateTimeFormat('pt-BR', options).format(d)
}

