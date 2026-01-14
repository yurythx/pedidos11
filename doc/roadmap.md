# ProjetoRavenna - Roadmap de Implementação

## ✅ Módulos Implementados

- [x] **core** - Infraestrutura multi-tenancy (TenantModel, TenantManager)
- [x] **locations** - Endereços genéricos (Endereco com GenericFK)
- [x] **catalog** - Catálogo de produtos (Categoria, Produto)
- [x] **stock** - Gestão de estoque (Deposito, Saldo, Movimentacao)
- [x] **sales** - Vendas (Venda, ItemVenda, VendaService)

---

## 🎯 Próximos Passos (Ordem de Prioridade)

### FASE 1: Apps Fundamentais (CRÍTICO)

Sem esses apps, nada funciona. Prioridade máxima.

#### 1.1. App `tenant` (Empresas)
- [ ] Criar model `Empresa`
  - Campos: nome, razao_social, cnpj, is_active
  - Configurações: logo, tema, preferências
- [ ] Manager customizado para empresas
- [ ] Validação de CNPJ

**Estimativa:** 30 minutos  
**Dependências:** Nenhuma  
**Impacto:** 🔴 CRÍTICO (todos os outros models dependem)

---

#### 1.2. App `authentication` (Usuários e Autenticação)
- [ ] Criar model `CustomUser` (extends AbstractUser)
  - Campo `empresa` (ForeignKey para tenant.Empresa)
  - Campo `cargo` (Vendedor, Gerente, Admin)
  - Campo `permissoes_customizadas`
- [ ] Authentication backend customizado
- [ ] JWT Token configuration (opcional)
- [ ] Signals para criar perfil padrão

**Estimativa:** 45 minutos  
**Dependências:** tenant  
**Impacto:** 🔴 CRÍTICO (sales.Venda depende)

---

#### 1.3. App `partners` (Clientes e Fornecedores)
- [ ] Model `Cliente`
  - Campos: nome, cpf_cnpj, email, telefone
  - Tipo: Pessoa Física / Jurídica
  - Relacionamento com Endereco (GenericFK)
- [ ] Model `Fornecedor`
  - Similar a Cliente
  - Campos adicionais: prazo_entrega, condicao_pagamento
- [ ] Validações de CPF/CNPJ

**Estimativa:** 1 hora  
**Dependências:** authentication, locations  
**Impacto:** 🔴 CRÍTICO (sales.Venda.cliente depende)

---

### FASE 2: Módulo Financeiro (IMPORTANTE)

#### 2.1. App `financial` (Contas a Pagar/Receber)
- [ ] Model `ContaReceber`
  - Origem: Venda
  - Campos: valor, data_vencimento, data_pagamento, status
- [ ] Model `ContaPagar`
  - Origem: Compra (futuro)
  - Campos similares a ContaReceber
- [ ] Model `FormaPagamento`
  - Parcelamento, juros, desconto
- [ ] Service: `FinanceiroService`
  - Gerar contas a partir de vendas
  - Baixar pagamentos
  - Calcular juros/multas

**Estimativa:** 2 horas  
**Dependências:** sales, partners  
**Impacto:** 🟡 IMPORTANTE (para controle financeiro)

---

### FASE 3: API REST (IMPORTANTE)

#### 3.1. Django Rest Framework Setup
- [ ] Instalar DRF e drf-spectacular
- [ ] Configurar settings (REST_FRAMEWORK)
- [ ] Configurar autenticação (TokenAuth ou JWT)
- [ ] Configurar documentação (Swagger/ReDoc)

**Estimativa:** 30 minutos  
**Dependências:** Todos os models  
**Impacto:** 🟡 IMPORTANTE (para frontend)

---

#### 3.2. Serializers e ViewSets

**Catalog API:**
- [ ] CategoriaSerializer + ViewSet
- [ ] ProdutoSerializer + ViewSet
- [ ] Filtros e busca

**Stock API:**
- [ ] DepositoSerializer + ViewSet
- [ ] SaldoSerializer (read-only)
- [ ] MovimentacaoSerializer + ViewSet
- [ ] Endpoint customizado: `/api/stock/consultar-saldo/`

**Sales API:**
- [ ] VendaSerializer + ViewSet
- [ ] ItemVendaSerializer (nested)
- [ ] Actions customizadas:
  - `/api/vendas/{id}/finalizar/`
  - `/api/vendas/{id}/cancelar/`
  - `/api/vendas/{id}/validar-estoque/`

**Partners API:**
- [ ] ClienteSerializer + ViewSet
- [ ] FornecedorSerializer + ViewSet

**Estimativa:** 3 horas  
**Dependências:** DRF setup  
**Impacto:** 🟡 IMPORTANTE (integração frontend)

---

### FASE 4: Configuração Django (NECESSÁRIO)

#### 4.1. Settings e URLs
- [ ] Configurar `settings.py`
  - INSTALLED_APPS (todos os apps)
  - DATABASE (PostgreSQL)
  - Multi-tenancy middleware
  - CORS headers
- [ ] Configurar `urls.py`
  - Admin
  - API routes
  - Documentação
- [ ] Arquivo `.env` para variáveis de ambiente

**Estimativa:** 45 minutos  
**Dependências:** Todos os apps  
**Impacto:** 🟡 NECESSÁRIO (para rodar)

---

#### 4.2. Migrations
- [ ] Criar migrations para todos os apps
  - Ordem: tenant → core → authentication → locations → catalog → stock → partners → sales → financial
- [ ] Executar migrate
- [ ] Criar fixtures de dados iniciais
  - Empresa padrão
  - Usuário admin
  - Categorias exemplo
  - Depósito padrão

**Estimativa:** 30 minutos  
**Dependências:** Todos os models  
**Impacto:** 🟡 NECESSÁRIO (para rodar)

---

### FASE 5: Testes (RECOMENDADO)

#### 5.1. Tests Unitários
- [ ] Tests para `core.TenantManager`
- [ ] Tests para `stock.Movimentacao` (race conditions)
- [ ] Tests para `sales.VendaService`
  - Finalização com estoque OK
  - Finalização com estoque insuficiente
  - Cancelamento
  - Rollback em erros

**Estimativa:** 2 horas  
**Dependências:** Todos os models  
**Impacto:** 🟢 RECOMENDADO (qualidade)

---

#### 5.2. Tests de Integração
- [ ] Fluxo completo: Criar venda → Finalizar → Verificar estoque
- [ ] Fluxo de cancelamento
- [ ] Múltiplas empresas (isolamento)

**Estimativa:** 1 hora  
**Dependências:** Tests unitários  
**Impacto:** 🟢 RECOMENDADO (qualidade)

---

### FASE 6: Features Avançadas (OPCIONAL)

#### 6.1. Compras e Entrada de Estoque
- [ ] App `purchases` (Compras)
- [ ] Model `Compra`, `ItemCompra`
- [ ] Service para entrada de estoque

**Estimativa:** 3 horas  
**Impacto:** 🟢 OPCIONAL (para ciclo completo)

---

#### 6.2. Relatórios e Dashboard
- [ ] Vendas por período
- [ ] Produtos mais vendidos
- [ ] Estoque mínimo/crítico
- [ ] Contas a receber em atraso

**Estimativa:** 4 horas  
**Impacto:** 🟢 OPCIONAL (analytics)

---

#### 6.3. Integrações
- [ ] Integração fiscal (NFe, NFCe)
- [ ] Gateway de pagamento
- [ ] Email notifications

**Estimativa:** 8+ horas  
**Impacto:** 🟢 OPCIONAL (produção avançada)

---

## 📋 Resumo por Prioridade

### 🔴 CRÍTICO (Fazer Agora)
1. **tenant** - Model Empresa (30min)
2. **authentication** - CustomUser (45min)
3. **partners** - Cliente e Fornecedor (1h)
4. **Configuração Django** - Settings e migrations (1h15)

**Total CRÍTICO:** ~3h30min

---

### 🟡 IMPORTANTE (Fazer em Seguida)
5. **financial** - Contas a pagar/receber (2h)
6. **API REST** - DRF setup + serializers/viewsets (3h30)

**Total IMPORTANTE:** ~5h30min

---

### 🟢 RECOMENDADO (Fazer Depois)
7. **Testes** - Unitários e integração (3h)
8. **Features Avançadas** - Compras, relatórios, integrações (15h+)

---

## 🎯 Sugestão de Sequência

### Opção A: Mínimo Viável (MVP)
```
1. tenant (30min)
2. authentication (45min)
3. partners (1h)
4. Configuração Django (1h15)
5. Testar manualmente no Django Admin
```
**Total: ~3h30min → Backend funcional para testes**

### Opção B: Pronto para Produção
```
1-4. Apps críticos (3h30)
5. financial (2h)
6. API REST completa (3h30)
7. Tests (3h)
8. Deploy básico (1h)
```
**Total: ~13h → Sistema completo e testado**

### Opção C: Sistema Completo
```
1-7. Tudo acima (12h)
8. Compras (3h)
9. Relatórios (4h)
10. Integrações (8h+)
```
**Total: ~27h+ → ERP/PDV profissional**

---

## ❓ Qual caminho seguir?

**Recomendação:** Começar pela **Opção A (MVP)** para ter algo funcionando rápido, depois evoluir.

### Próxima Sprint (Sugestão)
1. ✅ Implementar `tenant.Empresa`
2. ✅ Implementar `authentication.CustomUser`
3. ✅ Implementar `partners.Cliente` e `partners.Fornecedor`
4. ✅ Configurar Django (settings, urls, migrations)
5. ✅ Testar no Django Admin

**Após isso, já teremos um sistema funcional para testes manuais!**

---

## 🚀 Começamos por qual?

Sugiro começarmos pelos **apps críticos** na ordem:
1. **tenant** (é a base de tudo)
2. **authentication** (usuários)
3. **partners** (clientes/fornecedores)

Me diga qual você prefere ou se quer que eu implemente tudo em sequência! 💪
