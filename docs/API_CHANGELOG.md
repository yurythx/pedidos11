# API Change Log

## Migração do Catálogo
- Produtos, Categorias e metadados (imagens, atributos, valores, variações) foram movidos para o app `catalogo`.
- Endpoints antigos sob `/api/v1/vendas/*` relacionados ao catálogo foram descontinuados.
- Use os novos endpoints:
  - `/api/v1/catalogo/produtos`
  - `/api/v1/catalogo/categorias`
  - `/api/v1/catalogo/produtos-imagens`
  - `/api/v1/catalogo/produtos-atributos`
  - `/api/v1/catalogo/produtos-atributos-valores`
  - `/api/v1/catalogo/produtos-variacoes`

## Alias em Cadastro
- Para conveniência, `/api/v1/cadastro/produtos` e `/api/v1/cadastro/categorias` apontam para os ViewSets do catálogo.

## Timeline de Deprecação
- Versão atual: endpoints de catálogo em `vendas` deixam de ser expostos nas rotas e passam a retornar cabeçalho `X-Deprecated` quando utilizados.
- Futuro: remoção definitiva das classes de view de catálogo em `vendas` (apenas endpoints de pedido permanecem).

## Exemplos de Migração
- Listar produtos:
  - Antigo: `GET /api/v1/vendas/produtos?q=nome`
  - Novo: `GET /api/v1/catalogo/produtos?q=nome`
- Lista por categoria:
  - Antigo: `GET /api/v1/vendas/categorias/{slug}/produtos`
  - Novo: `GET /api/v1/catalogo/produtos?categoria={slug}`

