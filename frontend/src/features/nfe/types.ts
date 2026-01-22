export interface NFe {
  id: string;
  numero: number;
  serie: number;
  modelo: string;
  chave_acesso: string;
  status: 'DIGITACAO' | 'VALIDADA' | 'ASSINADA' | 'TRANSMITIDA' | 'AUTORIZADA' | 'REJEITADA' | 'CANCELADA' | 'DENEGADA';
  data_emissao: string;
  valor_total_nota: string;
  xml_envio?: string;
  xml_retorno?: string;
  xml_processado?: string;
  protocolo_autorizacao?: string;
  observacoes?: string;
  cliente: {
    id: string;
    nome: string;
    cpf_cnpj: string;
  };
  venda?: {
    id: string;
    total_liquido: string;
  };
}

export interface NFeFilter {
  data_inicio?: string;
  data_fim?: string;
  status?: string;
}

export interface GerarNFePayload {
  venda_id: string;
  modelo?: '55' | '65';
  serie?: string;
}

export interface TransmissaoResultado {
  cStat: string;
  xMotivo: string;
  protocolo?: {
    nProt: string;
    cStat: string;
    xMotivo: string;
  };
}
