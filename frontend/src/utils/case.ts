const snakeToCamelStr = (str: string) =>
  str.replace(/_([a-z])/g, (_, c) => c.toUpperCase())

const camelToSnakeStr = (str: string) =>
  str.replace(/([A-Z])/g, '_$1').toLowerCase()

const isObject = (val: unknown): val is Record<string, unknown> =>
  !!val && typeof val === 'object' && !Array.isArray(val)

export const toCamel = <T = any>(input: any): T => {
  if (Array.isArray(input)) return input.map((v) => toCamel(v)) as any
  if (!isObject(input)) return input
  const out: Record<string, unknown> = {}
  Object.keys(input).forEach((k) => {
    const v = (input as any)[k]
    const nk = snakeToCamelStr(k)
    out[nk] = toCamel(v)
  })
  return out as T
}

export const toSnake = <T = any>(input: any): T => {
  if (Array.isArray(input)) return input.map((v) => toSnake(v)) as any
  if (!isObject(input)) return input
  const out: Record<string, unknown> = {}
  Object.keys(input).forEach((k) => {
    const v = (input as any)[k]
    const nk = camelToSnakeStr(k)
    out[nk] = toSnake(v)
  })
  return out as T
}

