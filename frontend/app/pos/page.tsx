'use client'
import React, { useEffect } from 'react'
import { ProductGrid } from '../../src/features/pos/components/ProductGrid'
import { CartPanel } from '../../src/features/pos/components/CartPanel'
import { useCartStore } from '../../src/features/pos/cartStore'

export default function PosPage() {
  const { increment, decrement, clear } = useCartStore()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === '+') increment(Number.NaN)
      if (e.key === '-') decrement(Number.NaN)
      if (e.key === 'Escape') clear()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [increment, decrement, clear])

  return (
    <div className="flex w-full p-4 gap-4">
      <ProductGrid />
      <CartPanel />
    </div>
  )
}

