'use client'
import React, { useEffect, useState } from 'react'
import { userService, User } from '@/features/users/services/userService'
import { Plus, Trash, Edit, User as UserIcon, Shield } from 'lucide-react'

export default function UsuariosPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  // Form State
  const [formData, setFormData] = useState<Partial<User>>({
    username: '',
    first_name: '',
    email: '',
    password: '',
    cargo: 'VENDEDOR',
    is_colaborador: false,
    role_atendente: false,
    role_caixa: false,
    comissao_percentual: '10'
  })

  const fetch = async () => {
    try {
      const data = await userService.getAll()
      // API might return { results: [] } or []
      const list = Array.isArray(data) ? data : (data as any).results || []
      setUsers(list)
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
    try {
      if (editingId) {
        const payload = { ...formData }
        if (!payload.password) delete payload.password // Don't send empty password on update
        await userService.update(editingId, payload)
      } else {
        await userService.create(formData)
      }
      setIsModalOpen(false)
      resetForm()
      fetch()
    } catch (e: any) {
        const msg = e.response?.data ? JSON.stringify(e.response.data) : 'Erro ao salvar'
        alert('Erro: ' + msg)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza?')) return
    try {
      await userService.delete(id)
      fetch()
    } catch (e) {
      alert('Erro ao excluir')
    }
  }

  const resetForm = () => {
    setFormData({
        username: '',
        first_name: '',
        email: '',
        password: '',
        cargo: 'VENDEDOR',
        is_colaborador: false,
        role_atendente: false,
        role_caixa: false,
        comissao_percentual: '10'
    })
    setEditingId(null)
  }

  const handleEdit = (user: User) => {
    setEditingId(user.id)
    setFormData({
        username: user.username,
        first_name: user.first_name,
        email: user.email,
        password: '', // Password not shown
        cargo: user.cargo,
        is_colaborador: user.is_colaborador,
        role_atendente: user.role_atendente,
        role_caixa: user.role_caixa,
        comissao_percentual: user.comissao_percentual
    })
    setIsModalOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Gerenciar Usuários</h1>
        <button 
          onClick={() => { setIsModalOpen(true); resetForm(); }}
          className="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-colors"
        >
          <Plus size={20} /> Novo Usuário
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <th className="p-4">Usuário</th>
              <th className="p-4">Cargo</th>
              <th className="p-4">Funções</th>
              <th className="p-4">Comissão</th>
              <th className="p-4 text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4">
                    <div className="font-medium text-gray-900">{u.first_name || u.username}</div>
                    <div className="text-xs text-gray-500">{u.email}</div>
                </td>
                <td className="p-4">
                    <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-bold">
                        {u.cargo}
                    </span>
                </td>
                <td className="p-4">
                    <div className="flex gap-1 flex-wrap">
                        {u.role_atendente && <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs">Atendente</span>}
                        {u.role_caixa && <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs">Caixa</span>}
                        {!u.role_atendente && !u.role_caixa && <span className="text-gray-400 text-xs">-</span>}
                    </div>
                </td>
                <td className="p-4 text-gray-600">
                    {Number(u.comissao_percentual) > 0 ? `${u.comissao_percentual}%` : '-'}
                </td>
                <td className="p-4 text-right space-x-2">
                  <button 
                    onClick={() => handleEdit(u)}
                    className="p-2 text-primary hover:bg-red-50 rounded transition-colors"
                  >
                    <Edit size={18} />
                  </button>
                  <button 
                    onClick={() => handleDelete(u.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-white p-6 rounded-xl w-[500px] shadow-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                <UserIcon className="text-primary" />
                {editingId ? 'Editar' : 'Novo'} Usuário
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">Nome</label>
                    <input 
                      type="text" 
                      value={formData.first_name}
                      onChange={e => setFormData({...formData, first_name: e.target.value})}
                      className="input"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">Login (Username)</label>
                    <input 
                      type="text" 
                      value={formData.username}
                      onChange={e => setFormData({...formData, username: e.target.value})}
                      className="input"
                      required
                    />
                  </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Email</label>
                <input 
                  type="email" 
                  value={formData.email}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">
                    {editingId ? 'Nova Senha (deixe em branco para manter)' : 'Senha'}
                </label>
                <input 
                  type="password" 
                  value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  className="input"
                  required={!editingId}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">Cargo Principal</label>
                    <select 
                      value={formData.cargo}
                      onChange={e => setFormData({...formData, cargo: e.target.value})}
                      className="input"
                    >
                        <option value="VENDEDOR">Vendedor</option>
                        <option value="GERENTE">Gerente</option>
                        <option value="ADMIN">Administrador</option>
                        <option value="CAIXA">Caixa (Operador)</option>
                        <option value="ESTOQUISTA">Estoquista</option>
                        <option value="FINANCEIRO">Financeiro</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700">Comissão (%)</label>
                    <input 
                      type="number"
                      step="0.1"
                      value={formData.comissao_percentual}
                      onChange={e => setFormData({...formData, comissao_percentual: e.target.value})}
                      className="input"
                    />
                  </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                  <h3 className="font-bold text-gray-700 mb-2 text-sm flex items-center gap-2">
                      <Shield size={16} /> Funções Operacionais
                  </h3>
                  <div className="space-y-2">
                      <label className="flex items-center gap-2 cursor-pointer">
                          <input 
                            type="checkbox"
                            checked={formData.is_colaborador}
                            onChange={e => setFormData({...formData, is_colaborador: e.target.checked})}
                            className="w-4 h-4 text-primary rounded focus:ring-primary"
                          />
                          <span className="text-sm">É Colaborador (Funcionário)</span>
                      </label>
                      
                      {formData.is_colaborador && (
                          <div className="ml-6 space-y-2 animate-in slide-in-from-left-2">
                              <label className="flex items-center gap-2 cursor-pointer">
                                  <input 
                                    type="checkbox"
                                    checked={formData.role_atendente}
                                    onChange={e => setFormData({...formData, role_atendente: e.target.checked})}
                                    className="w-4 h-4 text-primary rounded focus:ring-primary"
                                  />
                                  <span className="text-sm">Função: Atendente/Garçom</span>
                              </label>
                              <label className="flex items-center gap-2 cursor-pointer">
                                  <input 
                                    type="checkbox"
                                    checked={formData.role_caixa}
                                    onChange={e => setFormData({...formData, role_caixa: e.target.checked})}
                                    className="w-4 h-4 text-primary rounded focus:ring-primary"
                                  />
                                  <span className="text-sm">Função: Operador de Caixa</span>
                              </label>
                          </div>
                      )}
                  </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark shadow-lg shadow-red-100"
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
