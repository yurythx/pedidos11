'use client'

import React, { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { request } from '../../src/lib/http/request'
import type { Produto, NFePreview, NFePreviewItem } from '../../src/types'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/Table'
import { Upload, Check, FileText, AlertCircle, ShoppingCart, Package, ArrowRight, Save, Calendar } from 'lucide-react'
import { formatBRL } from '../../src/utils/currency'

export default function ComprasPage() {
  const router = useRouter()
  
  // Estados Gerais
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Estados de Dados
  const [preview, setPreview] = useState<NFePreview | null>(null)
  const [depositos, setDepositos] = useState<{ id: string; nome: string }[]>([])
  const [produtos, setProdutos] = useState<Produto[]>([])
  
  // Estados do Formulário
  const [depositoId, setDepositoId] = useState<string>('')
  const [itensForm, setItensForm] = useState<NFePreviewItem[]>([])
  
  // Estados Financeiros
  const [gerarConta, setGerarConta] = useState(true)
  const [dataVencimento, setDataVencimento] = useState<string>(
    new Date(new Date().setDate(new Date().getDate() + 30)).toISOString().split('T')[0]
  )

  // Carrega dependências iniciais
  useEffect(() => {
    const loadData = async () => {
      try {
        const [resDepositos, resProdutos] = await Promise.all([
          request.get<any>('/depositos/?page_size=100'),
          request.get<any>('/produtos/?page_size=1000') // Carrega mais produtos para o select
        ])
        setDepositos(resDepositos?.results ?? resDepositos ?? [])
        setProdutos(resProdutos?.results ?? resProdutos ?? [])
      } catch (err) {
        console.error('Erro ao carregar dados iniciais', err)
      }
    }
    loadData()
  }, [])

  const onUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPreview(null)
    setSuccessMsg(null)

    try {
      const input = e.currentTarget.elements.namedItem('xml') as HTMLInputElement
      const file = input?.files?.[0]
      if (!file) throw new Error('Selecione um arquivo XML')

      const form = new FormData()
      form.append('arquivo', file)
      
      const res = await request.post<{ success: boolean; preview: NFePreview; errors?: string[] }>('/nfe/importacao/upload-xml/', form)
      
      if (!res.success) {
        throw new Error(res.errors?.join(', ') ?? 'Erro ao processar XML')
      }

      setPreview(res.preview)
      
      // Inicializa o form com os dados do preview
      // Mapeia os campos que vêm do parser (assumindo que o parser retorna qtd_xml e valor_unitario/preco_custo)
      const mappedItens = res.preview.itens.map(item => ({
        ...item,
        produto_id: item.produto_sugerido_id ?? '',
        fator_conversao: item.fator_conversao_sugerido ?? 1,
        // Tenta pegar do item original se vier no payload (parser geralmente extrai isso)
        qtd_xml: (item as any).qtd_xml ?? (item as any).qCom ?? 0,
        preco_custo: (item as any).preco_custo ?? (item as any).vUnCom ?? 0,
        lote_codigo: (item as any).lote ?? '',
        lote_validade: (item as any).validade ?? '',
        lote_fabricacao: (item as any).fabricacao ?? '',
      }))
      
      setItensForm(mappedItens)

    } catch (err: any) {
      setError(err?.message ?? 'Erro no upload')
    } finally {
      setLoading(false)
    }
  }

  const updateItem = (index: number, field: keyof NFePreviewItem, value: any) => {
    setItensForm(prev => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      return next
    })
  }

  const totalImportacao = itensForm.reduce((acc, item) => {
    const qtd = Number(item.qtd_xml || 0)
    const custo = Number(item.preco_custo || 0)
    return acc + (qtd * custo)
  }, 0)

  const onConfirmar = async () => {
    if (!preview) return
    if (!depositoId) {
      alert('Selecione um depósito de entrada')
      return
    }

    if (!confirm('Confirma a importação da NFe? Isso irá criar movimentações de estoque.')) return

    setLoading(true)
    setError(null)

    try {
      const payload = {
        deposito_id: depositoId,
        numero_nfe: preview.numero_nfe,
        serie_nfe: preview.serie_nfe,
        fornecedor: preview.fornecedor,
        financeiro: {
          gerar_conta: gerarConta,
          data_vencimento: dataVencimento
        },
        itens: itensForm.map(i => ({
          codigo_xml: i.codigo_xml,
          produto_id: i.produto_id,
          fator_conversao: Number(i.fator_conversao),
          qtd_xml: Number(i.qtd_xml),
          preco_custo: Number(i.preco_custo),
          lote: i.lote_codigo ? {
            codigo: i.lote_codigo,
            validade: i.lote_validade || null,
            fabricacao: i.lote_fabricacao || null,
          } : null
        }))
      }

      const res = await request.post<any>('/nfe/importacao/confirmar/', payload)
      
      if (res.status === 'sucesso' || res.status === 'parcial') {
        setSuccessMsg(res.message)
        setPreview(null)
        setItensForm([])
        // Limpa input de arquivo se possível, ou apenas reseta estado visual
      } else {
        throw new Error(res.message ?? 'Erro desconhecido')
      }

    } catch (err: any) {
      setError(err?.message ?? 'Erro ao confirmar importação')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto pb-20">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1 flex items-center gap-2">
            <ShoppingCart className="w-8 h-8 text-primary" />
            Compras & Importação XML
          </h1>
          <p className="text-gray-500 mt-1">Gerencie compras e dê entrada via XML de NFe</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <Link href="/compras/historico" className="btn btn-secondary h-[42px] flex items-center">
            <FileText className="w-4 h-4 mr-2" />
            Histórico de Entradas
          </Link>

          {/* Depósito Selector - Global para a operação */}
          <div className="w-full md:w-64">
             <label className="text-xs font-bold text-gray-500 uppercase mb-1 block">Depósito de Entrada</label>
             <select 
               className="input w-full"
               value={depositoId}
               onChange={e => setDepositoId(e.target.value)}
             >
               <option value="">Selecione o depósito...</option>
               {depositos.map(d => (
                 <option key={d.id} value={d.id}>{d.nome}</option>
               ))}
             </select>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      {!preview && !successMsg && (
        <div className="card border-dashed border-2 border-gray-200 bg-gray-50 p-12 text-center hover:border-primary/50 transition-colors">
          <form onSubmit={onUpload} className="max-w-md mx-auto space-y-4">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">Importar Nota Fiscal (XML)</h3>
            <p className="text-gray-500 text-sm">
              Arraste o arquivo ou clique para selecionar. O sistema identificará os produtos e fornecedores automaticamente.
            </p>
            <input 
              type="file" 
              name="xml" 
              accept=".xml" 
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2.5 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-bold
                file:bg-primary file:text-white
                hover:file:bg-primary/90 cursor-pointer
                bg-white rounded-full border border-gray-200 p-1
              "
              onChange={(e) => {
                 // Auto submit on file select for better UX
                 if (e.target.files?.length) e.currentTarget.form?.requestSubmit()
              }}
            />
            {loading && <p className="text-sm text-blue-600 animate-pulse">Processando XML...</p>}
            {error && <div className="p-3 bg-red-100 text-red-700 rounded-lg text-sm">{error}</div>}
          </form>
        </div>
      )}

      {/* Success State */}
      {successMsg && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <Check className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-green-900">Importação Concluída!</h2>
          <p className="text-green-700">{successMsg}</p>
          <button onClick={() => setSuccessMsg(null)} className="btn btn-primary mt-4">
            Importar Outra NFe
          </button>
        </div>
      )}

      {/* Preview & Mapping Area */}
      {preview && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* NFe Info Card */}
          <div className="card bg-blue-50 border-blue-100 flex flex-col md:flex-row justify-between gap-6">
             <div>
                <span className="text-xs font-bold text-blue-600 uppercase">Fornecedor</span>
                <h3 className="text-xl font-bold text-blue-900">{preview.fornecedor.nome}</h3>
                <p className="text-blue-700 font-mono text-sm">{preview.fornecedor.cnpj}</p>
             </div>
             <div className="flex gap-8">
                <div>
                   <span className="text-xs font-bold text-blue-600 uppercase">Número NFe</span>
                   <p className="text-2xl font-bold text-blue-900">{preview.numero_nfe}</p>
                </div>
                <div>
                   <span className="text-xs font-bold text-blue-600 uppercase">Série</span>
                   <p className="text-2xl font-bold text-blue-900">{preview.serie_nfe}</p>
                </div>
             </div>
          </div>

          {error && (
            <div className="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200 flex items-center gap-3">
               <AlertCircle className="w-5 h-5" />
               {error}
            </div>
          )}

          {/* Items Table */}
          <div className="card overflow-hidden p-0">
             <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
                <h3 className="font-bold text-gray-700 flex items-center gap-2">
                   <Package className="w-5 h-5" /> Itens da Nota
                </h3>
                <span className="text-sm text-gray-500">{itensForm.length} itens encontrados</span>
             </div>
             
             <div className="overflow-x-auto">
               <table className="w-full text-sm text-left">
                 <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                   <tr>
                     <th className="px-4 py-3 w-[25%]">Produto na NFe (XML)</th>
                     <th className="px-4 py-3 w-[5%] text-center">Conv.</th>
                     <th className="px-4 py-3 w-[25%]">Produto no Sistema (De/Para)</th>
                     <th className="px-4 py-3 w-[10%] text-right">Qtd/Custo</th>
                     <th className="px-4 py-3 w-[25%]">Dados do Lote</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-gray-100">
                   {itensForm.map((item, idx) => (
                     <tr key={idx} className="hover:bg-blue-50/30 transition-colors group">
                       {/* Coluna 1: Dados XML */}
                       <td className="px-4 py-3 align-top">
                          <div className="font-medium text-gray-900">{item.descricao_xml}</div>
                          <div className="text-xs text-gray-500 font-mono mt-1">
                            Cód: {item.codigo_xml} • Un: {item.unidade_xml}
                          </div>
                       </td>

                       {/* Coluna 2: Fator */}
                       <td className="px-4 py-3 align-top text-center">
                          <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
                             <ArrowRight className="w-4 h-4" />
                          </div>
                          <input 
                            type="number" 
                            className="input w-16 text-center px-1 py-1 h-8 text-sm" 
                            value={item.fator_conversao}
                            onChange={(e) => updateItem(idx, 'fator_conversao', e.target.value)}
                            min="0.0001"
                            title="Fator de Conversão (Quantas unidades do sistema vêm em 1 unidade da nota)"
                          />
                       </td>

                       {/* Coluna 3: Produto Sistema */}
                       <td className="px-4 py-3 align-top">
                          <select 
                            className={`input w-full h-9 text-sm ${!item.produto_id ? 'border-red-300 bg-red-50' : ''}`}
                            value={item.produto_id ?? ''}
                            onChange={(e) => updateItem(idx, 'produto_id', e.target.value)}
                          >
                             <option value="">-- Selecione o Produto --</option>
                             {/* Mostra sugestões no topo se houver */}
                             {item.sugestoes_produtos?.map(s => (
                               <option key={`sug-${s.produto_id}`} value={s.produto_id} className="font-bold text-blue-700 bg-blue-50">
                                 ★ {s.nome} (Sugestão)
                               </option>
                             ))}
                             <option disabled>-------------------</option>
                             {produtos.map(p => (
                               <option key={p.id} value={p.id}>{p.nome}</option>
                             ))}
                          </select>
                          {!item.produto_id && (
                             <div className="text-xs text-red-500 mt-1 flex items-center gap-1">
                               <AlertCircle className="w-3 h-3" /> Vincule um produto
                             </div>
                          )}
                       </td>

                       {/* Coluna 4: Qtd/Custo */}
                       <td className="px-4 py-3 align-top text-right">
                          <div className="space-y-1">
                             <div className="flex justify-end items-center gap-2">
                                <span className="text-xs text-gray-400">Qtd:</span>
                                <input 
                                  type="number" 
                                  className="input w-20 text-right px-2 py-1 h-7 text-xs" 
                                  value={item.qtd_xml}
                                  onChange={(e) => updateItem(idx, 'qtd_xml', e.target.value)}
                                />
                             </div>
                             <div className="flex justify-end items-center gap-2">
                                <span className="text-xs text-gray-400">R$:</span>
                                <input 
                                  type="number" 
                                  className="input w-20 text-right px-2 py-1 h-7 text-xs" 
                                  value={item.preco_custo}
                                  onChange={(e) => updateItem(idx, 'preco_custo', e.target.value)}
                                />
                             </div>
                          </div>
                       </td>

                       {/* Coluna 5: Lote */}
                       <td className="px-4 py-3 align-top">
                          <div className="grid grid-cols-2 gap-2">
                             <input 
                               type="text" 
                               placeholder="Lote"
                               className="input px-2 py-1 h-7 text-xs"
                               value={item.lote_codigo}
                               onChange={(e) => updateItem(idx, 'lote_codigo', e.target.value)}
                             />
                             <div className="relative">
                               <input 
                                 type="date" 
                                 className="input px-2 py-1 h-7 text-xs w-full"
                                 title="Validade"
                                 value={item.lote_validade}
                                 onChange={(e) => updateItem(idx, 'lote_validade', e.target.value)}
                               />
                             </div>
                          </div>
                          {/* Fabricação opcional */}
                          <input 
                             type="date" 
                             className="input mt-1 px-2 py-1 h-7 text-xs w-full"
                             title="Data Fabricação (Opcional)"
                             placeholder="Fabricação"
                             value={item.lote_fabricacao}
                             onChange={(e) => updateItem(idx, 'lote_fabricacao', e.target.value)}
                          />
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </div>
          </div>

          {/* Dados Financeiros */}
          <div className="card bg-base-100 p-6 border border-gray-200 shadow-sm">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <span className="text-green-600 text-xl">$</span> Dados Financeiros
            </h3>
            
            <div className="flex flex-wrap items-end gap-6">
               <div className="form-control">
                  <label className="label cursor-pointer justify-start gap-3">
                    <input 
                      type="checkbox" 
                      className="checkbox checkbox-primary"
                      checked={gerarConta}
                      onChange={e => setGerarConta(e.target.checked)}
                    />
                    <span className="label-text font-medium">Gerar Conta a Pagar</span>
                  </label>
               </div>

               {gerarConta && (
                 <div className="form-control">
                    <label className="label text-xs font-bold uppercase text-gray-500 mb-1">Vencimento</label>
                    <div className="flex items-center gap-2">
                       <Calendar className="w-5 h-5 text-gray-400" />
                       <input 
                         type="date" 
                         className="input input-bordered"
                         value={dataVencimento}
                         onChange={e => setDataVencimento(e.target.value)}
                       />
                    </div>
                 </div>
               )}

               <div className="ml-auto text-right bg-gray-50 p-4 rounded-xl border border-gray-100">
                  <span className="block text-xs text-gray-500 uppercase mb-1">Valor Total da Nota</span>
                  <span className="text-2xl font-bold text-gray-900">{formatBRL(totalImportacao)}</span>
               </div>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex justify-end gap-4 pt-4 border-t">
             <button 
               onClick={() => { setPreview(null); setItensForm([]); }}
               className="btn btn-secondary"
             >
               Cancelar
             </button>
             <button 
               onClick={onConfirmar}
               disabled={loading || !depositoId || itensForm.some(i => !i.produto_id)}
               className="btn btn-primary bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
             >
               {loading ? 'Processando...' : (
                 <>
                   <Save className="w-5 h-5 mr-2" />
                   Confirmar Importação
                 </>
               )}
             </button>
          </div>
        </div>
      )}
    </div>
  )
}
