export interface Caixa {
  id: string;
  nome: string;
  ativo: boolean;
}

export interface SessaoCaixa {
  id: string;
  caixa: string; // ID
  caixa_nome?: string;
  operador: string; // ID
  operador_nome?: string;
  data_abertura: string;
  data_fechamento?: string;
  saldo_inicial: string;
  saldo_final_informado?: string;
  saldo_final_calculado?: string;
  status: 'ABERTA' | 'FECHADA';
  diferenca_caixa?: string;
}

export interface AberturaCaixaPayload {
  caixa_id: string;
  saldo_inicial: number;
}

export interface FechamentoCaixaPayload {
  saldo_final: number;
}

export interface MovimentoPayload {
  tipo: 'SUPRIMENTO' | 'SANGRIA';
  valor: number;
  descricao: string;
}
