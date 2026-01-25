# 🚀 GUIA DE INSTALAÇÃO E SETUP - Projeto Nix

**Versão:** 1.0.0  
**Data:** 25/01/2026  
**Tempo estimado:** 15-20 minutos

---

## 📋 PRÉ-REQUISITOS

### Sistema Operacional
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+)

### Software Necessário

#### Backend
- Python 3.11+
- pip 23+
- virtualenv

#### Frontend
- Node.js 18+
- npm 9+

#### Banco de Dados
- PostgreSQL 14+ (produção)
- SQLite (desenvolvimento - já configurado)

---

## ⚙️ INSTALAÇÃO PASSO A PASSO

### 1️⃣ Clonar Repositório (se necessário)

```bash
# Se ainda não tem o projeto
git clone <repository-url>
cd pedidos11
```

---

### 2️⃣ Setup do Backend (Django)

```bash
# Navegar para pasta do backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows PowerShell:
.\venv\Scripts\Activate

# macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
# Windows:
Copy-Item .env.example .env

# macOS/Linux:
cp .env.example .env

# Editar .env e adicionar:
# SECRET_KEY=<gerar com: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
# DEBUG=True
# DATABASE_URL=sqlite:///db.sqlite3

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

**Backend rodando em:** http://localhost:8000

---

### 3️⃣ Setup do Frontend (Next.js)

**Abrir novo terminal:**

```bash
# Navegar para pasta do frontend
cd frontend

# Instalar dependências
npm install

# Instalar dependências adicionais implementadas
npm install @tanstack/react-query zustand react-hook-form @hookform/resolvers/zod

# Criar arquivo .env.local
# Windows:
Copy-Item .env.example .env.local

# macOS/Linux:
cp .env.example .env.local

# Editar .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Rodar em desenvolvimento
npm run dev
```

**Frontend rodando em:** http://localhost:3000

---

## ✅ VERIFICAÇÃO

### Backend
1. Acesse http://localhost:8000/admin
2. Faça login com superusuário
3. Verifique se tem acesso ao Django Admin

### Frontend
1. Acesse http://localhost:3000
2. Navegue para `/produtos`
3. Tente criar um produto

---

## 🗂️ ESTRUTURA DE PASTAS

```
pedidos11/
├── backend/                 # Backend Django
│   ├── apps/               # Aplicações Django
│   │   ├── accounts/       # Autenticação
│   │   ├── catalog/        # Produtos
│   │   ├── inventory/      # Estoque
│   │   ├── sales/          # Vendas
│   │   └── finance/        # Financeiro
│   ├── config/             # Configurações
│   ├── venv/               # Ambiente virtual
│   └── manage.py
│
├── frontend/               # Frontend Next.js
│   ├── app/               # Pages (App Router)
│   │   ├── produtos/
│   │   ├── depositos/
│   │   ├── movimentacoes/
│   │   ├── pdv/
│   │   ├── vendas/
│   │   └── financeiro/
│   ├── src/
│   │   ├── features/      # Features organizadas
│   │   │   ├── catalog/
│   │   │   ├── stock/
│   │   │   ├── sales/
│   │   │   └── finance/
│   │   ├── lib/           # Utilitários
│   │   └── utils/         # Helpers
│   └── package.json
│
└── docs/                  # Documentação
    ├── PROJETO_COMPLETO_FINAL.md
    ├── GUIA_INSTALACAO.md (este arquivo)
    └── ...
```

---

## 🌐 PÁGINAS DISPONÍVEIS

Após instalação, acesse:

### Produtos
- http://localhost:3000/produtos
- http://localhost:3000/produtos/novo

### Estoque
- http://localhost:3000/depositos
- http://localhost:3000/saldos
- http://localhost:3000/movimentacoes
- http://localhost:3000/lotes

### Vendas
- http://localhost:3000/pdv
- http://localhost:3000/vendas

### Financeiro
- http://localhost:3000/financeiro
- http://localhost:3000/financeiro/receber

---

## 🐛 TROUBLESHOOTING

### Erro: "Module not found"

**Solução:**
```bash
cd frontend
npm install
```

### Erro: "Cannot connect to database"

**Solução:**
```bash
cd backend
python manage.py migrate
```

### Erro: "Port 8000 already in use"

**Solução:**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Erro: "React Query not configured"

**Solução:** Verificar se `QueryClientProvider` está configurado no `app/layout.tsx`

### Erro: API retorna 401

**Solução:** Verificar se o token de autenticação está sendo enviado corretamente nos headers

---

## 📦 DADOS INICIAIS (Seed)

### Criar Categorias de Teste

```bash
cd backend
python manage.py shell
```

```python
from apps.catalog.models import Categoria

categorias = [
    {'nome': 'Bebidas', 'ativo': True},
    {'nome': 'Alimentos', 'ativo': True},
    {'nome': 'Higiene', 'ativo': True},
]

for cat in categorias:
    Categoria.objects.create(**cat)
```

### Criar Depósito Padrão

```python
from apps.inventory.models import Deposito

Deposito.objects.create(
    nome='Depósito Principal',
    codigo='DEP001',
    is_padrao=True,
    ativo=True
)
```

---

## 🔐 SEGURANÇA

### Antes de Deploy em Produção

1. ✅ Gerar nova SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. ✅ Configurar variáveis de ambiente
```bash
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com
```

3. ✅ Usar PostgreSQL
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
```

4. ✅ Configurar HTTPS
5. ✅ Configurar CORS
6. ✅ Ativar tokens httpOnly

---

## 📚 PRÓXIMOS PASSOS

Após instalação bem-sucedida:

1. ✅ Ler `PROJETO_COMPLETO_FINAL.md`
2. ✅ Testar todos os fluxos
3. ✅ Personalizar conforme necessidade
4. ✅ Implementar features adicionais
5. ✅ Deploy

---

## 📞 SUPORTE

**Documentação:**
- `INDEX.md` - Índice completo
- `START_HERE_FRONTEND.md` - Guia frontend
- `ROADMAP_IMPLEMENTACAO.md` - Próximas features

**Problemas:**
1. Verificar logs do console
2. Verificar logs do backend
3. Consultar documentação
4. Revisar código de exemplo

---

## ✅ CHECKLIST DE INSTALAÇÃO

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] Backend rodando (http://localhost:8000)
- [ ] Frontend rodando (http://localhost:3000)
- [ ] Banco de dados migrado
- [ ] Superusuário criado
- [ ] Categorias de teste criadas
- [ ] Depósito padrão criado
- [ ] Página /produtos acessível
- [ ] PDV funciona
- [ ] Pode criar produto
- [ ] Pode criar venda

---

**Instalação completa! Pronto para usar!** 🎉

---

**Versão:** 1.0.0  
**Última atualização:** 25/01/2026
