import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Upload, AlertCircle, CheckCircle } from 'lucide-react'
import { empresaService } from '../../tenant/services/empresaService'

export function CertificadoConfig() {
  const queryClient = useQueryClient()
  const [senha, setSenha] = React.useState('')
  const [file, setFile] = React.useState<File | null>(null)
  const [ambiente, setAmbiente] = React.useState('2') // 2=Homologação

  const { data: empresa, isLoading } = useQuery({
    queryKey: ['empresa'],
    queryFn: () => empresaService.getMe()
  })

  React.useEffect(() => {
    if (empresa) {
      setAmbiente(empresa.ambiente_nfe || '2')
    }
  }, [empresa])

  const mutation = useMutation({
    mutationFn: (formData: FormData) => empresaService.update(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empresa'] })
      alert('Configurações salvas com sucesso!')
      setSenha('')
      setFile(null)
    },
    onError: (error: any) => {
      alert(`Erro ao salvar: ${error.message}`)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const formData = new FormData()
    formData.append('ambiente_nfe', ambiente)
    
    if (senha) {
      formData.append('senha_certificado', senha)
    }
    
    if (file) {
      formData.append('certificado_digital', file)
    }
    
    mutation.mutate(formData)
  }

  if (isLoading) return <div>Carregando...</div>

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5" />
        Configuração do Certificado Digital (A1)
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ambiente SEFAZ
          </label>
          <select
            value={ambiente}
            onChange={(e) => setAmbiente(e.target.value)}
            className="w-full border rounded-md p-2"
          >
            <option value="2">Homologação (Testes)</option>
            <option value="1">Produção</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Arquivo do Certificado (.pfx ou .p12)
          </label>
          <input
            type="file"
            accept=".pfx,.p12"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full border rounded-md p-2"
          />
          {empresa?.certificado_digital && !file && (
            <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              Certificado já configurado
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Senha do Certificado
          </label>
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder={empresa?.certificado_digital ? "Deixe em branco para manter a atual" : "Digite a senha"}
            className="w-full border rounded-md p-2"
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {mutation.isPending ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </form>
    </div>
  )
}
