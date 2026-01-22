import { request } from '@/lib/http/request';

export interface Colaborador {
  id: string;
  nome: string;
  cargo: string;
  comissao_percentual: string;
  ativo?: boolean;
}

export const colaboradorService = {
  getColaboradores: () => request.get<Colaborador[]>('/colaboradores/'),
  create: (data: Partial<Colaborador>) => request.post<Colaborador>('/colaboradores/', data),
  update: (id: string, data: Partial<Colaborador>) => request.patch<Colaborador>(`/colaboradores/${id}/`, data),
  delete: (id: string) => request.delete(`/colaboradores/${id}/`)
};
