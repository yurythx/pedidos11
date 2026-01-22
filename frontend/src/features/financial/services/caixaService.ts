import { request } from '@/lib/http/request';
import { Caixa, SessaoCaixa, AberturaCaixaPayload, FechamentoCaixaPayload, MovimentoPayload } from '../types';

export const caixaService = {
  getCaixas: () => request.get<Caixa[]>('/caixas/'),
  createCaixa: (data: Partial<Caixa>) => request.post<Caixa>('/caixas/', data),
  updateCaixa: (id: string, data: Partial<Caixa>) => request.patch<Caixa>(`/caixas/${id}/`, data),
  deleteCaixa: (id: string) => request.delete(`/caixas/${id}/`),
  
  getSessaoAberta: () => request.get<SessaoCaixa>('/sessoes-caixa/aberta/').catch(() => null),
  
  abrirCaixa: (data: AberturaCaixaPayload) => request.post<SessaoCaixa>('/sessoes-caixa/abrir/', data),
  
  fecharCaixa: (sessaoId: string, data: FechamentoCaixaPayload) => request.post<SessaoCaixa>(`/sessoes-caixa/${sessaoId}/fechar/`, data),
  
  movimentar: (sessaoId: string, data: MovimentoPayload) => 
    request.post(`/sessoes-caixa/${sessaoId}/movimentar/`, data)
};
