import { create } from 'zustand';
import { SessaoCaixa, Caixa } from '../types';
import { caixaService } from '../services/caixaService';

interface CaixaState {
  sessaoAberta: SessaoCaixa | null;
  caixasDisponiveis: Caixa[];
  isLoading: boolean;
  error: string | null;
  
  checkSessao: () => Promise<void>;
  fetchCaixas: () => Promise<void>;
  abrirCaixa: (caixaId: string, saldoInicial: number) => Promise<void>;
  fecharCaixa: (saldoFinal: number) => Promise<void>;
}

export const useCaixaStore = create<CaixaState>((set, get) => ({
  sessaoAberta: null,
  caixasDisponiveis: [],
  isLoading: false,
  error: null,
  
  checkSessao: async () => {
    set({ isLoading: true });
    try {
      const sessao = await caixaService.getSessaoAberta();
      set({ sessaoAberta: sessao, error: null });
    } catch (err) {
      // Se retornar null do service (tratado no catch do service) ou 404
      set({ sessaoAberta: null, error: null });
    } finally {
      set({ isLoading: false });
    }
  },
  
  fetchCaixas: async () => {
    try {
      const caixas = await caixaService.getCaixas();
      set({ caixasDisponiveis: caixas });
    } catch (err) {
      console.error(err);
    }
  },
  
  abrirCaixa: async (caixaId, saldoInicial) => {
    set({ isLoading: true, error: null });
    try {
      const sessao = await caixaService.abrirCaixa({ caixa_id: caixaId, saldo_inicial: saldoInicial });
      set({ sessaoAberta: sessao });
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || 'Erro ao abrir caixa';
      set({ error: msg });
      throw new Error(msg);
    } finally {
      set({ isLoading: false });
    }
  },
  
  fecharCaixa: async (saldoFinal) => {
    const { sessaoAberta } = get();
    if (!sessaoAberta) return;
    
    set({ isLoading: true, error: null });
    try {
      await caixaService.fecharCaixa(sessaoAberta.id, { saldo_final: saldoFinal });
      set({ sessaoAberta: null });
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || 'Erro ao fechar caixa';
      set({ error: msg });
      throw new Error(msg);
    } finally {
      set({ isLoading: false });
    }
  }
}));
