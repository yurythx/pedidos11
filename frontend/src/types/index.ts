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
  telefone: string | null
  is_active: boolean
  is_colaborador?: boolean
  role_atendente?: boolean
  role_caixa?: boolean
  comissao_percentual?: string
}

export interface Produto {
  id: string
  nome: string
  sku: string | null
  codigo_barras?: string | null
  tipo: TipoProduto
  tipo_display?: string
  categoria?: string | null
  categoria_nome?: string | null
  preco_venda: number
  preco_custo: number | null
  unidade: string
  ativo: boolean
  is_active?: boolean
  destaque?: boolean
}

export interface Mesa {
  id: string
  numero: string
  status: 'LIVRE' | 'OCUPADA' | 'SUJA' | 'RESERVADA'
  capacidade?: number
  venda_atual?: string | null
  venda_numero?: number | null
  total_conta?: string
  observacoes?: string
}

export interface Comanda {
  id: string
  codigo: string
  status: 'LIVRE' | 'EM_USO' | 'BLOQUEADA'
  venda_atual?: string | null
  venda_numero?: number | null
  observacoes?: string
}

export interface Pedido {
  id: number
  codigo: string
  mesa_id: string | null
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
  nome_fantasia?: string
  cpf_cnpj?: string | null
  rg_ie?: string | null
  email: string | null
  telefone: string | null
  celular?: string | null
  tipo_pessoa?: string
  observacoes?: string
  endereco_json: Record<string, unknown> | null
}

export interface Fornecedor {
  id: string
  razao_social: string
  nome_fantasia?: string
  nome?: string // Alias for compatibility
  nome_exibicao?: string
  cpf_cnpj?: string | null
  inscricao_estadual?: string | null
  email: string | null
  telefone: string | null
  contato_nome?: string | null
  tipo_pessoa?: string
  observacoes?: string
  endereco_json: Record<string, unknown> | null
}

export interface Lote {
  id: string
  codigo_lote: string
  produto_nome: string
  deposito_nome: string
  data_validade: string | null
  quantidade_atual: number
  dias_ate_vencer: number | null
  status_validade: string | null
  // Detail fields
  produto?: string
  deposito?: string
  data_fabricacao?: string | null
  observacao?: string
  percentual_consumido?: number
  created_at?: string
  updated_at?: string
}

export interface ConfiguracoesTenant {
  tema_cor_primaria: string | null
  permitir_conta_parcial: boolean
  kds_modo: 'KANBAN' | 'GRID'
  custom_json: Record<string, unknown> | null
}

export interface Movimentacao {
  id: string
  produto: string
  produto_nome: string
  deposito: string
  deposito_nome: string
  lote: string | null
  lote_codigo: string | null
  tipo: 'ENTRADA' | 'SAIDA' | 'BALANCO' | 'TRANSFERENCIA' | 'AJUSTE'
  quantidade: number
  valor_unitario: number
  valor_total: number
  documento: string
  observacao: string
  usuario: string
  created_at: string
}

export interface Venda {
  id: string
  numero: string
  cliente: string | null
  cliente_nome: string | null
  vendedor: string
  vendedor_nome: string | null
  status: 'ABERTA' | 'FINALIZADA' | 'CANCELADA'
  total_liquido: number
  quantidade_itens: number
  data_emissao: string
  data_finalizacao?: string | null
}

export interface ItemVenda {
  id: string
  produto: string
  produto_nome: string
  quantidade: number
  preco_unitario: number
  desconto: number
  subtotal: number
}

export interface VendaDetail extends Venda {
  itens: ItemVenda[]
}

export interface Paginacao<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type VendaSnapshotItem = {
  produto_id: string
  quantidade: number
  observacoes?: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: Usuario
}

export interface NFePreviewItem {
  codigo_xml: string
  descricao_xml: string
  unidade_xml?: string
  produto_sugerido_id?: string | null
  fator_conversao_sugerido?: number
  sugestoes_produtos?: Array<{
    produto_id: string
    nome: string
    fator_conversao?: number
  }>
  // Dados extras para o form
  produto_id?: string | null
  fator_conversao?: number
  qtd_xml?: number
  preco_custo?: number
  lote_codigo?: string
  lote_validade?: string
  lote_fabricacao?: string
}

export interface NFePreview {
  fornecedor: { cnpj: string; nome: string }
  numero_nfe: string
  serie_nfe: string
  itens: NFePreviewItem[]
}

export type StatusConta = 'PENDENTE' | 'PAGA' | 'CANCELADA' | 'VENCIDA'
export type TipoPagamento = 'DINHEIRO' | 'PIX' | 'CARTAO_DEBITO' | 'CARTAO_CREDITO' | 'BOLETO' | 'TRANSFERENCIA' | 'CHEQUE'

export interface ContaReceber {
  id: string
  venda: string | null
  venda_numero: number | null
  cliente: string | null
  cliente_nome: string | null
  descricao: string
  valor_original: number
  valor_juros: number
  valor_multa: number
  valor_desconto: number
  valor_total: number
  data_emissao: string
  data_vencimento: string
  data_pagamento: string | null
  status: StatusConta
  tipo_pagamento: TipoPagamento
  observacoes: string
  esta_vencida: boolean
  dias_atraso: number
  created_at: string
}

export type StatusProducao = 'PENDENTE' | 'EM_PREPARO' | 'PRONTO' | 'ENTREGUE'

export interface ProducaoItem {
  id: string
  produto_nome: string
  quantidade: number
  observacoes: string
  status_producao: StatusProducao
  venda_numero: number
  mesa_numero: string | null
  comanda_codigo: string | null
  setor_nome: string | null
  complementos_texto: string[]
  hora_pedido: string
}

export interface ContaPagar {
  id: string
  fornecedor: string | null
  fornecedor_nome: string | null
  descricao: string
  categoria: string
  numero_documento: string
  valor_original: number
  valor_juros: number
  valor_multa: number
  valor_desconto: number
  valor_total: number
  data_emissao: string
  data_vencimento: string
  data_pagamento: string | null
  status: StatusConta
  tipo_pagamento: TipoPagamento
  observacoes: string
  esta_vencida: boolean
  dias_atraso: number
  created_at: string
}
