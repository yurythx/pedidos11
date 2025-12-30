# API Pedidos11 — Guia de Uso

## Autenticação JWT
- Obter token:
```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'
```
- Resposta:
```json
{ "access": "<ACCESS>", "refresh": "<REFRESH>" }
```
- Usar token:
```bash
curl http://localhost:8000/api/v1/vendas/ \
  -H "Authorization: Bearer <ACCESS>"
```
- Renovar token:
```bash
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<REFRESH>"}'
```

## Documentação
- Swagger UI: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/
- Schema JSON: http://localhost:8000/api/schema/

## Convenções
- Filtro com django-filters via query string (ex.: ?status=aberto)
- Paginação (quando habilitada em prod): PageNumberPagination
- Rate limit: por usuário e escopos em REST_FRAMEWORK

## Módulos e Endpoints Base
- Raiz da API: http://localhost:8000/api/v1/
  - vendas: /api/v1/vendas/
  - estoque: /api/v1/estoque/
  - financeiro: /api/v1/financeiro/
  - compras: /api/v1/compras/
  - relatorios: /api/v1/
  - auditoria: /api/v1/
  - cadastro: /api/v1/cadastro/
  - catalogo: /api/v1/catalogo/

## Erros Comuns
- 401 Unauthorized: token inválido/ausente.
- 403 Forbidden: sem permissão.
- 429 Too Many Requests: limite de taxa atingido.
- 400/404/500: conforme validação/erros do servidor.

## Boas Práticas
- Preferir /api/docs e /api/redoc para descobrir endpoints.
- Versionar clientes usando o schema exportado.
- Manter o header Authorization e content-types corretos.
