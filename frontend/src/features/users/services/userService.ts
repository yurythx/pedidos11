import { request } from '@/lib/http/request';

export interface User {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  cargo: string;
  is_active: boolean;
  is_colaborador: boolean;
  role_atendente: boolean;
  role_caixa: boolean;
  comissao_percentual: string;
  password?: string;
}

export const userService = {
  getAll: () => request.get<User[]>('/auth/users/'),
  getAtendentes: () => request.get<User[]>('/auth/users/?role_atendente=true&is_active=true'),
  create: (data: Partial<User>) => request.post<User>('/auth/users/', data),
  update: (id: string, data: Partial<User>) => request.patch<User>(`/auth/users/${id}/`, data),
  delete: (id: string) => request.delete(`/auth/users/${id}/`)
};
