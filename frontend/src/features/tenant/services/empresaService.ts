import { request } from '../../../lib/http/request'

export interface EmpresaConfig {
  id: string;
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;
  inscricao_estadual: string;
  inscricao_municipal: string;
  ambiente_nfe: '1' | '2';
  regime_tributario: string;
  certificado_digital?: string; // URL or boolean
  senha_certificado?: string;
  serie_nfe: number;
  numero_nfe_atual: number;
}

export const empresaService = {
  getMe: () => {
    return request.get<EmpresaConfig>('/empresa/me/')
  },

  update: (data: Partial<EmpresaConfig> | FormData) => {
    // If data is FormData, request will handle content-type
    return request.patch<EmpresaConfig>('/empresa/me/', data)
  }
}
