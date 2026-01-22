import React, { useEffect, useState } from 'react';
import { useCaixaStore } from '../store/caixaStore';
import { useAuthStore } from '@/features/auth/store';
import { AberturaCaixaModal } from './AberturaCaixaModal';
import { FechamentoCaixaModal } from './FechamentoCaixaModal';

export const CaixaStatus = () => {
  const { sessaoAberta, checkSessao, isLoading } = useCaixaStore();
  const { user } = useAuthStore();
  const [showAbertura, setShowAbertura] = useState(false);
  const [showFechamento, setShowFechamento] = useState(false);

  const canOpenCaixa = user?.role_caixa || ['ADMIN', 'GERENTE'].includes(user?.cargo || '');

  useEffect(() => {
    checkSessao();
  }, []);

  if (isLoading) return <div className="text-sm text-gray-500">...</div>;

  if (!sessaoAberta) {
    if (!canOpenCaixa) {
        return (
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded bg-gray-50 text-gray-400 border border-gray-100 cursor-not-allowed select-none">
                <span className="text-xs font-bold">Caixa Fechado</span>
            </div>
        )
    }

    return (
      <>
        <button 
          onClick={() => setShowAbertura(true)}
          className="bg-red-100 text-red-700 px-3 py-1 rounded text-sm font-medium hover:bg-red-200 border border-red-200"
          title="Clique para abrir o caixa"
        >
          Caixa Fechado
        </button>
        {showAbertura && <AberturaCaixaModal onClose={() => setShowAbertura(false)} />}
      </>
    );
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <div className="flex flex-col items-end">
            <span className="text-green-600 text-sm font-bold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              Caixa Aberto
            </span>
            <span className="text-xs text-gray-500">{sessaoAberta.caixa_nome}</span>
        </div>
        <button 
          onClick={() => setShowFechamento(true)}
          className="border px-2 py-1 rounded text-xs hover:bg-gray-100 text-gray-600"
        >
          Fechar
        </button>
      </div>
      {showFechamento && <FechamentoCaixaModal onClose={() => setShowFechamento(false)} />}
    </>
  );
};
