'use client'

import React from 'react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import ReactDOMServer from 'react-dom/server'
import { Shell } from './Shell'
import { useAuthStore } from '../../features/auth/store'

let mockPathname = '/login'

vi.mock('next/navigation', () => {
  return {
    useRouter: () => ({ replace: vi.fn() }),
    usePathname: () => mockPathname
  }
})

describe('Shell', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      tokens: { access: null, refresh: null },
      tenantId: null
    })
    mockPathname = '/login'
  })

  it('não renderiza Sidebar em /login', () => {
    const html = ReactDOMServer.renderToString(
      <Shell>
        <div>Conteúdo</div>
      </Shell>
    )
    expect(html).not.toContain('Nix ERP')
  })

  it('renderiza Sidebar em rotas protegidas', () => {
    mockPathname = '/pos'
    const html = ReactDOMServer.renderToString(
      <Shell>
        <div>Conteúdo</div>
      </Shell>
    )
    expect(html).toContain('Nix ERP')
  })
})

