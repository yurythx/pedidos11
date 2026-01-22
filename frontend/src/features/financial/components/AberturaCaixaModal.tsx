'use client'
import React, { useEffect, useState } from 'react';
import { useCaixaStore } from '../store/caixaStore';
import { X, DollarSign, Monitor } from 'lucide-react';

interface Props {
  onClose: () => void;
}

export const AberturaCaixaModal = ({ onClose }: Props) => {
  const { caixasDisponiveis, fetchCaixas, abrirCaixa, error } = useCaixaStore();
  const [caixaId, setCaixaId] = useState('');
  const [saldoInicial, setSaldoInicial] = useState('0.00');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchCaixas();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caixaId) return;
    
    setIsSubmitting(true);
    try {
      await abrirCaixa(caixaId, parseFloat(saldoInicial));
      onClose();
    } catch (err) {
      // Error handled in store
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[60] animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden transform transition-all scale-100">
        
        {/* Header */}
        <div className="bg-primary px-6 py-4 flex justify-between items-center">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Monitor className="w-6 h-6" />
                Abrir Novo Caixa
            </h2>
            <button 
                onClick={onClose}
                className="text-white/80 hover:text-white hover:bg-white/10 p-2 rounded-full transition-colors"
            >
                <X size={20} />
            </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8">
            {error && (
                <div className="bg-red-50 border border-red-100 text-red-600 p-4 rounded-xl mb-6 text-sm flex items-center gap-2 animate-in slide-in-from-top-2">
                    <span className="font-bold">Erro:</span> {error}
                </div>
            )}
            
            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Selecione o Terminal</label>
                    <div className="relative">
                        <select 
                            className="w-full pl-4 pr-10 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all appearance-none bg-white text-gray-800"
                            value={caixaId}
                            onChange={e => setCaixaId(e.target.value)}
                            required
                        >
                            <option value="">Selecione um caixa...</option>
                            {caixasDisponiveis.map(c => (
                                <option key={c.id} value={c.id}>{c.nome}</option>
                            ))}
                        </select>
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                            <Monitor size={18} />
                        </div>
                    </div>
                </div>
                
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Fundo de Troco (Saldo Inicial)</label>
                    <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 font-bold">
                            R$
                        </div>
                        <input 
                            type="number" 
                            step="0.01"
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all font-mono text-lg font-bold text-gray-800"
                            value={saldoInicial}
                            onChange={e => setSaldoInicial(e.target.value)}
                            placeholder="0.00"
                        />
                    </div>
                    <p className="text-xs text-gray-400 mt-2 ml-1">Valor em dinheiro disponível na gaveta</p>
                </div>
            </div>
            
            <div className="flex gap-3 mt-8">
                <button 
                    type="button"
                    className="flex-1 px-4 py-3 border border-gray-200 text-gray-600 font-bold rounded-xl hover:bg-gray-50 transition-colors"
                    onClick={onClose}
                    disabled={isSubmitting}
                >
                    Cancelar
                </button>
                <button 
                    type="submit"
                    className="flex-1 px-4 py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary-dark shadow-lg shadow-red-100 hover:shadow-red-200 transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? (
                        <div className="flex items-center justify-center gap-2">
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            Abrindo...
                        </div>
                    ) : 'Confirmar Abertura'}
                </button>
            </div>
        </form>
      </div>
    </div>
  );
};
