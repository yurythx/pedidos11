import { request } from '../../../lib/http/request'
import { GerarNFePayload, NFe, NFeFilter, TransmissaoResultado } from '../types'

const BASE_URL = '/nfe/emissao'

export const nfeService = {
  list: (filter?: NFeFilter & { page?: number, page_size?: number }) => {
    return request.get<{ results: NFe[], count: number }>(`${BASE_URL}/`, { params: filter })
  },

  getById: (id: string) => {
    return request.get<NFe>(`${BASE_URL}/${id}/`)
  },

  gerarDeVenda: (payload: GerarNFePayload) => {
    return request.post<NFe>(`${BASE_URL}/gerar-de-venda/`, payload)
  },

  transmitir: (id: string) => {
    return request.post<TransmissaoResultado>(`${BASE_URL}/${id}/transmitir/`)
  },

  gerarXml: (id: string) => {
    return request.post<{ xml: string }>(`${BASE_URL}/${id}/gerar-xml/`)
  },

  consultarRecibo: (recibo: string) => {
    return request.post<TransmissaoResultado>(`${BASE_URL}/consultar-recibo/`, { recibo })
  }
}
