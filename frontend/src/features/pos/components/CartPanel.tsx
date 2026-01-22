'use client'
import { CartPanelBalcao } from './CartPanelBalcao'
import { CartPanelMesa } from './CartPanelMesa'

// Wrapper simples de retrocompatibilidade até refatorarmos o PosPage
export function CartPanel() {
  const { mesaId } = useCartStore()
  
  if (mesaId) {
    return <CartPanelMesa />
  }
  return <CartPanelBalcao />
}

