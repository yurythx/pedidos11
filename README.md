# Backend Delivery (Django + DRF) — Documentação de Implantação

## Visão Geral
- Backend de vendas de produtos, expondo API REST para um front-end em Next.js.
- Stack: Django 5.x, Django REST Framework, SimpleJWT, CORS Headers, Pillow.
- Padrões SOLID aplicados com separação em camadas: Models, Serializers, Services, ViewSets, Permissions.
- Versionamento de API em `/api/v1/`.

## Estrutura do Projeto
```
pedidos11/
├── core/
│   ├── settings.py
│   └── urls.py
├── vendas/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   ├── urls_api.py
│   └── permissions.py
├── estoque/
├── financeiro/
├── relatorios/
├── auditoria/
├── manage.py
└── README.md
```

## Setup Local
- Requisitos: Python 3.12+, pip, virtualenv.
- Passos:
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install "Django>=5,<6" djangorestframework djangorestframework-simplejwt django-cors-headers pillow
.\.venv\Scripts\python manage.py makemigrations
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```
- Criar usuário admin:
```bash
.\.venv\Scripts\python manage.py createsuperuser
```

## Configurações Principais
- Settings: [settings.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/core/settings.py)
- INSTALLED_APPS: `rest_framework`, `corsheaders`, `vendas`, `estoque`, `financeiro`, `relatorios`, `auditoria`.
  - Middleware: `corsheaders.middleware.CorsMiddleware`.
  - REST_FRAMEWORK: autenticação `JWTAuthentication`.
  - CORS_ALLOWED_ORIGINS: `http://localhost:3000`.
  - Media: `MEDIA_URL=/media/`, `MEDIA_ROOT=media/`.
- URLs do projeto: [urls.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/core/urls.py)
  - Inclui `api/v1/` (roteamento dos viewsets) e serve media em DEBUG.
  - Índice HTML/JSON em `GET /api/v1/` e schema OpenAPI em `GET /api/schema/`.
  - UI interativa de docs (Swagger/Redoc) em `GET /api/docs/`.
- Cadastro:
  - `GET/POST /api/v1/cadastro/fornecedores/` (admin)
  - `GET/POST /api/v1/cadastro/enderecos/` (admin)
  - `GET/POST /api/v1/cadastro/clientes/` (admin)

## Modelagem de Dados
- Arquivo: [models.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/models.py)
- Entidades:
  - Categoria: `nome` único, `slug` único com geração automática.
- Produto: `nome`, `slug` único com fallback incremental, `sku` único (auto quando ausente), `ean` (8-14 dígitos), `unidade` (`UN|CX|KG|LT`), `marca`, `categoria` (FK), `preco` (Decimal), `custo` (Decimal), `descricao`, `imagem`, `disponivel`.
  - Pedido: `usuario`, `slug` único, `status`, `total`, `data_criacao`, `cost_center`.
  - ItemPedido: `pedido`, `produto`, `quantidade`, `preco_unitario`; método `subtotal`.

## Serializers
- Arquivo: [serializers.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/serializers.py)
- ProdutoSerializer:
  - Usa `categoria` como SlugRelatedField
  - Exibe `categoria_nome`, `slug` como somente leitura
- CategoriaSerializer:
  - Básico para listagem de categorias.
- PedidoSerializer:
  - Campo `itens_payload` (write_only) com lista `{produto: <slug>, quantidade: <int>}`
  - Valida disponibilidade de produtos
  - Cria pedido, itens e calcula `total`; integra estoque e financeiro

## Services (Regra de Negócio)
- Arquivo: [services.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/services.py)
- ProdutoService:
  - `disponiveis()`, `buscar_por_slug(slug)`, `filtrar(categoria_slug, texto)`
- PedidoService:
  - `validate_disponibilidade(itens_payload)`: garante que todos os produtos existem e estão disponíveis.
  - `criar_itens(pedido, itens_payload)`: cria `ItemPedido` com `preco_unitario` do Produto.
  - `calcular_total(itens)`: soma subtotais com precisão Decimal.

## ViewSets e Permissões
- Arquivo: [views.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/views.py)
- ProdutoViewSet:
  - `lookup_field='slug'`.
  - Leitura pública; escrita restrita a staff (`IsAdminOrReadOnly`).
  - Filtros simples via query params: `categoria`, `q` (texto).
- CategoriaViewSet:
  - Leitura pública; `@action produtos` retorna produtos disponíveis da categoria.
- PedidoViewSet:
  - `IsAuthenticated`.
  - Usuário comum vê apenas seus pedidos; staff vê todos.
  - `IsOwner` no `retrieve`.
- Permissões: Estoque [permissions.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/estoque/permissions.py), Financeiro [permissions.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/financeiro/permissions.py)
  - `IsAdminOrReadOnly` e `IsOwner`.

## Rotas da API
- Arquivo: [urls_api.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/urls_api.py)
- Base: `/api/v1/vendas/`
- Produtos:
  - `GET /api/v1/vendas/produtos/` (filtros avançados: `categoria`, `marca`, `unidade`, `sku`, `ean`, `preco_min`, `preco_max`, e `q` em nome/sku/ean)
  - `GET /api/v1/vendas/produtos/{slug}/`
  - `POST/PUT/PATCH/DELETE` apenas para admin
  - Exemplo de criação (admin):
    ```
    {
      "nome": "Suco de Uva",
      "categoria": "bebidas",
      "preco": "9.90",
      "custo": "6.00",
      "descricao": "Garrafa 1L",
      "disponivel": true,
      "ean": "7891234567890",
      "ncm": "20098900",
      "cfop": "5102",
      "unidade": "UN",
      "marca": "Acme"
    }
    ```
  - Imagens:
    - `GET/POST /api/v1/vendas/produtos-imagens/?produto=<slug>` (admin)
    - Campos: `produto`, `imagem`, `alt`, `pos`
  - Atributos técnicos:
    - Campo `atributos` em Produto (JSON arbitrário)
    - Catálogo de atributos:
      - `GET/POST /api/v1/vendas/produtos-atributos/` (admin)
      - `GET/POST /api/v1/vendas/produtos-atributos-valores/?produto=<slug>&atributo=<codigo>` (admin)
    - Variações de produto:
      - `GET/POST /api/v1/vendas/produtos-variacoes/?produto=<slug>` (admin)
      - Campos: `produto`, `sku`, `nome`, `preco`, `custo`, `disponivel`, `atributos`, `imagem`
- Estoque:
  - `GET /api/v1/estoque/movimentos/` (admin)
  - `POST /api/v1/estoque/movimentos/entrada` (admin)
  - `POST /api/v1/estoque/movimentos/ajuste` (admin)
- `GET /api/v1/estoque/movimentos/saldo?produto=<slug>` (admin)
- `GET /api/v1/estoque/movimentos/historico?produto=<slug>&start=YYYY-MM-DD&end=YYYY-MM-DD` (admin)
 - Recebimentos:
   - `GET /api/v1/estoque/recebimentos/` (admin/operacao)
   - `POST /api/v1/estoque/recebimentos/` com `itens_payload` (admin/operacao)
   - Corpo exemplo:
     ```
     {
       "fornecedor": "Fornecedor X",
       "documento": "NF-123",
       "observacao": "Entrada inicial",
       "itens_payload": [
         {"produto": "suco", "quantidade": 10, "custo_unitario": 5.50},
         {"produto": "agua", "quantidade": 20}
       ]
     }
     ```
  - Depósitos:
    - `GET/POST /api/v1/estoque/depositos/`
    - Saldo por depósito: `GET /api/v1/estoque/movimentos/saldo?produto=<slug>&deposito=<slug>`
    - Histórico por depósito: `GET /api/v1/estoque/movimentos/historico?produto=<slug>&deposito=<slug>&start=YYYY-MM-DD&end=YYYY-MM-DD`
    - Transferência: `POST /api/v1/estoque/movimentos/transferir` com `{"produto":"<slug>","quantidade":X,"origem":"<dep_slug>","destino":"<dep_slug>"}`
  - Motivos de ajuste:
    - `GET/POST /api/v1/estoque/motivos-ajuste/`
    - Ex.: `POST /api/v1/estoque/movimentos/ajuste` com `{"motivo":"INVENTARIO"}`
  - CSV de recebimentos:
    - `GET /api/v1/estoque/recebimentos/csv?fornecedor=<slug>&deposito=<slug>&start=YYYY-MM-DD&end=YYYY-MM-DD`
  - Estornar recebimento:
    - `POST /api/v1/estoque/recebimentos/{id}/estornar/` estorna as quantidades e marca `estornado_em`
- Financeiro:
  - `GET /api/v1/financeiro/lancamentos/` (admin)
  - `GET /api/v1/financeiro/lancamentos/resumo?start=YYYY-MM-DD&end=YYYY-MM-DD&cost_center=LJ1` (admin)
  - `GET /api/v1/financeiro/lancamentos/resumo_csv?cost_center=LJ1` (admin)
  - `GET /api/v1/financeiro/lancamentos/contas_resumo?side=debit|credit&cost_center=LJ1` (admin)
  - `GET /api/v1/financeiro/lancamentos/contas_resumo_csv?side=debit|credit&cost_center=LJ1` (admin)
  - `GET /api/v1/financeiro/lancamentos/centros_resumo?cost_center=LJ1` (admin)
  - `GET /api/v1/financeiro/lancamentos/centros_resumo_csv?cost_center=LJ1` (admin)
  - CRUD Superuser: `GET/POST /api/v1/financeiro/contas/`, `GET/POST /api/v1/financeiro/centros/`, `GET/POST /api/v1/financeiro/defaults/`
- Relatórios:
  - `GET /api/v1/relatorios/faturamento?start=YYYY-MM-DD&end=YYYY-MM-DD&cost_center=LJ1` (admin)
  - `GET /api/v1/relatorios/itens?start=YYYY-MM-DD&end=YYYY-MM-DD&limit=10&cost_center=LJ1&page=1&page_size=10` (admin)
  - `GET /api/v1/relatorios/categorias?start=YYYY-MM-DD&end=YYYY-MM-DD&cost_center=LJ1&page=1&page_size=10` (admin)
  - CSV: `GET /api/v1/relatorios/faturamento_csv`, `itens_csv`, `categorias_csv` (admin)
- Categorias:
  - `GET /api/v1/vendas/categorias/`
  - `GET /api/v1/vendas/categorias/{slug}/produtos/`
- Pedidos:
  - `GET /api/v1/vendas/pedidos/` (apenas do usuário autenticado, admin vê todos)
  - `POST /api/v1/vendas/pedidos/` (criação por itens_payload)
  - `GET /api/v1/vendas/pedidos/{slug}/` (dono ou admin)
- Autenticação (JWT):
  - `POST /api/v1/token/`
  - `POST /api/v1/token/refresh/`

## Exemplos de Uso (cURL)
- Obter token:
```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua_senha"}'
```
- Schema OpenAPI:
```bash
curl http://localhost:8000/api/schema/
```
- UI de documentação:
```bash
start http://localhost:8000/api/docs/
```
 - Na UI, informe o token JWT no campo “Token JWT” para autorizar chamadas protegidas.
- Listar produtos públicos:
```bash
curl http://localhost:8000/api/v1/vendas/produtos/
curl "http://localhost:8000/api/v1/vendas/produtos/?categoria=burgers&q=cheddar"
curl "http://localhost:8000/api/v1/vendas/produtos/?page_size=5&ordering=preco"
```
- Detalhe por slug:
```bash
curl http://localhost:8000/api/v1/vendas/produtos/x-burger
```
- Criar pedido:
```bash
curl -X POST http://localhost:8000/api/v1/vendas/pedidos/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "itens_payload": [
      {"produto": "x-burger", "quantidade": 2},
      {"produto": "suco-laranja", "quantidade": 1}
    ]
  }'
``` 

- Estoque - histórico de movimentos:
```bash
curl "http://localhost:8000/api/v1/estoque/movimentos/historico?produto=x-burger&start=2025-01-01&end=2025-01-31"
curl -OJ "http://localhost:8000/api/v1/estoque/movimentos/historico_csv?produto=x-burger&cost_center=LJ1"
```
 - Estoque - recebimentos:
```bash
curl -X POST http://localhost:8000/api/v1/estoque/recebimentos/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "fornecedor": "fornecedor-x",
    "documento": "NF-123",
    "itens_payload": [
      {"produto": "suco", "quantidade": 10, "custo_unitario": 5.50}
    ]
  }'
```

- Relatórios em CSV:
```bash
curl -OJ "http://localhost:8000/api/v1/relatorios/faturamento_csv?start=2025-01-01&end=2025-01-31&cost_center=LJ1"
curl -OJ "http://localhost:8000/api/v1/relatorios/itens_csv?limit=20&cost_center=LJ1"
curl -OJ "http://localhost:8000/api/v1/relatorios/categorias_csv?start=2025-01-01&end=2025-01-31&cost_center=LJ1"
curl -OJ "http://localhost:8000/api/v1/financeiro/lancamentos/resumo_csv?cost_center=LJ1"
curl -OJ "http://localhost:8000/api/v1/financeiro/lancamentos/contas_resumo_csv?side=debit&cost_center=LJ1"
curl -OJ "http://localhost:8000/api/v1/financeiro/lancamentos/centros_resumo_csv?cost_center=LJ1"
``` 
## Rate Limiting
- Padrões:
  - anon: 50/min
  - user: 200/min
  - financeiro: 60/min
  - estoque: 120/min
  - relatorios: 60/min
- Escopos aplicados:
  - Financeiro: lançamentos, contas, centros, defaults
  - Relatórios: todos os endpoints
  - Estoque: movimentos (entrada, ajuste, saldo, histórico)

## Financeiro: Contas e Centros
- Financeiro: Contas e Centros
- Seed inicial:
```bash
python manage.py seed_accounts
```
- CRUD (somente superuser):
  - `GET/POST /api/v1/financeiro/contas/`
  - `GET/POST /api/v1/financeiro/centros/`
  - `GET/POST /api/v1/financeiro/defaults/` (centro padrão por usuário)
- Uso em pedidos:
  - Campo opcional `cost_center` no payload (ex.: `"LJ1"`). A resposta inclui `cost_center_codigo` e `cost_center_nome`.
- Paginação de relatórios:
  - Use `page` e `page_size`. Metadados em headers: `X-Total-Count`, `X-Page`, `X-Page-Size`.

## RBAC e Headers
- Grupos de acesso:
  - operacao e estoque para endpoints de Estoque
  - financeiro para endpoints de Financeiro
- Criar grupos:
```bash
python manage.py seed_groups
```
- Idempotency-Key:
  - Use o header Idempotency-Key em POST de pedidos e movimentos de estoque
- Cache HTTP:
  - Endpoints de Relatórios e Financeiro retornam ETag e Last-Modified e aceitam If-None-Match

## Políticas de Segurança
- JWT obrigatório para endpoints de pedidos; produtos e categorias são leitura pública.
- CORS liberado para `http://localhost:3000`.
- Não expor SECRET_KEY em produção; usar variáveis de ambiente e `DEBUG=False`.
- `ALLOWED_HOSTS` deve incluir domínio/host do deploy.

## Mídia e Estático
- Uploads de imagem de produto vão para `media/produtos/`.
- Em produção, servir `MEDIA_ROOT` e `STATICFILES` via servidor de arquivos (Nginx/S3).

## Boas Práticas e SOLID
- SRP: regras de negócio em `services.py`; views só orquestram.
- Aberto/Fechado: expandir filtros e regras criando novos métodos de serviço.
- Substituibilidade: extensões de Produto/variações devem respeitar contratos de base.
- Segregação de Interfaces: serializers e views expõem apenas o necessário.
- Inversão de Dependência: views dependem de abstrações (services), não de implementação acoplada.
 - Configuração por ambiente:
   - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `JWT_ACCESS_MINUTES`, `JWT_REFRESH_DAYS`, `PAGE_SIZE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`
   - Em produção: `DEBUG=False`, cookies seguros e HSTS configurados
 - Observabilidade:
   - Logging configurado (console) e pronto para integração com agregadores
 - Padrões de API:
   - Schema OpenAPI em `/api/schema/`, UI em `/api/docs/`, índice em `/api/v1/`
   - Throttling por escopo e Idempotency-Key em POST críticos
 - Segurança:
   - JWT obrigatório nos endpoints sensíveis; CORS restrito por origem
   - `ALLOWED_HOSTS` e redirecionamento SSL em produção
 - Saúde e suporte:
   - Endpoint de health em `/api/health/`

## Troubleshooting
- Erro de migração: rodar `makemigrations` e `migrate`; verificar dependências instaladas.
- Upload de imagem falha: confirmar `MEDIA_ROOT`, permissões do diretório e multipart no request.
- 401 em pedidos: confirmar JWT `Authorization: Bearer <token>` e expiração do token.
- 403 ao criar/editar produtos: verifique se o usuário é staff.

## Próximos Passos (Evolução)
- Filtros avançados com `django-filter` e `DjangoFilterBackend`.
- Paginação DRF (`PAGE_SIZE`) e ordenação.
- Documentação da API com `drf-spectacular` ou `drf-yasg`.
- Admin registrations e actions para gestão de catálogo.
- Testes unitários e de integração (pytest/django test) para services e serializers.
- Webhooks/Signals para status de pedidos e notificações.
- Dockerização e CI/CD.

## Deploy (Resumo)
- Configurar variáveis:
  - `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, DB (PostgreSQL recomendado), storage de mídia.
- Rodar migrações e criar superuser.
- Servir via ASGI/WSGI (gunicorn/uvicorn) atrás de Nginx.
- Configurar CORS para o domínio do frontend.

## Referências de Código
- Settings: [settings.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/core/settings.py)
- Projeto URLs: [urls.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/core/urls.py)
- Models: [models.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/models.py)
- Serializers: [serializers.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/serializers.py)
- Services: [services.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/services.py)
- ViewSets: [views.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/views.py)
- Rotas API: [urls_api.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/vendas/urls_api.py)
- Permissões: Estoque [permissions.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/estoque/permissions.py), Financeiro [permissions.py](file:///c:/Users/yuri.menezes/Desktop/Projetos/pedidos11/financeiro/permissions.py)
