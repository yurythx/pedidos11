'use client'

import React, { useEffect } from 'react'
import { Sidebar } from './Sidebar'
import { useAuthStore } from '../../features/auth/store'
import { useRouter, usePathname } from 'next/navigation'
import { request } from '../../lib/http/request'
import { CaixaStatus } from '../../features/financial/components/CaixaStatus'

import { Search, Command as CmdIcon, User as UserIcon, Package, UserPlus } from 'lucide-react'

export function Shell({ children }: { children: React.ReactNode }) {
  const { user, tokens, _hasHydrated } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const [showSearch, setShowSearch] = React.useState(false)

  const isAuthPage = pathname === '/login'
  const isPublicPage = pathname?.startsWith('/menu/') || isAuthPage

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setShowSearch(prev => !prev)
      }
      if (e.key === 'Escape') setShowSearch(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useEffect(() => {
    // Se ainda não hidratou o localStorage, não faz nada
    if (!_hasHydrated) return

    const bootstrap = async () => {
      // Se temos tokens mas não temos o objeto user, tentamos buscar
      if (!user && tokens.access && !isPublicPage) {
        try {
          const me = await request.get<any>('/usuarios/me/')
          useAuthStore.getState().setUser(me)
          return
        } catch (err) {
          console.error('Falha ao recuperar perfil:', err)
          useAuthStore.getState().logout()
        }
      }

      // Se após tentar (ou se não tinha token), ainda não temos user e não é página pública
      if (!useAuthStore.getState().user && !isPublicPage) {
        router.replace('/login')
        return
      }

      // Se o usuário JÁ está logado e tenta acessar o login, manda para a home
      if (useAuthStore.getState().user && isAuthPage) {
        router.replace('/')
      }
    }

    bootstrap()
  }, [_hasHydrated, user, tokens.access, router, isPublicPage])

  // Enquanto não hidratou, mostra um loading simples ou nada para evitar flash de tela de login
  if (!_hasHydrated) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (pathname?.startsWith('/menu/')) {
    return <>{children}</>
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {!isAuthPage && <Sidebar />}

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        {!isAuthPage && (
          <header className="h-14 border-b bg-white flex items-center justify-between px-6 shrink-0 z-10">
            <div
              className="group flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg cursor-pointer hover:bg-gray-200 transition-all border border-gray-200"
              onClick={() => setShowSearch(true)}
            >
              <Search size={16} className="text-gray-500" />
              <span className="text-sm text-gray-500">Buscar (Ctrl+K)</span>
              <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border bg-white px-1.5 font-mono text-[10px] font-medium text-gray-400">
                <span className="text-xs">⌘</span>K
              </kbd>
            </div>

            <div className="flex items-center gap-4">
              <CaixaStatus />
            </div>
          </header>
        )}

        <main className="flex-1 overflow-auto md:p-6 p-4 relative w-full">
          {children}
        </main>
      </div>

      {/* Global Command Palette Modal */}
      {showSearch && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4 backdrop-blur-sm bg-black/20 animate-in fade-in duration-200">
          <div className="absolute inset-0" onClick={() => setShowSearch(false)} />
          <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden relative animate-in zoom-in-95 duration-200">
            <div className="flex items-center gap-3 p-4 border-b">
              <Search className="w-5 h-5 text-gray-400" />
              <input
                autoFocus
                placeholder="O que você deseja buscar?"
                className="flex-1 outline-none text-lg text-gray-800 placeholder:text-gray-400"
                onChange={(e) => {
                  // Aqui você integraria com uma busca na API no futuro
                }}
              />
            </div>

            <div className="p-2 max-h-[60vh] overflow-auto">
              <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Ações Rápidas</div>
              <button onClick={() => { router.push('/vendas/nova'); setShowSearch(false); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 text-left transition-colors group">
                <Package className="w-5 h-5 text-blue-500" />
                <span className="font-medium text-gray-700">Nova Venda (PDV)</span>
                <span className="ml-auto text-xs text-gray-400 opacity-0 group-hover:opacity-100 italic">Ir para...</span>
              </button>
              <button onClick={() => { router.push('/clientes/novo'); setShowSearch(false); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 text-left transition-colors group">
                <UserPlus className="w-5 h-5 text-green-500" />
                <span className="font-medium text-gray-700">Cadastrar Cliente</span>
                <span className="ml-auto text-xs text-gray-400 opacity-0 group-hover:opacity-100 italic">Ir para...</span>
              </button>

              <div className="mt-2 px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Módulos</div>
              <button onClick={() => { router.push('/financeiro'); setShowSearch(false); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 text-left transition-colors group">
                <CmdIcon className="w-5 h-5 text-gray-500" />
                <span className="font-medium text-gray-700">Fluxo de Caixa</span>
              </button>
              <button onClick={() => { router.push('/perfil'); setShowSearch(false); }} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 text-left transition-colors group">
                <UserIcon className="w-5 h-5 text-gray-500" />
                <span className="font-medium text-gray-700">Configurações de Perfil</span>
              </button>
            </div>

            <div className="bg-gray-50 p-3 flex items-center justify-between text-[10px] text-gray-400 border-t">
              <div className="flex gap-4">
                <span><kbd className="border bg-white px-1 rounded">↑↓</kbd> Navegar</span>
                <span><kbd className="border bg-white px-1 rounded">Enter</kbd> Selecionar</span>
              </div>
              <div><kbd className="border bg-white px-1 rounded">ESC</kbd> para fechar</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

