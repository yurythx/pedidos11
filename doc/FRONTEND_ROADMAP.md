# Roadmap Detalhado do Frontend (Projeto Nix)

Este roadmap orienta a implementação do frontend (Web) alinhado ao backend já funcional. Baseia-se na documentação de integração e nos endpoints disponíveis.

## Objetivos
- Autenticação JWT robusta com guardas de rota e menus por cargo (RBAC)
- CRUDs principais: usuários, clientes, fornecedores, endereços, estoque, catálogo, vendas, financeiro
- NFe: upload/preview/confirmar com feedback claro
- KDS e dashboards operacionais
- DX e qualidade: testes, acessibilidade, performance, documentação

## Fundamentos
- Stack: Next.js (App Router), TypeScript, Axios (conforme guia), CSS utilitário (já presente), ícones/suporte UI
- Config: `.env` com BASE_URL; CORS no backend conforme INTEGRATION_GUIDE
- Cliente HTTP: interceptors para Authorization e refresh; tratamento de 401/403/429
- Estado: caches por página (server actions ou SWR opcional); uso de paginação e filtros da API
- RBAC: menu e rotas condicionados ao cargo (`ADMIN`, `GERENTE`, `VENDEDOR`, etc.)

## Fase 0 — Setup e Infra
- Criar estrutura `/frontend` separada com:
  - app/: layout, rotas
  - src/lib/http/: axios client (com interceptors e refresh)
  - src/config/env.ts: baseURL
  - src/features/auth/: login e guarda
  - src/components/layout/: Shell, Sidebar, Header (avatar)
- Integração com documentação:
  - [INTEGRATION_GUIDE_FRONT_MOBILE.md](./INTEGRATION_GUIDE_FRONT_MOBILE.md)
  - [POSTMAN_COLLECTION.json](./POSTMAN_COLLECTION.json)
  - [OPENAPI_CLIENTS.md](./OPENAPI_CLIENTS.md)

## Fase 1 — Autenticação e Shell
- Telas:
  - Login (username/password) → salva access/refresh
  - Recuperação básica de sessão (refresh)
- Rotas:
  - Guardas para rotas autenticadas
  - RBAC: exibir menus por cargo
- Header:
  - Avatar do usuário, nome e empresa
  - Menu de perfil e sair

## Fase 2 — Usuários e Perfil
- Endpoints:
  - GET/POST/PUT/DELETE `/api/usuarios/` (admin/gerente)
  - GET/PATCH `/api/usuarios/me/` (foto_perfil, dados pessoais)
- Telas:
  - Lista/Detalhe/Editar usuários (com paginação/ordenar)
  - Perfil do usuário logado (upload de foto)
- Validações:
  - E-mail obrigatório; máscara de telefone

## Fase 3 — Parceiros e Endereços
- Endpoints:
  - Clientes: `/api/clientes/`
  - Fornecedores: `/api/fornecedores/`
  - Endereços genéricos: `/api/enderecos/` com `content_type` e `object_id`
- Telas:
  - Listar/CRUD clientes e fornecedores
  - Aba Endereços nas entidades (cobrança/entrega/etc.)
- UX:
  - Autocomplete de CEP; validação de UF; exibição formato brasileiro

## Fase 4 — Catálogo
- Endpoints:
  - `/api/produtos/`, `/api/categorias/`, `/api/fichas-tecnicas/`
  - Ação: `POST /api/produtos/{id}/recalcular_custo/`
- Telas:
  - Lista/CRUD de produtos com filtros (tipo, preço, busca)
  - Ficha técnica (BOM) com cálculo de custo
- UX:
  - Paginação; ordenação; destaque de produtos compostos

## Fase 5 — Estoque
- Endpoints:
  - `/api/depositos/`, `/api/saldos/`, `/api/movimentacoes/`, `/api/lotes/`
- Telas:
  - Depósitos e saldos por produto
  - Movimentações (entrada/saída/transferência)
  - Lotes com validade (filtros por data)
- Rate limiting:
  - Tratamento de 429; backoff em operações intensivas

## Fase 6 — Vendas
- Endpoints:
  - `/api/vendas/`, `/api/itens-venda/`
  - Dashboard: `/api/dashboard/resumo-dia/`
- Telas:
  - Criar venda; adicionar itens; finalizar/cancelar
  - Resumo do dia (indicadores)
- Throttling:
  - Escopo `vendas` com 100 req/min → feedback amigável

## Fase 7 — Financeiro
- Endpoints:
  - `/api/contas-receber/`, `/api/contas-pagar/`
- Telas:
  - Lançamentos; filtros por status/data/valor
  - Ações de baixa/liquidação (conforme API)

## Fase 8 — Restaurante/KDS
- Endpoints:
  - `/api/mesas/`, `/api/comandas/`, `/api/producao/`
  - `GET /api/dashboard/resumo-dia/`
- Telas:
  - Gestão de mesas e comandas
  - Painel de produção (KDS)

## Fase 9 — NFe (Upload/Importação)
- Endpoints:
  - `POST /api/nfe/importacao/upload-xml/` (multipart)
  - `POST /api/nfe/importacao/confirmar/`
- Telas:
  - Upload XML → preview: fornecedor, identificação, itens, sugestões
  - Confirmação com seleção de produto e fator de conversão
- CLI auxiliar:
  - `python -m nfe.cli_parse` para debug local com fixtures

## Qualidade e DX
- Testes:
  - Integração (mocks da API), e2e (Playwright/Cypress)
  - Casos de paginação, filtros, 401/403/429
- Acessibilidade:
  - Navegação por teclado; ARIA; contrastes
- Performance:
  - Cache por página; lazy-loading; redução de payloads
- Observabilidade:
  - Logger mínimo de erros (sem dados sensíveis)

## Entregáveis por Fase
- UI funcional com estados (loading, empty, error)
- Integração com endpoints e filtros/paginação
- Testes mínimos e documentação de rotas usadas (linkar ao guia)

## Critérios de Conclusão (Definition of Done)
- Confere com POSTMAN/REST Client e `/api/docs`
- Trata autenticação e rate limiting
- Paginação e filtros funcionam
- Acessibilidade básica OK
- Sem erros no console e sem vazamento de tokens

## Referências
- [INTEGRATION_GUIDE_FRONT_MOBILE.md](./INTEGRATION_GUIDE_FRONT_MOBILE.md)
- [INTEGRATION_CHECKLISTS.md](./INTEGRATION_CHECKLISTS.md)
- [POSTMAN_COLLECTION.json](./POSTMAN_COLLECTION.json)
- [http_examples.http](./http_examples.http)
