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

## 🚀 Deploy Automatizado

**Deploy em 1 comando!**

### Linux/Ubuntu (Servidor)
```bash
./deploy.sh
```

### Windows (Local)
```powershell
.\deploy.ps1
```

**Inclui:**
- ✅ 11 verificações automáticas
- ✅ Backup automático
- ✅ Health checks completos
- ✅ Rollback automático se falhar
- ✅ Logs detalhados

📖 **Documentação:** [DEPLOY_AUTOMATIZADO.md](docs/DEPLOY_AUTOMATIZADO.md)

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

> **Toda documentação foi movida para a pasta [`docs/`](docs/)**

### 🚀 Para Começar
- 📄 **[INICIO_RAPIDO.md](docs/INICIO_RAPIDO.md)** ← **COMECE AQUI!**
- 📄 **[GUIA_INSTALACAO.md](docs/GUIA_INSTALACAO.md)** - Setup completo
- 📄 **[DOCKER_GUIA.md](docs/DOCKER_GUIA.md)** - Com Docker (2 min)
- 📄 **[CHECKLIST_VALIDACAO.md](docs/CHECKLIST_VALIDACAO.md)** - 200+ itens de teste

### 🚀 Deploy
- 📄 **[DEPLOY_AUTOMATIZADO.md](docs/DEPLOY_AUTOMATIZADO.md)** ← **1 comando!**
- 📄 **[DEPLOY_UBUNTU.md](docs/DEPLOY_UBUNTU.md)** - Deploy em servidor Ubuntu
- 📄 **[DEPLOY_GITHUB.md](docs/DEPLOY_GITHUB.md)** - CI/CD via GitHub
- 📄 **[GITHUB_COMPLETO.md](docs/GITHUB_COMPLETO.md)** - Setup GitHub completo

### 📊 Visão Geral
- 📄 **[PROJETO_COMPLETO_FINAL.md](docs/PROJETO_COMPLETO_FINAL.md)** - Resumo executivo
- 📄 **[INDEX.md](docs/INDEX.md)** - Navegação completa de toda documentação
-  **[CONCLUSAO.md](docs/CONCLUSAO.md)** - Próximos passos
- 📄 **[PLANO_ACAO_EXECUTAVEL.md](docs/PLANO_ACAO_EXECUTAVEL.md)** - Roadmap executável

### 🔧 Técnica
- � **[ANALISE_DETALHADA_PROJETO.md](docs/ANALISE_DETALHADA_PROJETO.md)** - Análise backend
- � **[ROADMAP_IMPLEMENTACAO.md](docs/ROADMAP_IMPLEMENTACAO.md)** - Roadmap 12 semanas
- 📄 **[START_HERE_FRONTEND.md](docs/START_HERE_FRONTEND.md)** - Guia frontend

### 📈 Estratégica
- � **[RESUMO_EXECUTIVO.md](docs/RESUMO_EXECUTIVO.md)** - Para stakeholders
- 📄 **[COMPARATIVO_ESTADO.md](docs/COMPARATIVO_ESTADO.md)** - ROI e métricas
- 📄 **[PLANO_EXECUCAO_MELHORIAS.md](docs/PLANO_EXECUCAO_MELHORIAS.md)** - Plano ação

**📁 Veja todos os documentos em [`docs/README.md`](docs/README.md)**
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
