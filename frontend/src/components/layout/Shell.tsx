'use client'

import React, { useEffect } from 'react'
import { Sidebar } from './Sidebar'
import { useAuthStore } from '../../features/auth/store'
import { useRouter, usePathname } from 'next/navigation'
import { request } from '../../lib/http/request'
import { CaixaStatus } from '../../features/financial/components/CaixaStatus'

export function Shell({ children }: { children: React.ReactNode }) {
  const { user, tokens } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const isAuthPage = pathname === '/login'
  const isPublicPage = pathname?.startsWith('/menu/') || isAuthPage

  useEffect(() => {
    const bootstrap = async () => {
      if (!user && tokens.access && !isPublicPage) {
        try {
          const me = await request.get<any>('/usuarios/me/')
          useAuthStore.getState().setUser(me)
          return
        } catch {
          useAuthStore.getState().logout()
        }
      }
      if (!useAuthStore.getState().user && !isPublicPage) {
        router.replace('/login')
      }
    }
    bootstrap()
  }, [user, tokens, router, isPublicPage])

  if (pathname?.startsWith('/menu/')) {
    return <>{children}</>
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {!isAuthPage && <Sidebar />}
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header para Status do Caixa e Perfil */}
        {!isAuthPage && (
          <header className="h-14 border-b bg-white flex items-center justify-between px-6 shrink-0 z-10">
            <div className="text-sm font-medium text-gray-500">
               {/* Breadcrumb ou Título da Página poderia vir aqui */}
               Projeto Nix
            </div>
            <div className="flex items-center gap-4">
              <CaixaStatus />
              {/* Outros itens de header como Notificações ou Avatar User */}
            </div>
          </header>
        )}

        <main className="flex-1 overflow-auto md:p-6 p-4 relative w-full">
          {children}
        </main>
      </div>
    </div>
  )
}

