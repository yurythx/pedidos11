import React, { useState, useEffect } from 'react';
import { useCaixaStore } from '../store/caixaStore';
import { formatBRL } from '../../../utils/currency';
import { request } from '../../../lib/http/request';
import { Calculator, Eye, EyeOff } from 'lucide-react';

interface Props {
  onClose: () => void;
}

interface ResumoCaixa {
  saldo_inicial: number
  total_suprimentos: number
  total_sangrias: number
  total_vendas: number
  vendas_por_tipo: Record<string, number>
  saldo_final_dinheiro: number
}

export const FechamentoCaixaModal = ({ onClose }: Props) => {
  const { sessaoAberta, fecharCaixa, error } = useCaixaStore();
  const [saldoFinal, setSaldoFinal] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resumo, setResumo] = useState<ResumoCaixa | null>(null);
  const [showResumo, setShowResumo] = useState(false);

  useEffect(() => {
    if (sessaoAberta?.id) {
        request.get(`/sessoes-caixa/${sessaoAberta.id}/resumo/`)
            .then(res => setResumo(res as any))
            .catch(console.error)
    }
  }, [sessaoAberta?.id]);

  if (!sessaoAberta) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!saldoFinal) return;
    
    if (!confirm('Confirma o fechamento do caixa?')) return;

    setIsSubmitting(true);
    try {
      await fecharCaixa(parseFloat(saldoFinal));
      onClose();
    } catch (err) {
      // Error handled in store
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
      <div className="bg-white p-6 rounded-xl w-[450px] shadow-2xl">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
            <Calculator className="text-red-600" /> Fechar Caixa
        </h2>
        
        <div className="mb-6 bg-gray-50 p-4 rounded-lg border border-gray-100">
          <p className="text-sm text-gray-600"><span className="font-semibold">Operador:</span> {sessaoAberta.operador_nome}</p>
          <p className="text-sm text-gray-600"><span className="font-semibold">Abertura:</span> {new Date(sessaoAberta.data_abertura).toLocaleString()}</p>
        </div>

        {/* Toggle Resumo */}
        <div className="mb-4">
            <button 
                type="button" 
                onClick={() => setShowResumo(!showResumo)}
                className="text-sm font-medium text-primary hover:text-primary-dark flex items-center gap-1 transition-colors"
            >
                {showResumo ? <><EyeOff size={16}/> Ocultar Conferência</> : <><Eye size={16}/> Ver Conferência (Prévia)</>}
            </button>

            {showResumo && resumo && (
                <div className="bg-white p-3 rounded-lg mt-2 text-sm space-y-1 border border-gray-200 shadow-sm animate-in slide-in-from-top-2">
                    <div className="flex justify-between">
                        <span>Saldo Inicial:</span>
                        <span>{formatBRL(resumo.saldo_inicial)}</span>
                    </div>
                    <div className="flex justify-between text-green-600">
                        <span>(+) Suprimentos:</span>
                        <span>{formatBRL(resumo.total_suprimentos)}</span>
                    </div>
                    <div className="flex justify-between text-red-600">
                        <span>(-) Sangrias:</span>
                        <span>{formatBRL(resumo.total_sangrias)}</span>
                    </div>
                    
                    <div className="border-t border-gray-100 my-2 pt-1 font-bold text-gray-700">Vendas por Tipo</div>
                    <div className="pl-2 space-y-1 text-xs text-gray-600 mb-2">
                        {Object.entries(resumo.vendas_por_tipo).map(([tipo, valor]) => (
                            Number(valor) > 0 && (
                                <div key={tipo} className="flex justify-between">
                                    <span>{tipo.replace('CARTAO_', 'CARTÃO ')}:</span>
                                    <span>{formatBRL(Number(valor))}</span>
                                </div>
                            )
                        ))}
                         {/* Fallback se não tiver vendas */}
                         {Object.values(resumo.vendas_por_tipo).every(v => Number(v) === 0) && (
                            <div className="text-gray-400 italic">Nenhuma venda registrada</div>
                         )}
                    </div>

                    <div className="border-t-2 border-dashed border-gray-200 mt-2 pt-2 flex justify-between font-bold text-lg text-gray-800 bg-gray-50 p-2 rounded">
                        <span>Esperado na Gaveta:</span>
                        <span>{formatBRL(resumo.saldo_final_dinheiro)}</span>
                    </div>
                </div>
            )}
        </div>

        {error && <div className="bg-red-50 border border-red-200 text-red-700 p-3 mb-4 rounded-lg text-sm">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block mb-2 text-sm font-bold text-gray-700">
                Saldo Final em Dinheiro (R$) <span className="text-red-500">*</span>
            </label>
            <div className="relative">
                <span className="absolute left-3 top-3 text-gray-500 font-bold">R$</span>
                <input 
                  type="number" 
                  step="0.01"
                  className="w-full border border-gray-300 p-3 pl-10 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all font-bold text-lg"
                  value={saldoFinal}
                  onChange={e => setSaldoFinal(e.target.value)}
                  placeholder="0,00"
                  required
                  autoFocus
                />
            </div>
            <p className="text-xs text-gray-500 mt-1">Conte o dinheiro físico na gaveta e informe o valor.</p>
          </div>
          
          <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-100">
            <button 
              type="button"
              className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700 font-medium transition-colors"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancelar
            </button>
            <button 
              type="submit"
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-bold shadow-lg shadow-red-200 transition-all active:scale-95 disabled:opacity-70"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Fechando...' : 'Confirmar Fechamento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
