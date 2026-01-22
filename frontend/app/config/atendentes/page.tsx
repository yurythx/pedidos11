'use client'
import React, { useEffect, useState } from 'react'
import { colaboradorService, Colaborador } from '@/features/partners/services/colaboradorService'
import { Plus, Trash, Edit } from 'lucide-react'

export default function AtendentesPage() {
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  // Form State
  const [nome, setNome] = useState('')
  const [cargo, setCargo] = useState('')
  const [comissao, setComissao] = useState('0')

  const fetch = async () => {
    try {
      const data = await colaboradorService.getColaboradores()
      // API might return { results: [] } or []
      const list = Array.isArray(data) ? data : (data as any).results || []
      setColaboradores(list)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetch()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = { nome, cargo, comissao_percentual: comissao }
    try {
      if (editingId) {
        await colaboradorService.update(editingId, payload)
      } else {
        await colaboradorService.create(payload)
      }
      setIsModalOpen(false)
      resetForm()
      fetch()
    } catch (e) {
      alert('Erro ao salvar atendente')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza?')) return
    try {
      await colaboradorService.delete(id)
      fetch()
    } catch (e) {
      alert('Erro ao excluir')
    }
  }

  const resetForm = () => {
    setNome('')
    setCargo('')
    setComissao('0')
    setEditingId(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Equipe e Atendentes</h1>
        <button 
          onClick={() => { setIsModalOpen(true); resetForm(); }}
          className="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-colors"
        >
          <Plus size={20} /> Novo Atendente
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <th className="p-4">Nome</th>
              <th className="p-4">Cargo</th>
              <th className="p-4">Comissão (%)</th>
              <th className="p-4 text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {colaboradores.map(c => (
              <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 text-gray-900 font-medium">{c.nome}</td>
                <td className="p-4 text-gray-600">{c.cargo}</td>
                <td className="p-4 text-gray-600">{c.comissao_percentual}%</td>
                <td className="p-4 text-right space-x-2">
                  <button 
                    onClick={() => { 
                        setEditingId(c.id); 
                        setNome(c.nome); 
                        setCargo(c.cargo); 
                        setComissao(c.comissao_percentual); 
                        setIsModalOpen(true); 
                    }}
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
             {colaboradores.length === 0 && !loading && (
                <tr>
                    <td colSpan={4} className="p-8 text-center text-gray-500">Nenhum atendente cadastrado.</td>
                </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-white p-6 rounded-xl w-96 shadow-2xl transform transition-all scale-100">
            <h2 className="text-xl font-bold mb-4 text-gray-800">{editingId ? 'Editar' : 'Novo'} Atendente</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-gray-700">Nome Completo</label>
                <input 
                  type="text" 
                  value={nome}
                  onChange={e => setNome(e.target.value)}
                  className="w-full border border-gray-300 p-2 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-gray-700">Cargo</label>
                <input 
                  type="text" 
                  value={cargo}
                  onChange={e => setCargo(e.target.value)}
                  className="w-full border border-gray-300 p-2 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                  placeholder="Ex: Garçom, Gerente"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-gray-700">Comissão (%)</label>
                <input 
                  type="number" 
                  step="0.1"
                  value={comissao}
                  onChange={e => setComissao(e.target.value)}
                  className="w-full border border-gray-300 p-2 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
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
