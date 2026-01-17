export type MenuItem = {
  id: string
  label: string
  href: string
  roles: string[]
}

export const baseMenu: MenuItem[] = [
  { id: 'dashboard', label: 'Dashboard', href: '/', roles: ['ADMIN', 'GERENTE', 'ATENDENTE', 'COZINHA'] },
  { id: 'pdv', label: 'PDV', href: '/pos', roles: ['ADMIN', 'GERENTE', 'ATENDENTE'] },
  { id: 'kds', label: 'KDS', href: '/kds', roles: ['ADMIN', 'COZINHA'] },
  { id: 'compras', label: 'Compras & NFe', href: '/compras', roles: ['ADMIN', 'GERENTE'] },
  { id: 'vendas', label: 'Vendas', href: '/vendas', roles: ['ADMIN', 'GERENTE', 'VENDEDOR', 'CAIXA'] },
  { id: 'produtos', label: 'Produtos', href: '/produtos', roles: ['ADMIN', 'GERENTE'] },
  { id: 'clientes', label: 'Clientes', href: '/clientes', roles: ['ADMIN', 'GERENTE', 'ATENDENTE'] },
  { id: 'fornecedores', label: 'Fornecedores', href: '/fornecedores', roles: ['ADMIN', 'GERENTE'] },
  { id: 'config', label: 'Configurações', href: '/config', roles: ['ADMIN'] },
  { id: 'usuarios', label: 'Usuários', href: '/usuarios', roles: ['ADMIN', 'GERENTE'] },
  { id: 'perfil', label: 'Perfil', href: '/perfil', roles: ['ADMIN', 'GERENTE', 'ATENDENTE', 'COZINHA'] },
  { id: 'depositos', label: 'Depósitos', href: '/depositos', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'] },
  { id: 'saldos', label: 'Saldos', href: '/saldos', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'] },
  { id: 'lotes', label: 'Lotes', href: '/lotes', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'] },
  { id: 'movimentacoes', label: 'Movimentações', href: '/movimentacoes', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'] },
]

export const getMenuForRole = (role: string | null): MenuItem[] => {
  if (!role) return []
  return baseMenu.filter((item) => item.roles.includes(role))
}

