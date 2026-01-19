'use client'
import React, { useEffect, useState } from 'react'
import { ProductGrid } from '../../src/features/pos/components/ProductGrid'
import { CartPanel } from '../../src/features/pos/components/CartPanel'
import { useCartStore } from '../../src/features/pos/cartStore'
import { ShoppingCart, X } from 'lucide-react'

export default function PosPage() {
  const { increment, decrement, clear, items } = useCartStore()
  const [showMobileCart, setShowMobileCart] = useState(false)

  // Total items for badge
  const totalItems = items.reduce((acc, item) => acc + item.quantity, 0)

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
    <div className="flex flex-col md:flex-row w-full h-[calc(100vh-6rem)] gap-4 relative">
      {/* Product Grid Area */}
      <div className="flex-1 overflow-hidden h-full">
        <ProductGrid />
      </div>

      {/* Desktop Cart Panel */}
      <div className="hidden md:block w-96 h-full">
        <CartPanel />
      </div>

      {/* Mobile Cart Toggle Button */}
      <button
        onClick={() => setShowMobileCart(true)}
        className="md:hidden fixed bottom-6 right-6 bg-primary text-white p-4 rounded-full shadow-lg z-30 flex items-center justify-center"
      >
        <ShoppingCart className="w-6 h-6" />
        {totalItems > 0 && (
          <span className="absolute -top-2 -right-2 bg-red-600 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center border-2 border-white">
            {totalItems}
          </span>
        )}
      </button>

      {/* Mobile Cart Overlay/Drawer */}
      {showMobileCart && (
        <div className="fixed inset-0 z-50 md:hidden flex flex-col bg-white animate-in slide-in-from-bottom duration-300">
          <div className="flex items-center justify-between p-4 border-b bg-gray-50">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <ShoppingCart className="w-5 h-5" />
              Carrinho ({totalItems})
            </h2>
            <button 
              onClick={() => setShowMobileCart(false)}
              className="p-2 bg-gray-200 rounded-full hover:bg-gray-300"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <CartPanel />
          </div>
        </div>
      )}
    </div>
  )
}

