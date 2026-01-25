import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { CartState, CartItem } from '../types'

export const useCartStore = create<CartState>()(
    persist(
        (set, get) => ({
            items: [],
            cliente: undefined,
            observacao: undefined,

            addItem: (produto, quantidade) => {
                const items = get().items
                const existingItem = items.find(item => item.produto.id === produto.id)

                if (existingItem) {
                    set({
                        items: items.map(item =>
                            item.produto.id === produto.id
                                ? { ...item, quantidade: item.quantidade + quantidade }
                                : item
                        ),
                    })
                } else {
                    set({
                        items: [
                            ...items,
                            {
                                produto: {
                                    id: produto.id,
                                    nome: produto.nome,
                                    preco_venda: produto.preco_venda,
                                    unidade_medida: produto.unidade_medida,
                                },
                                quantidade,
                                desconto: 0,
                            },
                        ],
                    })
                }
            },

            updateQuantity: (produtoId, quantidade) => {
                if (quantidade <= 0) {
                    get().removeItem(produtoId)
                    return
                }

                set({
                    items: get().items.map(item =>
                        item.produto.id === produtoId ? { ...item, quantidade } : item
                    ),
                })
            },

            updateDesconto: (produtoId, desconto) => {
                set({
                    items: get().items.map(item =>
                        item.produto.id === produtoId ? { ...item, desconto: Math.max(0, desconto) } : item
                    ),
                })
            },

            removeItem: (produtoId) => {
                set({
                    items: get().items.filter(item => item.produto.id !== produtoId),
                })
            },

            setCliente: (cliente) => {
                set({ cliente })
            },

            setObservacao: (observacao) => {
                set({ observacao })
            },

            clear: () => {
                set({
                    items: [],
                    cliente: undefined,
                    observacao: undefined,
                })
            },

            getSubtotal: () => {
                return get().items.reduce(
                    (sum, item) => sum + item.produto.preco_venda * item.quantidade,
                    0
                )
            },

            getDescontoTotal: () => {
                return get().items.reduce((sum, item) => sum + item.desconto, 0)
            },

            getTotal: () => {
                return get().getSubtotal() - get().getDescontoTotal()
            },
        }),
        {
            name: 'cart-storage',
        }
    )
)
