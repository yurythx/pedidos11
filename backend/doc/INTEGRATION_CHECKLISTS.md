# Checklists de Integração por Módulo

Use estes checklists para integrar rapidamente cada módulo do backend com o frontend ou mobile, cobrindo as operações essenciais, endpoints e validações.

## Autenticação
- [ ] Obter access/refresh via POST /api/auth/token/
- [ ] Armazenar tokens com segurança (memória/cookies/secure storage)
- [ ] Interceptor para renovar access via /api/auth/token/refresh/
- [ ] Tratar 401/403/429

## Catálogo
- [ ] Listar categorias: GET /api/categorias/
- [ ] Listar produtos: GET /api/produtos/?search=&preco_min=&preco_max=&tipo=
- [ ] Detalhar produto: GET /api/produtos/{id}/
- [ ] Criar/editar produto: POST/PUT /api/produtos/
- [ ] Recalcular custo de composto: POST /api/produtos/{id}/recalcular_custo/
- [ ] Paginação e ordering: page, page_size, ordering

## Estoque
- [ ] Listar depósitos: GET /api/depositos/
- [ ] Consultar saldos: GET /api/saldos/?produto_id=&deposito_id=
- [ ] Movimentação: POST /api/movimentacoes/ (entrada/saída)
- [ ] Lotes: GET /api/lotes/?validade_min=&produto_id=
- [ ] Importar NFe: upload + preview + confirmar (ver seção NFe)

## Vendas
- [ ] Criar venda: POST /api/vendas/
- [ ] Adicionar itens: POST /api/itens-venda/
- [ ] Finalizar venda: PUT/PATCH /api/vendas/{id}/ (status)
- [ ] Cancelar venda: ações conforme API
- [ ] Relatórios/dashboards: GET /api/dashboard/resumo-dia/
- [ ] Rate limit específico (vendas): tratar 429

## Financeiro
- [ ] Contas a receber: GET/POST /api/contas-receber/
- [ ] Contas a pagar: GET/POST /api/contas-pagar/
- [ ] Baixar títulos: ações conforme API
- [ ] Filtros por status/data/valor

## Parceiros
- [ ] Clientes: GET/POST /api/clientes/
- [ ] Fornecedores: GET/POST /api/fornecedores/
- [ ] Integração com NFe: vínculo de produtos do fornecedor

## Restaurante/KDS
- [ ] Mesas e comandas: GET/POST /api/mesas/, /api/comandas/
- [ ] Painel de produção: GET /api/producao/
- [ ] Dashboard do dia: GET /api/dashboard/resumo-dia/

## NFe (Importação)
- [ ] Upload XML: POST /api/nfe/importacao/upload-xml/ (multipart)
- [ ] Validar/preview: resposta com fornecedor, identificação, itens e sugestões
- [ ] Confirmar importação: POST /api/nfe/importacao/confirmar/
- [ ] Tratamento de lotes/validade: itens com rastreabilidade

## Padrões de UX/Erro
- [ ] Feedback para 401/403/429 com mensagens claras
- [ ] Estados de carregamento e paginação
- [ ] Reintentos exponenciais para 429
- [ ] Log mínimo (sem dados sensíveis)

## Ambiente e Configuração
- [ ] CORS para origens do front/mobile
- [ ] Base URL adequada (emuladores/dispositivo físico)
- [ ] Variáveis .env para API base, tempo de expiração, etc.

