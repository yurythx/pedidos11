'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { request } from '../../../../src/lib/http/request'
import { useParams } from 'next/navigation'

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

  if (loading) return <div className="p-4">Carregando endereços...</div>
  return (
    <div className="p-4 max-w-3xl">
      <h1 className="text-xl font-semibold mb-3">Endereços do Cliente</h1>
      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
      <form onSubmit={onCreate} className="space-y-2 mb-4 border p-3 rounded">
        <div className="grid grid-cols-4 gap-2">
          <div>
            <label className="block text-sm">Tipo</label>
            <select className="mt-1 w-full border rounded px-2 py-1" value={form.tipo} onChange={(e) => onChange('tipo', e.target.value)}>
              <option value="ENTREGA">Entrega</option>
              <option value="COBRANCA">Cobrança</option>
              <option value="COMERCIAL">Comercial</option>
              <option value="RESIDENCIAL">Residencial</option>
              <option value="FISICO">Físico</option>
            </select>
          </div>
          <div>
            <label className="block text-sm">CEP</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.cep ?? ''} onChange={(e) => onChange('cep', e.target.value)} />
          </div>
          <div className="col-span-2">
            <label className="block text-sm">Logradouro</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.logradouro ?? ''} onChange={(e) => onChange('logradouro', e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-2">
          <div>
            <label className="block text-sm">Número</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.numero ?? ''} onChange={(e) => onChange('numero', e.target.value)} />
          </div>
          <div>
            <label className="block text-sm">Complemento</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.complemento ?? ''} onChange={(e) => onChange('complemento', e.target.value)} />
          </div>
          <div>
            <label className="block text-sm">Bairro</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.bairro ?? ''} onChange={(e) => onChange('bairro', e.target.value)} />
          </div>
          <div>
            <label className="block text-sm">Cidade</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.cidade ?? ''} onChange={(e) => onChange('cidade', e.target.value)} />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-2">
          <div>
            <label className="block text-sm">UF</label>
            <input className="mt-1 w-full border rounded px-2 py-1" value={form.uf ?? ''} onChange={(e) => onChange('uf', e.target.value)} />
          </div>
        </div>
        <button type="submit" className="bg-black text-white rounded px-3 py-2">Adicionar</button>
      </form>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-2 border">Tipo</th>
            <th className="text-left p-2 border">Endereço</th>
            <th className="text-left p-2 border">CEP</th>
            <th className="text-left p-2 border">Cidade/UF</th>
          </tr>
        </thead>
        <tbody>
          {enderecos.map((e) => (
            <tr key={e.id}>
              <td className="p-2 border">{e.tipo}</td>
              <td className="p-2 border">
                {e.logradouro}, {e.numero}{e.complemento ? ` - ${e.complemento}` : ''} - {e.bairro}
              </td>
              <td className="p-2 border">{e.cep}</td>
              <td className="p-2 border">{e.cidade}/{e.uf}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

