'use client'

import React, { useEffect } from 'react'
import { Sidebar } from './Sidebar'
import { useAuthStore } from '../../features/auth/store'
import { useRouter, usePathname } from 'next/navigation'
import { request } from '../../lib/http/request'

export function Shell({ children }: { children: React.ReactNode }) {
  const { user, tokens } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const isAuthPage = pathname === '/login'

  useEffect(() => {
    const bootstrap = async () => {
      if (!user && tokens.access && !isAuthPage) {
        try {
          const me = await request.get<any>('/usuarios/me/')
          useAuthStore.getState().setUser(me)
          return
        } catch {
          useAuthStore.getState().logout()
        }
      }
      if (!useAuthStore.getState().user && !isAuthPage) {
        router.replace('/login')
      }
    }
    bootstrap()
  }, [user, tokens, router, isAuthPage])

  return (
    <div className="flex">
      {!isAuthPage && <Sidebar />}
      <main className="flex-1 min-h-screen">{children}</main>
    </div>
  )
}

