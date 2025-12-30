export type TokenPair = { access: string; refresh: string };
export type Categoria = { nome: string; slug: string };
export type Produto = {
  nome: string;
  slug: string;
  sku?: string;
  ean?: string;
  unidade?: string;
  marca?: string;
  ncm?: string;
  cfop?: string;
  atributos?: Record<string, unknown>;
  categoria: string;
  categoria_nome?: string;
  preco: string | number;
  custo?: string | number;
  descricao?: string;
  imagem?: string | null;
  disponivel: boolean;
};
export type ItemPedidoRead = {
  produto_nome: string;
  produto_slug: string;
  quantidade: number;
  preco_unitario: string | number;
};
export type Pedido = {
  slug: string;
  status: string;
  total: string | number;
  data_criacao: string;
  itens: ItemPedidoRead[];
  cost_center_codigo?: string | null;
  cost_center_nome?: string | null;
};
export type Dashboard = {
  total_pedidos: number;
  pedidos_por_status: Record<string, number>;
  faturamento_total: string;
  faturamento_avista: string;
  faturamento_prazo: string;
  ar_outstanding: string;
  saldo_estoque_total: number;
};
export const login = async (baseUrl: string, username: string, password: string): Promise<TokenPair> => {
  const r = await fetch(`${baseUrl}/api/v1/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!r.ok) throw new Error("Auth failed");
  return r.json();
};
export const refresh = async (baseUrl: string, token: string): Promise<TokenPair> => {
  const r = await fetch(`${baseUrl}/api/v1/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: token })
  });
  if (!r.ok) throw new Error("Refresh failed");
  return r.json();
};
export const listProdutos = async (baseUrl: string, token: string, params?: Record<string, string>): Promise<Produto[]> => {
  const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
  const r = await fetch(`${baseUrl}/api/v1/catalogo/produtos${qs}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Fetch produtos failed");
  return r.json();
};
export const getProduto = async (baseUrl: string, token: string, slug: string): Promise<Produto> => {
  const r = await fetch(`${baseUrl}/api/v1/catalogo/produtos/${slug}/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Fetch produto failed");
  return r.json();
};
export const listCategorias = async (baseUrl: string, token: string): Promise<Categoria[]> => {
  const r = await fetch(`${baseUrl}/api/v1/catalogo/categorias/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Fetch categorias failed");
  return r.json();
};
export const listCategoriaProdutos = async (baseUrl: string, token: string, slug: string): Promise<Produto[]> => {
  const r = await fetch(`${baseUrl}/api/v1/catalogo/categorias/${slug}/produtos/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Fetch categoria produtos failed");
  return r.json();
};
export const criarPedido = async (
  baseUrl: string,
  token: string,
  itens: { produto: string; quantidade: number }[],
  costCenter?: string
): Promise<Pedido> => {
  const r = await fetch(`${baseUrl}/api/v1/vendas/pedidos/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      "Idempotency-Key": crypto.randomUUID()
    },
    body: JSON.stringify({ itens_payload: itens, cost_center: costCenter })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};
export const relatoriosDashboard = async (baseUrl: string, token: string, params?: Record<string, string>): Promise<Dashboard> => {
  const qs = params ? `?${new URLSearchParams(params).toString()}` : "";
  const r = await fetch(`${baseUrl}/api/v1/relatorios/relatorios/dashboard${qs}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Fetch dashboard failed");
  return r.json();
};
