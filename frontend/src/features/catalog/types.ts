export enum TipoProduto {
  SIMPLES = 'SIMPLES',
  COMPOSTO = 'COMPOSTO',
  MATERIA_PRIMA = 'MATERIA_PRIMA'
}

export enum UnidadeMedida {
  UN = 'UN',
  KG = 'KG',
  L = 'L',
  CX = 'CX'
}

export interface Categoria {
  id: string
  nome: string
  descricao?: string
  ativo: boolean
  ordem: number
  created_at: string
}

export interface Produto {
  id: string
  nome: string
  descricao?: string
  tipo: TipoProduto
  categoria: Categoria
  preco_custo?: number
  preco_venda: number
  margem_lucro?: number
  unidade_medida: UnidadeMedida
  codigo_barras?: string
  sku?: string
  ativo: boolean
  estoque_minimo?: number
  estoque_maximo?: number
  foto?: string
  created_at: string
  updated_at: string
}

export interface FichaTecnicaItem {
  id: string
  produto_pai: string
  produto_filho: Produto
  quantidade: number
  custo_unitario: number
  custo_total: number
  created_at: string
}

export interface CreateProdutoDTO {
  nome: string
  descricao?: string
  tipo: TipoProduto
  categoria_id: string
  preco_custo?: number
  preco_venda: number
  unidade_medida: UnidadeMedida
  codigo_barras?: string
  sku?: string
  ativo?: boolean
  estoque_minimo?: number
  estoque_maximo?: number
}

export interface ProductFilters {
  search?: string
  categoria_id?: string
  tipo?: TipoProduto
  preco_min?: number
  preco_max?: number
  ativo?: boolean
  ordering?: string
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  page_size: number
  total_pages: number
  current_page: number
  results: T[]
}
