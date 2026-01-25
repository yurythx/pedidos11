import { z } from 'zod'

export const finalizarVendaSchema = z.object({
    forma_pagamento: z.enum(['DINHEIRO', 'CREDITO', 'DEBITO', 'PIX', 'BOLETO']),
    parcelas: z.number().min(1).max(12).optional(),
    valor_pago: z.number().min(0).optional(),
}).refine(
    (data) => {
        // Se for dinheiro, precisa do valor pago
        if (data.forma_pagamento === 'DINHEIRO' && !data.valor_pago) {
            return false
        }
        // Se for crédito, pode ter parcelas
        if (data.forma_pagamento === 'CREDITO' && data.parcelas && data.parcelas < 1) {
            return false
        }
        return true
    },
    {
        message: 'Dados de pagamento inválidos',
    }
)

export type FinalizarVendaFormData = z.infer<typeof finalizarVendaSchema>
