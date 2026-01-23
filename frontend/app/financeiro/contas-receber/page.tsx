'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  MoreHorizontal, 
  Eye, 
  Trash2,
  DollarSign,
  Calendar,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { PaymentModal, PaymentData } from '../../../src/components/financial/PaymentModal'
import { request } from '../../../src/lib/http/request'
import { ContaReceber, Paginacao, StatusConta } from '../../../src/types'
import { useRouter } from 'next/navigation'

export default function ContasReceberPage() {
  const router = useRouter()
  const [contas, setContas] = useState<ContaReceber[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedConta, setSelectedConta] = useState<ContaReceber | null>(null)
  const [pagination, setPagination] = useState<{
    count: number
    next: string | null
    previous: string | null
    current_page: number
    total_pages: number
  }>({
    count: 0,
    next: null,
    previous: null,
    current_page: 1,
    total_pages: 1
  })
  
  // Filtros
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [vencidasFilter, setVencidasFilter] = useState(false)

  const fetchContas = useCallback(async (page = 1) => {
    try {
      setLoading(true)
      let url = `/contas-receber/?page=${page}`
      
      if (statusFilter) {
        url += `&status=${statusFilter}`
      }
      
      if (vencidasFilter) {
        url += `&vencidas=true`
      }
      
      if (searchTerm) {
        url += `&search=${searchTerm}`
      }

      const response = await request(url)
      setContas(response.results)
      setPagination({
        count: response.count,
        next: response.next,
        previous: response.previous,
        current_page: page,
        total_pages: Math.ceil(response.count / 20) // Assumindo page_size 20
      })
    } catch (error) {
      console.error('Erro ao buscar contas a receber:', error)
    } finally {
      setLoading(false)
    }
  }, [statusFilter, vencidasFilter, searchTerm])

  useEffect(() => {
    fetchContas()
  }, [fetchContas])

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      fetchContas(newPage)
    }
  }

  const handleBaixarClick = (conta: ContaReceber) => {
    setSelectedConta(conta)
    setIsModalOpen(true)
  }

  const handleConfirmBaixa = async (data: PaymentData) => {
    if (!selectedConta) return

    try {
        await request.post(`/contas-receber/${selectedConta.id}/baixar/`, data)
        fetchContas(pagination.current_page)
        alert('Conta recebida com sucesso!')
    } catch (err: any) {
        alert(err?.message || 'Erro ao receber conta')
        throw err
    }
  }

  const getStatusBadge = (status: StatusConta, estaVencida: boolean) => {
    if (status === 'PAGA') {
      return <span className="badge badge-success gap-2"><CheckCircle className="w-3 h-3" /> Recebida</span>
    }
    if (status === 'CANCELADA') {
      return <span className="badge badge-ghost gap-2"><XCircle className="w-3 h-3" /> Cancelada</span>
    }
    if (estaVencida) {
      return <span className="badge badge-error gap-2"><AlertCircle className="w-3 h-3" /> Vencida</span>
    }
    return <span className="badge badge-warning gap-2"><Calendar className="w-3 h-3" /> Pendente</span>
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-base-content">Contas a Receber</h1>
          <p className="text-base-content/60">Gerencie seus recebimentos</p>
        </div>
        <div className="flex gap-2">
          <Link href="/financeiro/contas-receber/nova" className="btn btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Nova Conta
          </Link>
        </div>
      </div>

      {/* Filtros e Busca */}
      <div className="card bg-base-100 shadow-sm">
        <div className="card-body p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="form-control flex-1">
              <div className="input-group">
                <input
                  type="text"
                  placeholder="Buscar por descrição ou cliente..."
                  className="input input-bordered w-full"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button className="btn btn-square">
                  <Search className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0">
              <select 
                className="select select-bordered"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">Todos os Status</option>
                <option value="PENDENTE">Pendente</option>
                <option value="PAGA">Recebida</option>
                <option value="CANCELADA">Cancelada</option>
              </select>

              <button 
                className={`btn ${vencidasFilter ? 'btn-error' : 'btn-outline'}`}
                onClick={() => setVencidasFilter(!vencidasFilter)}
              >
                <AlertCircle className="w-4 h-4 mr-2" />
                Vencidas
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabela */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body p-0">
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Descrição / Cliente</th>
                  <th>Vencimento</th>
                  <th>Valor</th>
                  <th>Status</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8">
                      <span className="loading loading-spinner loading-lg text-primary"></span>
                    </td>
                  </tr>
                ) : contas.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-base-content/60">
                      Nenhuma conta encontrada.
                    </td>
                  </tr>
                ) : (
                  contas.map((conta) => (
                    <tr key={conta.id} className="hover">
                      <td>
                        <div className="flex flex-col">
                          <span className="font-medium">{conta.descricao}</span>
                          <span className="text-xs text-base-content/60">{conta.cliente_nome || 'Sem cliente'}</span>
                          {conta.venda_numero && (
                            <Link href={`/vendas/${conta.venda}`} className="text-xs text-primary hover:underline">
                              Venda #{conta.venda_numero}
                            </Link>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="flex flex-col">
                          <span>{formatDate(conta.data_vencimento)}</span>
                          {conta.dias_atraso > 0 && conta.status === 'PENDENTE' && (
                            <span className="text-xs text-error font-medium">{conta.dias_atraso} dias de atraso</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="flex flex-col">
                          <span className="font-bold">{formatCurrency(conta.valor_total)}</span>
                          {conta.valor_original !== conta.valor_total && (
                            <span className="text-xs text-base-content/60 line-through">
                              {formatCurrency(conta.valor_original)}
                            </span>
                          )}
                        </div>
                      </td>
                      <td>{getStatusBadge(conta.status, conta.esta_vencida)}</td>
                      <td>
                        <div className="dropdown dropdown-end">
                          <label tabIndex={0} className="btn btn-ghost btn-sm btn-square">
                            <MoreHorizontal className="w-4 h-4" />
                          </label>
                          <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                            <li>
                              <Link href={`/financeiro/contas-receber/${conta.id}`}>
                                <Eye className="w-4 h-4" />
                                Ver Detalhes
                              </Link>
                            </li>
                            {conta.status === 'PENDENTE' && (
                              <li>
                                <button 
                                    className="text-success"
                                    onClick={() => handleBaixarClick(conta)}
                                >
                                  <DollarSign className="w-4 h-4" />
                                  Baixar (Receber)
                                </button>
                              </li>
                            )}
                          </ul>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Paginação */}
      <div className="flex justify-center mt-4">
        <div className="join">
          <button 
            className="join-item btn"
            disabled={!pagination.previous}
            onClick={() => handlePageChange(pagination.current_page - 1)}
          >
            «
          </button>
          <button className="join-item btn">
            Página {pagination.current_page} de {pagination.total_pages}
          </button>
          <button 
            className="join-item btn"
            disabled={!pagination.next}
            onClick={() => handlePageChange(pagination.current_page + 1)}
          >
            »
          </button>
        </div>
      </div>

      <PaymentModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirmBaixa}
        valorOriginal={selectedConta?.valor_original || 0}
        tipo="RECEBER"
      />
    </div>
  )
}
