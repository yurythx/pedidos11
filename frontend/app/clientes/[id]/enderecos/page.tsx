'use client'

import React, { useEffect, useState } from 'react'
import { request } from '../../../../src/lib/http/request'
import { useParams } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../../src/components/ui/Table'
import { Plus, MapPin } from 'lucide-react'

type Endereco = {
  id: string
  object_id: string
  tipo: string
  cep: string
  logradouro: string
  numero: string
  complemento?: string | null
  bairro: string
  cidade: string
  uf: string
}

export default function EnderecosClientePage() {
  const params = useParams<{ id: string }>()
  const clienteId = params.id
  const [enderecos, setEnderecos] = useState<Endereco[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await request.get<any>('/enderecos/?page_size=100')
        const results: Endereco[] = (res?.results ?? res ?? []).filter(
          (e: Endereco) => e.object_id === clienteId
        )
        setEnderecos(results)
      } catch (err: any) {
        setError(err?.message ?? 'Erro ao carregar endereços')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [clienteId])

  const [form, setForm] = useState<Partial<Endereco>>({
    tipo: 'ENTREGA',
    cep: '',
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    uf: 'SP',
  })

  const onChange = (field: keyof Endereco, value: any) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const payload = {
        content_type: 'partners.cliente',
        object_id: clienteId,
        tipo: form.tipo,
        cep: form.cep,
        logradouro: form.logradouro,
        numero: form.numero,
        complemento: form.complemento,
        bairro: form.bairro,
        cidade: form.cidade,
        uf: form.uf,
      }
      const created = await request.post<Endereco>('/enderecos/', payload)
      setEnderecos((list) => [created, ...list])
      setForm({
        tipo: 'ENTREGA',
        cep: '',
        logradouro: '',
        numero: '',
        complemento: '',
        bairro: '',
        cidade: '',
        uf: 'SP',
      })
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao criar endereço')
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Carregando endereços...</div>

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="heading-1">Endereços do Cliente</h1>
          <p className="text-gray-500 mt-1">Gerencie os locais de entrega e cobrança</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 className="heading-2 mb-4 flex items-center gap-2">
           <MapPin className="w-5 h-5 text-gray-400" />
           Novo Endereço
        </h2>
        {error && <p className="text-red-600 text-sm mb-3 bg-red-50 p-3 rounded-lg">{error}</p>}
        <form onSubmit={onCreate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="label">Tipo</label>
              <select className="input" value={form.tipo} onChange={(e) => onChange('tipo', e.target.value)}>
                <option value="ENTREGA">Entrega</option>
                <option value="COBRANCA">Cobrança</option>
                <option value="COMERCIAL">Comercial</option>
                <option value="RESIDENCIAL">Residencial</option>
                <option value="FISICO">Físico</option>
              </select>
            </div>
            <div>
              <label className="label">CEP</label>
              <input className="input" value={form.cep ?? ''} onChange={(e) => onChange('cep', e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <label className="label">Logradouro</label>
              <input className="input" value={form.logradouro ?? ''} onChange={(e) => onChange('logradouro', e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="label">Número</label>
              <input className="input" value={form.numero ?? ''} onChange={(e) => onChange('numero', e.target.value)} />
            </div>
            <div>
              <label className="label">Complemento</label>
              <input className="input" value={form.complemento ?? ''} onChange={(e) => onChange('complemento', e.target.value)} />
            </div>
            <div>
              <label className="label">Bairro</label>
              <input className="input" value={form.bairro ?? ''} onChange={(e) => onChange('bairro', e.target.value)} />
            </div>
            <div>
              <label className="label">Cidade</label>
              <input className="input" value={form.cidade ?? ''} onChange={(e) => onChange('cidade', e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="label">UF</label>
              <input className="input" value={form.uf ?? ''} onChange={(e) => onChange('uf', e.target.value)} />
            </div>
          </div>
          <div className="flex justify-end">
            <button type="submit" className="btn btn-primary">
              <Plus className="w-5 h-5 mr-2" />
              Adicionar Endereço
            </button>
          </div>
        </form>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Tipo</TableHead>
            <TableHead>Endereço</TableHead>
            <TableHead>CEP</TableHead>
            <TableHead>Cidade/UF</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {enderecos.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} className="text-center py-8 text-gray-500">
                Nenhum endereço cadastrado.
              </TableCell>
            </TableRow>
          ) : (
            enderecos.map((e) => (
              <TableRow key={e.id}>
                <TableCell>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-bold rounded-full">
                    {e.tipo}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="font-medium text-gray-900">{e.logradouro}, {e.numero}</div>
                  <div className="text-xs text-gray-500">{e.bairro}{e.complemento ? ` - ${e.complemento}` : ''}</div>
                </TableCell>
                <TableCell>{e.cep}</TableCell>
                <TableCell>{e.cidade}/{e.uf}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

