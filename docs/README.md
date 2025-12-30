# Pedidos11 — Documentação da Aplicação

## Visão Geral
Aplicação de vendas com módulos de cadastro, estoque, financeiro, compras e auditoria. Usa Django e DRF, com JWT para autenticação, filtros com django-filters e caching leve via ETag/Last-Modified em endpoints críticos.

## Arquitetura por Aplicativo
- Cadastro: modelos [Address](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/cadastro/models.py#L6-L20), [Supplier](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/cadastro/models.py#L22-L44) e [Customer](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/cadastro/models.py#L46-L68).
- Catálogo: produtos, categorias, imagens, atributos, variações. Modelos espelham as tabelas de vendas para transição suave. API e admin em [catalogo](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/catalogo).
- Vendas: criação de pedidos com validações e integrações com estoque e financeiro. Serializers em [serializers.py](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/vendas/serializers.py).
- Estoque: depósitos, movimentos e recebimentos com itens. Modelos em [models.py](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/estoque/models.py).
- Financeiro: razão (LedgerEntry), contas, centros, títulos (AR/AP) e parcelas. Views em [views.py](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/financeiro/views.py) e serviços em [services.py](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/financeiro/services.py).
- Compras: ordens e itens de compra. Modelos em [models.py](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/compras/models.py).
- Auditoria: logs e idempotência. Modelos em [models.py](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/auditoria/models.py).

## Fluxos Principais
- Pedido à vista:
  1. Criação do pedido
  2. Saída de estoque
  3. Registro contábil: Caixa x Receita de Vendas
  4. Registro COGS: Custo das Vendas x Estoque
- Pedido a prazo:
  1. Criação com parcelas (soma deve igualar total; due_date ISO)
  2. Saída de estoque
  3. Registro contábil: Clientes x Receita de Vendas
  4. Geração de Title AR e TitleParcel conforme parcelas
  5. Registro COGS

## Títulos (AR/AP) e Parcelas
- Operações:
  - Receber/Pagar título (baixa parcial/total)
  - Receber/Pagar parcela
  - Atualizar/Remover parcela (restrições: não editável se quitada; não remove se valor_pago > 0)
- Endpoints relevantes:
  - Listagem CSV, filtros e ordenação em [TitleViewSet.csv](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/financeiro/views.py#L942-L965)
  - Aging por due_date em [a_receber_aging_due](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/financeiro/views.py#L749-L793)
  - Livro-caixa em [livro_caixa](file:///c:/Users/allle/OneDrive/Área%20de%20Trabalho/Projetos/pedidos11/financeiro/views.py#L586-L626)

## Estoque
- Movimentos: IN/OUT/ADJUST com vínculos a pedido, depósito e motivo de ajuste.
- Recebimentos e itens vinculados a compras.
- Admin com exportações CSV e edição inline.

## Admin
- Catálogo: administração de produtos e categorias; imagens, atributos, valores e variações.
- Vendas: ações para gerar AR, recalcular totais, exportar CSV (somente pedidos e itens).
- Financeiro: receber/pagar, marcar atrasados, exportar CSV; parcelas inline.
- Estoque: exportar movimentos/recebimentos, itens inline.
- Compras: gerar AP e recalcular total.
- Auditoria: edição de logs e chaves.
- Branding: cabeçalho personalizado e admindocs (/admin/doc).

## Segurança e Confiabilidade
- JWT com lifetimes configuráveis.
- Idempotência em criações críticas (ex.: pedido).
- ETag/Last-Modified em endpoints de listagem/CSV para cache eficiente.
- Throttling por escopo (financeiro, estoque, relatórios).

## Testes
- 44 testes cobrindo:
  - Estoque: entradas, saídas, ajustes e estorno
  - Financeiro: aging, livro-caixa, AR/AP e parcelas
  - Vendas: criação de pedidos, validações e integrações
  - Compras: geração de AP e pagamento

## Endpoints Principais
- Root: [ApiRoot](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/core/urls.py#L29-L47)
- Catálogo: /api/v1/catalogo/
- Vendas: /api/v1/vendas/
- Estoque: /api/v1/estoque/
- Financeiro: /api/v1/financeiro/
- Compras: /api/v1/compras/
- Cadastro: /api/v1/cadastro/
- Auditoria: /api/v1/auditoria/
- Admin: /admin/ e /admin/doc/

## Deprecação de Endpoints de Catálogo em Vendas
- Os endpoints de produtos/categorias (e metadados) sob /api/v1/vendas foram descontinuados e retornam o cabeçalho X-Deprecated: "Use /api/v1/catalogo/*".
- Utilize os endpoints equivalentes sob /api/v1/catalogo. Após período de migração, as rotas antigas podem ser removidas definitivamente.

## Change Log
- Veja detalhes e exemplos de migração em [API_CHANGELOG.md](file:///c:/Users/allle/OneDrive/%C3%81rea%20de%20Trabalho/Projetos/pedidos11/docs/API_CHANGELOG.md)

## Nomes de Rotas (basenames)
- Catálogo:
  - catalogo-produto, catalogo-categoria
  - catalogo-produto-imagem, catalogo-produto-atributo, catalogo-produto-atributo-valor, catalogo-produto-variacao
- Vendas:
  - pedido

## Convenções
- Slugs autogerados e imutáveis (readonly no admin).
- Docstrings em classes e funções descrevem finalidade e uso.
- Preferência por operações atômicas em serviços financeiros e de estoque.
