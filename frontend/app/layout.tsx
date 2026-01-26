'use client'
import React from 'react'
import '../globals.css'
import { Shell } from '../src/components/layout/Shell'
import { QueryProvider } from '../src/providers/query'

import { Toaster } from 'sonner'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  React.useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => console.log('SW Registered', reg))
        .catch((err) => console.log('SW Error', err));
    }
  }, []);

  return (
    <html lang="pt-BR">
      <head>
        <link rel="manifest" href="/manifest.webmanifest" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Nix ERP" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
      </head>
      <body>
        <QueryProvider>
          <Toaster position="top-right" richColors closeButton />
          <Shell>{children}</Shell>
        </QueryProvider>
      </body>
    </html>
  )
}


