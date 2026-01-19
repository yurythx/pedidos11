'use client'

import React, { useMemo, useState } from 'react'
import { useAuthStore } from '../../features/auth/store'
import { getMenuForRole } from '../../features/rbac/menu'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { 
  LayoutDashboard, 
  Store, 
  ChefHat, 
  TrendingUp, 
  ShoppingCart, 
  Package, 
  Users, 
  Truck, 
  Warehouse, 
  ArrowLeftRight, 
  Boxes, 
  Container, 
  UserCog, 
  Settings, 
  User, 
  LogOut, 
  ChevronLeft, 
  ChevronRight 
} from 'lucide-react'

// Map string names to components
const IconMap: Record<string, React.ElementType> = {
  'LayoutDashboard': LayoutDashboard,
  'Store': Store,
  'ChefHat': ChefHat,
  'TrendingUp': TrendingUp,
  'ShoppingCart': ShoppingCart,
  'Package': Package,
  'Users': Users,
  'Truck': Truck,
  'Warehouse': Warehouse,
  'ArrowLeftRight': ArrowLeftRight,
  'Boxes': Boxes,
  'Container': Container,
  'UserCog': UserCog,
  'Settings': Settings,
  'User': User
}

export function Sidebar() {
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)
  const menu = useMemo(() => getMenuForRole(user?.cargo ?? null), [user])
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  // Mobile menu control
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Close mobile menu on route change
  React.useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [pathname])

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setIsMobileMenuOpen(true)}
        className="fixed top-4 left-4 z-30 p-2 bg-white rounded-lg shadow-md md:hidden text-gray-600 hover:text-primary"
      >
        <Store className="w-6 h-6" />
      </button>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      <aside 
        className={`
          bg-white border-r border-gray-100 flex flex-col transition-all duration-300 shadow-sm z-50
          fixed md:relative h-full
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          ${collapsed ? 'md:w-20' : 'md:w-72'}
          w-72
        `}
      >
        {/* Header / Logo */}
        <div className="h-20 flex items-center justify-between px-6 border-b border-gray-50">
          {(!collapsed || isMobileMenuOpen) && (
            <div className="flex items-center gap-2 text-primary">
              <Store className="w-8 h-8" />
              <span className="text-xl font-bold tracking-tight">Nix Food</span>
            </div>
          )}
          {collapsed && !isMobileMenuOpen && (
            <div className="mx-auto text-primary">
              <Store className="w-8 h-8" />
            </div>
          )}
          
          {/* Desktop Collapse Button */}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className={`
              p-1.5 rounded-full bg-gray-50 text-gray-400 hover:text-primary hover:bg-red-50 transition-colors
              hidden md:block
              ${collapsed ? 'hidden' : 'block'}
            `}
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

           {/* Mobile Close Button */}
           <button
            onClick={() => setIsMobileMenuOpen(false)}
            className="md:hidden p-1.5 rounded-full bg-gray-50 text-gray-400 hover:text-primary"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1 custom-scrollbar">
          {menu.map((item) => {
            const Icon = IconMap[item.icon] || LayoutDashboard
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
            
            return (
              <Link 
                key={item.id} 
                href={item.href} 
                className={`
                  flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group
                  ${isActive 
                    ? 'bg-primary text-white shadow-md shadow-red-200' 
                    : 'text-gray-600 hover:bg-red-50 hover:text-primary'
                  }
                  ${collapsed && !isMobileMenuOpen ? 'justify-center' : ''}
                `}
                title={collapsed ? item.label : undefined}
              >
                <Icon 
                  className={`
                    ${collapsed && !isMobileMenuOpen ? 'w-6 h-6' : 'w-5 h-5'} 
                    ${isActive ? 'text-white' : 'text-gray-400 group-hover:text-primary'}
                    transition-colors
                  `} 
                />
                
                {(!collapsed || isMobileMenuOpen) && (
                  <span className="font-medium text-sm">{item.label}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* User / Logout */}
        <div className="p-4 border-t border-gray-50 bg-gray-50/50">
          <div className={`flex items-center ${collapsed && !isMobileMenuOpen ? 'justify-center' : 'justify-between'}`}>
            {(!collapsed || isMobileMenuOpen) && (
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                  {user?.first_name?.[0] || 'U'}
                </div>
                <div className="flex flex-col truncate">
                  <span className="text-sm font-semibold text-gray-900 truncate">
                    {user?.first_name || 'Usuário'}
                  </span>
                  <span className="text-xs text-gray-500 truncate">
                    {user?.cargo || 'Cargo'}
                  </span>
                </div>
              </div>
            )}
            
            <button 
              onClick={handleLogout}
              className={`
                p-2 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors
                ${collapsed && !isMobileMenuOpen ? '' : 'ml-2'}
              `}
              title="Sair"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>
    </>
  )
}
