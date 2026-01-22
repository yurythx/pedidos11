import { request } from '@/lib/http/request';

export interface PublicEmpresa {
  nome_fantasia: string;
  slug: string;
  logo: string;
  cor_primaria: string;
  cor_secundaria: string;
  telefone: string;
  endereco_principal: any;
}

export interface PublicProduto {
  id: string;
  nome: string;
  descricao: string;
  preco_venda: string;
  imagem: string;
  grupos_complementos: any[];
}

export interface PublicCategoria {
  id: string;
  nome: string;
  produtos: PublicProduto[];
}

export const publicMenuService = {
  getInfo: (slug: string) => request.get<PublicEmpresa>(`/public/menu/${slug}/info/`),
  getCatalogo: (slug: string) => request.get<PublicCategoria[]>(`/public/menu/${slug}/catalogo/`)
};
