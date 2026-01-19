export type MenuItem = {
  id: string
  label: string
  href: string
  roles: string[]
  icon: string
}

export const baseMenu: MenuItem[] = [
  { id: 'dashboard', label: 'Dashboard', href: '/', roles: ['ADMIN', 'GERENTE', 'ATENDENTE', 'COZINHA'], icon: 'LayoutDashboard' },
  { id: 'pdv', label: 'PDV', href: '/pos', roles: ['ADMIN', 'GERENTE', 'ATENDENTE'], icon: 'Store' },
  { id: 'kds', label: 'KDS', href: '/kds', roles: ['ADMIN', 'COZINHA'], icon: 'ChefHat' },
  { id: 'vendas', label: 'Vendas', href: '/vendas', roles: ['ADMIN', 'GERENTE', 'VENDEDOR', 'CAIXA'], icon: 'TrendingUp' },
  { id: 'compras', label: 'Compras & NFe', href: '/compras', roles: ['ADMIN', 'GERENTE'], icon: 'ShoppingCart' },
  { id: 'produtos', label: 'Produtos', href: '/produtos', roles: ['ADMIN', 'GERENTE'], icon: 'Package' },
  { id: 'clientes', label: 'Clientes', href: '/clientes', roles: ['ADMIN', 'GERENTE', 'ATENDENTE'], icon: 'Users' },
  { id: 'fornecedores', label: 'Fornecedores', href: '/fornecedores', roles: ['ADMIN', 'GERENTE'], icon: 'Truck' },
  { id: 'estoque', label: 'Gestão de Estoque', href: '/saldos', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'], icon: 'Warehouse' },
  // Agrupando visualmente no sidebar, mas mantendo rotas
  { id: 'movimentacoes', label: 'Movimentações', href: '/movimentacoes', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'], icon: 'ArrowLeftRight' },
  { id: 'lotes', label: 'Lotes', href: '/lotes', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'], icon: 'Boxes' },
  { id: 'depositos', label: 'Depósitos', href: '/depositos', roles: ['ADMIN', 'GERENTE', 'ESTOQUISTA'], icon: 'Container' },
  
  { id: 'usuarios', label: 'Usuários', href: '/usuarios', roles: ['ADMIN', 'GERENTE'], icon: 'UserCog' },
  { id: 'config', label: 'Configurações', href: '/config', roles: ['ADMIN'], icon: 'Settings' },
  { id: 'perfil', label: 'Perfil', href: '/perfil', roles: ['ADMIN', 'GERENTE', 'ATENDENTE', 'COZINHA'], icon: 'User' },
]

export const getMenuForRole = (role: string | null): MenuItem[] => {
  if (!role) return []
  return baseMenu.filter((item) => item.roles.includes(role))
}
