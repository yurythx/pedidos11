# Guia de Integração: Frontend e Mobile

Este guia descreve como integrar aplicações Web (SPA/Next.js) e Mobile (React Native/Flutter) com a API do Projeto Nix. Foque em autenticação JWT, consumo de endpoints, paginação, filtros, rate limiting, upload de arquivos e boas práticas de segurança.

## Base da API
- Base URL: http://localhost:8000/
- Documentação interativa: /api/docs
- Schema OpenAPI: /api/schema
- Endpoints principais: /api/*
- Autenticação (JWT): /api/auth/*

## Autenticação JWT
- Obter token:
```http
POST /api/auth/token/
Content-Type: application/json
{
  "username": "<usuario>",
  "password": "<senha>"
}
```
- Resposta inclui access, refresh e user; o access deve ser enviado no header:
```
Authorization: Bearer <access_token>
```
- Renovar token:
```http
POST /api/auth/token/refresh/
{
  "refresh": "<refresh_token>"
}
```
- Verificar token:
```http
POST /api/auth/token/verify/
{
  "token": "<access_token>"
}
```
- Claims úteis no token: empresa_id, nome_empresa, cargo, permissions, flags de papel (is_admin, is_gerente, is_vendedor).

## Multi-tenancy
- Todo acesso é automaticamente filtrado pela empresa do usuário autenticado (multi-tenancy).
- Não há cabeçalho extra para tenant; o escopo vem do usuário.

## CORS
- Origem permitida configurável via variável de ambiente: CORS_ALLOWED_ORIGINS (padrão inclui http://localhost:3000).
- Para mobile (emuladores), use base URL acessível e configure CORS conforme necessário.

## Paginação, Filtros e Ordenação
- Padrão de paginação: Page Number.
- Resposta paginada:
```json
{
  "count": 123,
  "next": "http://.../api/produtos/?page=3",
  "previous": null,
  "page_size": 50,
  "total_pages": 3,
  "current_page": 2,
  "results": [ ... ]
}
```
- Parâmetros:
  - page, page_size (máximo 1000)
  - filtros específicos por recurso (ex.: produtos: preco_min, preco_max, tipo, search)
  - ordering por campos suportados (ex.: ?ordering=nome)

## Rate Limiting (Throttling)
- 401/403 para autenticação/permissões.
- 429 para limites excedidos.
- Limites:
  - Usuários autenticados: 10.000/dia
  - Burst: 60/min
  - Sustentado: 1000/h
  - Vendas: 100/min
  - Relatórios: 10/min

## Uploads (NFe XML)
- Upload de NFe:
```
POST /api/nfe/importacao/upload-xml/
Form-Data: arquivo=@nfe.xml
```
- Preview retorna fornecedor, identificação, itens e sugestões de produto/matching.
- Confirmação da importação:
```
POST /api/nfe/importacao/confirmar/
Content-Type: application/json
{
  "deposito_id": "<uuid>",
  "numero_nfe": "12345",
  "serie_nfe": "1",
  "fornecedor": { "cnpj": "...", "nome": "..." },
  "itens": [
    {
      "codigo_xml": "...",
      "produto_id": "<uuid>",
      "fator_conversao": 12,
      "qtd_xml": 10,
      "preco_custo": 48.00,
      "lote": { "codigo": "LOTE2026", "validade": "2026-12-31" }
    }
  ]
}
```

### Upload Multipart em React Native
```javascript
import { Platform } from 'react-native';

async function uploadNFeXML(token, uri) {
  const form = new FormData();
  form.append('arquivo', {
    uri,
    name: 'nfe.xml',
    type: 'text/xml',
  });

  const res = await fetch('http://localhost:8000/api/nfe/importacao/upload-xml/', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      // Content-Type será definido automaticamente pelo fetch para multipart/form-data
    },
    body: form,
  });
  if (!res.ok) throw new Error(`Upload falhou: ${res.status}`);
  return res.json();
}
```

### Upload Multipart em Flutter
```dart
import 'dart:io';
import 'package:http/http.dart' as http;

Future<http.StreamedResponse> uploadNFeXML(String accessToken, String filePath) async {
  final request = http.MultipartRequest(
    'POST',
    Uri.parse('http://localhost:8000/api/nfe/importacao/upload-xml/'),
  );
  request.headers['Authorization'] = 'Bearer $accessToken';
  request.files.add(await http.MultipartFile.fromPath(
    'arquivo',
    filePath,
    contentType: MediaType('text', 'xml'), // opcional
  ));
  return request.send();
}
```

## Recursos Comuns
- Catálogo:
  - GET /api/produtos/?search=coca&preco_min=10&preco_max=100
  - POST /api/produtos/ (dados do produto; empresa é atribuída automaticamente)
- Estoque:
  - GET /api/lotes/?validade_min=2026-01-01
  - POST /api/movimentacoes/ (entrada/saída com depósito e produto)
- Vendas:
  - POST /api/vendas/ (criar venda) → itens via /api/itens-venda/
  - Ações customizadas disponíveis conforme documentação Swagger
- Financeiro:
  - GET /api/contas-pagar/?status=ABERTA
  - POST /api/contas-receber/ (lançamentos)
- Restaurante/KDS:
  - GET /api/producao/ (painel de produção)
  - GET /api/dashboard/resumo-dia/

## Exemplos de Cliente

### Axios (Web/SPA)
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access'); // prefira memória/secure storage
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh');
      if (refresh) {
        const { data } = await axios.post('http://localhost:8000/api/auth/token/refresh/', { refresh });
        localStorage.setItem('access', data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return axios(original);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### React Native (fetch)
```javascript
async function getProdutos(token) {
  const res = await fetch('http://localhost:8000/api/produtos/', {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.status === 429) throw new Error('Rate limit excedido');
  return res.json();
}
```

### Flutter (http)
```dart
import 'package:http/http.dart' as http;

Future<http.Response> getProdutos(String accessToken) {
  return http.get(
    Uri.parse('http://localhost:8000/api/produtos/'),
    headers: { 'Authorization': 'Bearer $accessToken' },
  );
}
```

## Segurança e Boas Práticas
- Sempre usar HTTPS em produção.
- Armazenar tokens em local seguro:
  - Web: preferir memória (estado) ou cookies httpOnly; evitar localStorage sempre que possível.
  - Mobile: usar armazenamento seguro (Keychain/EncryptedSharedPreferences/secure storage).
- Renovar tokens com refresh; evitar re-logins desnecessários.
- Respeitar rate limits e tratar 429 com backoff.
- Configurar CORS adequadamente (origens do front/mobile).
- Mobile: usar base URL correta
  - Android Emulator → http://10.0.2.2:8000
  - iOS Simulator → http://localhost:8000
  - Dispositivo físico → IP da máquina (ex.: http://192.168.0.10:8000)

## Descoberta de Endpoints
- Use /api/docs para explorar endpoints, filtros, parâmetros e payloads.
- Use /api/schema para geração automática de clientes (OpenAPI).

## Versionamento
- Versão atual: 1.0.0 (drf-spectacular).
- Para breaking changes, será incluído prefixo de versão em rotas (/api/v2) e changelog.

## Ambiente
- Variáveis relevantes:
  - SECRET_KEY, DEBUG, ALLOWED_HOSTS
  - CORS_ALLOWED_ORIGINS
  - PostgreSQL (produção) ou SQLite (dev)

## Troubleshooting
- 401 Unauthorized: token expirado/inválido → renovar com refresh ou fazer login.
- 403 Forbidden: sem permissão → verificar cargo/roles e endpoint.
- 429 Too Many Requests: respeitar rate limits (backoff exponencial).
- CORS bloqueando requisições: adicionar origem em CORS_ALLOWED_ORIGINS.
- Paginação sem resultados: conferir page, page_size e filtros aplicados.

