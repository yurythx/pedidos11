'use client'
import React, { useEffect, useState } from 'react'
import { caixaService } from '@/features/financial/services/caixaService'
import { Caixa } from '@/features/financial/types'
import { Plus, Trash, Edit } from 'lucide-react'

export default function CaixasPage() {
  const [caixas, setCaixas] = useState<Caixa[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCaixa, setEditingCaixa] = useState<Caixa | null>(null)
  const [nome, setNome] = useState('')

  const fetchCaixas = async () => {
    try {
      const data = await caixaService.getCaixas()
      setCaixas(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCaixas()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingCaixa) {
        await caixaService.updateCaixa(editingCaixa.id, { nome })
      } else {
        await caixaService.createCaixa({ nome, ativo: true })
      }
      setIsModalOpen(false)
      setNome('')
      setEditingCaixa(null)
      fetchCaixas()
    } catch (e) {
      alert('Erro ao salvar caixa')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza?')) return
    try {
      await caixaService.deleteCaixa(id)
      fetchCaixas()
    } catch (e) {
      alert('Erro ao excluir')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gerenciar Caixas</h1>
        <button 
          onClick={() => { setIsModalOpen(true); setEditingCaixa(null); setNome(''); }}
          className="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-colors"
        >
          <Plus size={20} /> Novo Caixa
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <th className="p-4">Nome</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {caixas.map(c => (
              <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 text-gray-900 font-medium">{c.nome}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${c.ativo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {c.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="p-4 text-right space-x-2">
                  <button 
                    onClick={() => { setEditingCaixa(c); setNome(c.nome); setIsModalOpen(true); }}
                    className="p-2 text-primary hover:bg-red-50 rounded transition-colors"
                  >
                    <Edit size={18} />
                  </button>
                  <button 
                    onClick={() => handleDelete(c.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {caixas.length === 0 && !loading && (
                <tr>
                    <td colSpan={3} className="p-8 text-center text-gray-500">Nenhum caixa cadastrado.</td>
                </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-white p-6 rounded-xl w-96 shadow-2xl transform transition-all scale-100">
            <h2 className="text-xl font-bold mb-4 text-gray-800">{editingCaixa ? 'Editar' : 'Novo'} Caixa</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-gray-700">Nome do Caixa</label>
                <input 
                  type="text" 
                  value={nome}
                  onChange={e => setNome(e.target.value)}
                  className="w-full border border-gray-300 p-2 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all"
                  placeholder="Ex: Caixa 01"
                  required
                />
              </div>
              <div className="flex justify-end gap-2">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                >
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
