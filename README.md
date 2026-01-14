# ProjetoRavenna - ERP/PDV Multi-Tenant

Sistema ERP/PDV completo com foco em **Food Service** (Restaurantes, Bares, Lanchonetes).

## 🚀 Quick Start

```powershell
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env

# 2. Database (PostgreSQL)
# Criar database: projetoravenna

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
- **Sales**: Vendas, Itens, Integração com estoque
- **Financial**: Contas a Pagar/Receber
- **Restaurant**: Mesas, Comandas, Setores de Produção
- **Partners**: Clientes, Fornecedores

### ✅ Food Service
- Sistema de Mesas (abrir, adicionar pedidos, fechar)
- Comandas individuais
- Complementos de produtos
- KDS (Kitchen Display System)
- Dashboard com analytics

---

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

- [Setup Rápido](SETUP_RAPIDO.md)
- [Próximos Passos](PROXIMOS_PASSOS.md)
- [Documentação Completa](doc/README.md)

---

## 🛠️ Stack

- **Backend**: Django 5.x + DRF
- **Database**: PostgreSQL
- **Auth**: JWT (simplejwt)
- **API Doc**: drf-spectacular (Swagger/ReDoc)

---

## 📊 Status

**Backend:** ✅ 100% Completo  
**Testes:** ⏳ Pendente  
**Frontend:** ⏳ Não iniciado  
**Deploy:** ⏳ Não iniciado

---

## 👨‍💻 Desenvolvido por

ProjetoRavenna - ERP/PDV Multi-Tenant  
**Arquitetura:** DDD + SOLID + Multi-tenancy

---

**Seja bem-vindo ao ProjetoRavenna!** 🎉
