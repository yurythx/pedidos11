# 🎯 ROADMAP IMPLEMENTAÇÃO - Sprints 2 e 3

**Status:** ✅ Produtos Completo | 🚧 Em Progresso  
**Atualizado:** 25/01/2026 16:15

---

## ✅ CONCLUÍDO (Semana 5)

### CRUD Produtos - 100% ✨

**Arquivos criados:** 11
- [x] Types e interfaces
- [x] API clients (produtos e categorias)
- [x] Hooks com React Query
- [x] Componentes (List, Filters, Card)
- [x] Páginas (Lista, Criar, Editar)
- [x] Utilitários (currency)

**Funcionalidades:**
- [x] Listagem com paginação
- [x] Filtros avançados (busca, categoria, tipo, preço, status)
- [x] Ordenação
- [x] Criar produto com validação Zod
- [x] Editar produto
- [x] Deletar com confirmação
- [x] Cálculo automático de margem
- [x] Cards visuais
- [x] Loading states
- [x] Tratamento de erros

**Progresso Frontend:** 30% → 40% 📈

---

## 🚧 PRÓXIMO: Semana 6 - Gestão de Estoque

### Objetivo
Sistema completo de controle de estoque com movimentações e lotes.

### Features

#### 1. Depósitos (1 dia)
- [ ] CRUD de depósitos
- [ ] Marcar depósito padrão
- [ ] Visualizar saldos por depósito

#### 2. Saldos de Estoque (1 dia)
- [ ] Listar saldos por produto
- [ ] Filtrar por depósito
- [ ] Alertas de estoque mínimo/máximo
- [ ] Dashboard de estoque

#### 3. Movimentações (2 dias)
- [ ] Entrada de mercadoria
- [ ] Saída manual
- [ ] Transferência entre depósitos
- [ ] Ajuste de inventário
- [ ] Histórico de movimentações
- [ ] Filtros por data, tipo, produto

#### 4. Lotes (1 dia)
- [ ] Criar/editar lotes
- [ ] Controle de validade
- [ ] Alertas de vencimento
- [ ] Rastreabilidade (FIFO/FEFO)

---

## 📅 Semana 7 - PDV Básico

### Objetivo
Ponto de Venda funcional para realizar vendas.

### Features

#### 1. Carrinho de Compras (1.5 dias)
- [ ] Adicionar produtos ao carrinho
- [ ] Alterar quantidade
- [ ] Remover itens
- [ ] Calcular total
- [ ] Aplicar desconto

#### 2. Finalização de Venda (1.5 dias)
- [ ] Selecionar cliente
- [ ] Escolher forma de pagamento
- [ ] Dividir pagamento
- [ ] Gerar parcelas
- [ ] Confirmar venda

#### 3. Listagem de Vendas (1 dia)
- [ ] Histórico de vendas
- [ ] Filtros por data, status, cliente
- [ ] Detalhes da venda
- [ ] Cancelar venda
- [ ] Reimprimir cupom

---

## 📅 Semana 8 - Financeiro

### Objetivo
Gestão de contas a pagar e receber.

### Features

#### 1. Contas a Receber (2 dias)
- [ ] Listar contas a receber
- [ ] Criar lançamento manual
- [ ] Baixar conta (receber)
- [ ] Filtros por status, vencimento
- [ ] Dashboard de recebimentos

#### 2. Contas a Pagar (2 dias)
- [ ] Listar contas a pagar
- [ ] Criar lançamento manual
- [ ] Baixar conta (pagar)
- [ ] Filtros por fornecedor, vencimento
- [ ] Dashboard de pagamentos

---

## 🎯 SPRINT 3 - Features Avançadas (Semanas 9-12)

### Semana 9 - Gestão de Mesas

#### 1. Mesas (2 dias)
- [ ] Grid visual de mesas
- [ ] Status (livre, ocupada, reservada)
- [ ] Abrir mesa
- [ ] Adicionar pedidos à mesa
- [ ] Transferir mesa
- [ ] Fechar mesa

#### 2. Comandas (2 dias)
- [ ] Criar comanda individual
- [ ] Adicionar itens
- [ ] Transferir itens entre comandas
- [ ] Dividir conta
- [ ] Fechar comanda

---

### Semana 10 - KDS (Kitchen Display System)

#### 1. Painel de Produção (2 dias)
- [ ] Listar pedidos pendentes
- [ ] Filtrar por setor (cozinha, bar)
- [ ] Marcar item como preparando
- [ ] Marcar item como pronto
- [ ] Notificações em tempo real

#### 2. Setores de Produção (1 dia)
- [ ] CRUD de setores
- [ ] Configurar impressoras
- [ ] Tempo médio de preparo

---

### Semana 11 - Upload NFe

#### 1. Upload de XML (2 dias)
- [ ] Drag & drop de arquivo
- [ ] Upload múltiplo
- [ ] Parser de XML
- [ ] Preview de dados
- [ ] Validação

#### 2. Importação (2 dias)
- [ ] Matching de produtos
- [ ] Sugestões de produto
- [ ] Fator de conversão
- [ ] Criar produto novo
- [ ] Confirmar importação
- [ ] Gerar movimentação de estoque

---

### Semana 12 - Otimizações e Deploy

#### 1. Performance (2 dias)
- [ ] Code splitting
- [ ] Lazy loading de componentes
- [ ] Image optimization
- [ ] Bundle size reduction
- [ ] Cache strategies

#### 2. Deploy (2 dias)
- [ ] Configurar CI/CD
- [ ] Build otimizado
- [ ] Testes E2E
- [ ] Deploy em staging
- [ ] Deploy em produção

---

## 📊 Métricas de Progresso

| Semana | Feature | Progresso | Status |
|--------|---------|-----------|--------|
| 5 | Produtos | 100% | ✅ Completo |
| 6 | Estoque | 0% | 🔜 Próximo |
| 7 | PDV | 0% | ⏳ Aguardando |
| 8 | Financeiro | 0% | ⏳ Aguardando |
| 9 | Mesas | 0% | ⏳ Aguardando |
| 10 | KDS | 0% | ⏳ Aguardando |
| 11 | NFe | 0% | ⏳ Aguardando |
| 12 | Deploy | 0% | ⏳ Aguardando |

**Frontend Total:** 40% → 100% (meta)

---

## 🎯 Próxima Ação

**SEMANA 6 - DIA 1:** Começar Gestão de Estoque

### Setup Inicial

```bash
# Criar estrutura
cd frontend/src/features
mkdir stock
cd stock
mkdir api components hooks
New-Item -Path . -Name "types.ts" -ItemType "file"
```

### Arquivos a Criar

1. `types.ts` - Interfaces de depósito, saldo, movimentação, lote
2. `api/stock.ts` - API client
3. `hooks/useStock.ts` - Hooks React Query
4. `components/DepositoList.tsx` - Lista de depósitos
5. `components/MovimentacaoForm.tsx` - Formulário de movimentação

---

## ✅ Checklist de Qualidade

A cada feature completada:

- [ ] Código TypeScript sem erros
- [ ] Componentes responsivos
- [ ] Loading states implementados
- [ ] Tratamento de erros
- [ ] Validação de formulários
- [ ] Feedback visual (toasts/alerts)
- [ ] Documentação inline
- [ ] Testado manualmente

---

## 📚 Recursos Úteis

**Documentação:**
- `IMPLEMENTADO_PRODUTOS.md` - Referência do que foi feito
- `START_HERE_FRONTEND.md` - Guia inicial
- `SPRINT_2_FRONTEND_CORE.md` - Código base

**Próximos Guias (a criar):**
- `SEMANA_6_ESTOQUE.md` - Implementação completa de estoque
- `SEMANA_7_PDV.md` - Sistema de vendas
- `SEMANA_8_FINANCEIRO.md` - Contas a pagar/receber

---

**Última atualização:** 25/01/2026  
**Próxima revisão:** Final da Semana 6
