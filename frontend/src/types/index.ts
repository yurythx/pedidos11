export type UUID = string

export type TipoProduto = 'COMUM' | 'COMPOSTO' | 'INSUMO'

export interface Empresa {
  id: number
  nome: string
  cnpj: string
  ativo: boolean
}

export interface Usuario {
  id: string
  username: string
  email: string | null
  first_name: string | null
  last_name: string | null
  cargo: string
  empresa_id: string
  is_active: boolean
}

export interface Produto {
  id: number
  nome: string
  sku: string | null
  tipo: TipoProduto
  preco_venda: number
  preco_custo: number | null
  unidade: string
  ativo: boolean
}

export interface Mesa {
  id: number
  numero: string
  status: 'LIVRE' | 'OCUPADA'
}

export interface Pedido {
  id: number
  codigo: string
  mesa_id: number | null
  cliente_id: number | null
  total_bruto: number
  desconto: number
  total_liquido: number
  status: 'ABERTO' | 'PAGO' | 'CANCELADO'
  created_at: string
}

export interface ItemPedido {
  id: number
  pedido_id: number
  produto_id: number
  quantidade: number
  preco_unitario: number
  subtotal: number
}

export interface Cliente {
  id: string
  nome: string
  cpf_cnpj?: string | null
  email: string | null
  telefone: string | null
  endereco_json: Record<string, unknown> | null
}

export interface Fornecedor {
  id: string
  nome: string
  cpf_cnpj?: string | null
  email: string | null
  telefone: string | null
  endereco_json: Record<string, unknown> | null
}

export interface Lote {
  id: number
  produto_id: number
  quantidade: number
  validade: string | null
}

export interface NFeItem {
  id: number
  nfe_id: number
  descricao: string
  quantidade: number
  unidade: string
  valor_unitario: number
  produto_sugerido_id: number | null
}

export interface ConfiguracoesTenant {
  tema_cor_primaria: string | null
  permitir_conta_parcial: boolean
  kds_modo: 'KANBAN' | 'GRID'
  custom_json: Record<string, unknown> | null
}

export interface Paginacao<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type VendaSnapshotItem = {
  produto_id: number
  quantidade: number
}

export interface LoginResponse {
  access: string
  refresh: string
  user: Usuario
}

