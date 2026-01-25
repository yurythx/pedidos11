# Projeto Nix - ERP/PDV Multi-Tenant

Sistema ERP/PDV completo com foco em **Food Service** (Restaurantes, Bares, Lanchonetes).

## 🚀 Quick Start

```powershell
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env

# 2. Database (PostgreSQL)
# Criar database: projetonix

# 3. Migrations
python manage.py migrate

# 4. Dados Iniciais
python scripts/populate_initial_data.py

# 5. Rodar
python manage.py runserver
```

**Acesse:** http://localhost:8000/admin/ (admin/admin123)

📖 **Mais detalhes:** [SETUP_RAPIDO.md](SETUP_RAPIDO.md)

---

## 📦 Features Implementadas

### ✅ Core
- Multi-tenancy robusto
- Autenticação JWT com payload customizado
- API REST completa (50+ endpoints)
- SOLID principles (Score: 10/10)

### ✅ Módulos
- **Catalog**: Produtos, Categorias, Complementos
- **Stock**: Controle de estoque com movimentações

## 🌐 API Endpoints

**Autenticação:**
- `POST /api/auth/token/` - Login (JWT)
- `POST /api/auth/token/refresh/` - Renovar token

**Principais:**
- `/api/produtos/` - Catálogo
- `/api/vendas/` - Vendas
- `/api/mesas/` - Mesas (Food Service)
- `/api/producao/` - KDS
- `/api/dashboard/resumo-dia/` - Analytics

**Documentação:** http://localhost:8000/api/docs/

---

## 📚 Documentação

### 📋 Análise e Planejamento (NOVO!) 🎯
> **Análise completa do projeto com plano de melhorias para 12 semanas**

- **🚀 [COMECE AQUI: Índice Geral](INDEX.md)** - Guia de navegação
- 📊 [Resumo Executivo](RESUMO_EXECUTIVO.md) - Visão geral e plano (10 min)
- 📑 [Análise Detalhada](ANALISE_DETALHADA_PROJETO.md) - Deep dive técnico (45 min)
- 📋 [Plano de Execução](PLANO_EXECUCAO_MELHORIAS.md) - Passo a passo (60 min)
- 📈 [Comparativo Estado](COMPARATIVO_ESTADO.md) - Atual vs Desejado (30 min)

### Setup e Integração
- [Setup Rápido](SETUP_RAPIDO.md)
- [Documentação Completa](doc/README.md)
- [Guia de Integração Front/Mobile](doc/INTEGRATION_GUIDE_FRONT_MOBILE.md)
- [Checklists de Integração por Módulo](doc/INTEGRATION_CHECKLISTS.md)
- [Coleção Postman](doc/POSTMAN_COLLECTION.json)
- [Clientes OpenAPI (guia)](doc/OPENAPI_CLIENTS.md)
- [Exemplos HTTP (VS Code REST Client)](doc/http_examples.http)

---

## 🛠️ Stack

- **Backend**: Django 5.x + DRF
- **Database**: PostgreSQL
- **Auth**: JWT (simplejwt)
- **API Doc**: drf-spectacular (Swagger/ReDoc)

---

## 📊 Status

**Backend:** ✅ 100% Completo  
**Testes:** ⏳ Em expansão (NFe coberta)  
**Frontend:** 🚧 Projeto Next.js separado em back/frontend  
**Deploy:** ⏳ Não iniciado

---

## 👨‍💻 Desenvolvido por

Projeto Nix - ERP/PDV Multi-Tenant  
**Arquitetura:** DDD + SOLID + Multi-tenancy

---

**Seja bem-vindo ao Projeto Nix!** 🎉
