import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  FileText, 
  Send, 
  Download, 
  RefreshCw,
  Search,
  AlertCircle,
  CheckCircle,
  XCircle,
  Settings
} from 'lucide-react'
import Link from 'next/link'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow,
  TablePagination 
} from '../../../components/ui/Table'
import { nfeService } from '../services/nfeService'
import { NFe } from '../types'
import { formatBRL as formatCurrency } from '../../../utils/currency'
import { formatDate } from '../../../utils/date'

const StatusBadge = ({ status }: { status: NFe['status'] }) => {
  const styles = {
    DIGITACAO: 'bg-gray-100 text-gray-700',
    VALIDADA: 'bg-blue-100 text-blue-700',
    ASSINADA: 'bg-indigo-100 text-indigo-700',
    TRANSMITIDA: 'bg-yellow-100 text-yellow-700',
    AUTORIZADA: 'bg-green-100 text-green-700',
    REJEITADA: 'bg-red-100 text-red-700',
    CANCELADA: 'bg-red-100 text-red-700',
    DENEGADA: 'bg-orange-100 text-orange-700'
  }

  const labels = {
    DIGITACAO: 'Em Digitação',
    VALIDADA: 'Validada',
    ASSINADA: 'Assinada',
    TRANSMITIDA: 'Transmitida',
    AUTORIZADA: 'Autorizada',
    REJEITADA: 'Rejeitada',
    CANCELADA: 'Cancelada',
    DENEGADA: 'Denegada'
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.DIGITACAO}`}>
      {labels[status] || status}
    </span>
  )
}

export function NFeList() {
  const queryClient = useQueryClient()
  const [page, setPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(10)

  const { data: response, isLoading } = useQuery({
    queryKey: ['nfes', page, pageSize],
    queryFn: () => nfeService.list({ page, page_size: pageSize }) 
  })

  // Safe access to results array (API returns { results: [], count: ... })
  const nfes = Array.isArray(response) ? response : (response?.results || [])

  const transmitirMutation = useMutation({
    mutationFn: nfeService.transmitir,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nfes'] })
      alert('NFe transmitida com sucesso!')
    },
    onError: (error: any) => {
      alert(`Erro ao transmitir: ${error.message}`)
    }
  })

  const gerarXmlMutation = useMutation({
    mutationFn: nfeService.gerarXml,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nfes'] })
      alert('XML gerado com sucesso!')
    },
    onError: (error: any) => {
      alert(`Erro ao gerar XML: ${error.message}`)
    }
  })

  const handleTransmitir = (id: string) => {
    if (confirm('Deseja transmitir esta NFe para a SEFAZ?')) {
      transmitirMutation.mutate(id)
    }
  }

  const handleGerarXml = (id: string) => {
    gerarXmlMutation.mutate(id)
  }

  const handleDownloadXml = (xml: string, chave: string) => {
    const blob = new Blob([xml], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${chave}-nfe.xml`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Carregando notas fiscais...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Emissão de NFe</h1>
        <div className="flex gap-2">
          <Link href="/nfe/config" className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200">
            <Settings className="w-4 h-4" />
            Configurar
          </Link>
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Número/Série</TableHead>
            <TableHead>Emissão</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Valor</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {nfes?.map((nfe) => (
            <TableRow key={nfe.id}>
              <TableCell>
                <div className="font-medium">{nfe.numero}</div>
                <div className="text-xs text-gray-500">Série {nfe.serie}</div>
              </TableCell>
              <TableCell>{formatDate(nfe.data_emissao)}</TableCell>
              <TableCell>
                <div className="font-medium">{nfe.cliente.nome}</div>
                <div className="text-xs text-gray-500">{nfe.cliente.cpf_cnpj}</div>
              </TableCell>
              <TableCell>{formatCurrency(Number(nfe.valor_total_nota))}</TableCell>
              <TableCell>
                <StatusBadge status={nfe.status} />
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {/* Gerar XML */}
                  {!nfe.xml_envio && (
                    <button
                      onClick={() => handleGerarXml(nfe.id)}
                      className="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
                      title="Gerar XML"
                    >
                      <FileText className="w-4 h-4" />
                    </button>
                  )}

                  {/* Transmitir */}
                  {['VALIDADA', 'ASSINADA', 'REJEITADA'].includes(nfe.status) && nfe.xml_envio && (
                    <button
                      onClick={() => handleTransmitir(nfe.id)}
                      className="p-1 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded"
                      title="Transmitir para SEFAZ"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  )}

                  {/* Download XML */}
                  {nfe.xml_envio && (
                    <button
                      onClick={() => handleDownloadXml(nfe.xml_processado || nfe.xml_envio!, nfe.chave_acesso)}
                      className="p-1 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                      title="Baixar XML"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
          {(!nfes || nfes.length === 0) && (
            <TableRow>
              <TableCell className="text-center py-8 text-gray-500" >
                Nenhuma nota fiscal encontrada
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      
      {/* Pagination placeholder */}
      <TablePagination
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        hasMore={response?.next != null}
      />
    </div>
  )
}
