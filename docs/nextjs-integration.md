# Integração com Next.js

## Autenticação
1. Use POST /api/v1/token/ para obter `access` e `refresh`.
2. Envie Authorization: Bearer `<access>` em todas as requisições.
3. Renove com POST /api/v1/token/refresh/ quando necessário.

## SDK
Local: `clients/ts/sdk.ts`
Funções principais: `login`, `refresh`, `listProdutos`, `getProduto`, `listCategorias`, `listCategoriaProdutos`, `criarPedido`, `relatoriosDashboard`.

## Exemplo
```ts
import { login, listProdutos, criarPedido, relatoriosDashboard } from '../clients/ts/sdk';

const baseUrl = 'http://localhost:8000';

async function demo() {
  const auth = await login(baseUrl, 'admin', 'p');
  const produtos = await listProdutos(baseUrl, auth.access, { ordering: 'preco' });
  const pedido = await criarPedido(baseUrl, auth.access, [{ produto: produtos[0].slug, quantidade: 2 }], 'LJ1');
  const dash = await relatoriosDashboard(baseUrl, auth.access);
  return { produtos, pedido, dash };
}
```

## CORS e Produção
- Ajuste `CORS_ALLOWED_ORIGINS` em `core/settings.py`.
- Configure `ALLOWED_HOSTS` e variáveis de ambiente (DEBUG, SECURE_*).
- Em produção, apenas JSON renderer ativo.

## Descoberta
- Índice: GET `/api/v1/`
- Schema: GET `/api/schema/`
- Health: GET `/api/health/`
