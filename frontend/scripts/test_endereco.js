const axios = require('axios')
;(async () => {
  try {
    const API = process.env.API || 'http://192.168.1.121:8002/api'
    const r = await axios.post(`${API}/auth/token/`, {
      username: 'admin',
      password: 'admin123',
    })
    const access = r.data.access
    const c = axios.create({
      baseURL: API,
      headers: { Authorization: `Bearer ${access}` },
    })
    const clientes = await c.get('/clientes/?page_size=1')
    const cli = (clientes.data.results || clientes.data)[0]
    const clienteId = cli.id
    const res = await c.post('/enderecos/', {
      content_type: 'partners.cliente',
      object_id: clienteId,
      tipo: 'ENTREGA',
      cep: '01310-000',
      logradouro: 'Av. Paulista',
      numero: '1000',
      complemento: 'Conj 1',
      bairro: 'Bela Vista',
      cidade: 'São Paulo',
      uf: 'SP',
      referencia: 'Próximo ao MASP',
    })
    console.log('ok', res.status, res.data)
  } catch (e) {
    console.error('err', e.response && e.response.status, e.response && e.response.data)
  }
  process.exit(0)
})()
