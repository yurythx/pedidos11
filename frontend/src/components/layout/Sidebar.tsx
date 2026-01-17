'use client'

import React, { useMemo, useState } from 'react'
import { useAuthStore } from '../../features/auth/store'
import { getMenuForRole } from '../../features/rbac/menu'
import Link from 'next/link'

export function Sidebar() {
  const { user } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)
  const menu = useMemo(() => getMenuForRole(user?.cargo ?? null), [user])

  return (
    <aside className={`h-screen border-r ${collapsed ? 'w-16' : 'w-64'}`}>
      <div className="flex items-center justify-between p-3">
        <span className="font-semibold">{collapsed ? 'N' : 'Nix ERP'}</span>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="text-sm px-2 py-1 border rounded"
          aria-label="Alternar sidebar"
        >
          {collapsed ? '>' : '<'}
        </button>
      </div>
      <nav className="mt-2">
        {menu.map((item) => (
          <Link key={item.id} href={item.href} className="block px-3 py-2 hover:bg-gray-100">
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

