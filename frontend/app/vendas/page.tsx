'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../src/lib/http/request'
import type { Paginacao, Venda } from '../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TablePagination } from '../../src/components/ui/Table'
import { Plus, Search } from 'lucide-react'
import { formatBRL } from '../../src/utils/currency'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function VendasPage() {
  const router = useRouter()
  const [data, setData] = useState<Paginacao<Venda> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(20)

  const loadVendas = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await request.get<Paginacao<Venda>>(`/vendas/?page_size=${pageSize}&page=${page}`)
      setData(res)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao carregar vendas')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadVendas()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize])

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="heading-1">Vendas</h1>
        <Link href="/vendas/nova" className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Nova Venda
        </Link>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Carregando vendas...</div>}
      {error && <div className="p-4 bg-red-50 text-red-600 rounded-xl">{error}</div>}
      
      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Vendedor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Itens</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Emissão</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(data?.results ?? []).map((v) => (
                <TableRow 
                  key={v.id} 
                  onClick={() => router.push(`/vendas/${v.id}`)}
                  className="cursor-pointer hover:bg-gray-50 transition-colors"
                >
                  <TableCell><span className="font-mono font-medium text-blue-600">#{v.numero}</span></TableCell>
                  <TableCell>{v.cliente_nome ?? 'Balcão'}</TableCell>
                  <TableCell>{v.vendedor_nome ?? '-'}</TableCell>
                  <TableCell>
                    <span className={`
                      px-2 py-1 rounded-full text-xs font-bold
                      ${v.status === 'FINALIZADA' ? 'bg-green-100 text-green-700' : 
                        v.status === 'CANCELADA' ? 'bg-red-100 text-red-700' : 
                        'bg-blue-100 text-blue-700'}
                    `}>
                      {v.status}
                    </span>
                  </TableCell>
                  <TableCell>{v.quantidade_itens}</TableCell>
                  <TableCell className="font-medium">{formatBRL(v.total_liquido)}</TableCell>
                  <TableCell>{new Date(v.data_emissao).toLocaleDateString('pt-BR')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <TablePagination
            page={page}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
            hasMore={(data?.results?.length ?? 0) >= pageSize}
          />
        </>
      )}
    </div>
  )
}
