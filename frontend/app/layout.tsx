'use client'
import React from 'react'
import '../globals.css'
import { Shell } from '../src/components/layout/Shell'
import { QueryProvider } from '../src/providers/query'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <QueryProvider>
          <Shell>{children}</Shell>
        </QueryProvider>
      </body>
    </html>
  )
}


