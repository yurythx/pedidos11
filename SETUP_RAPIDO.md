# ProjetoRavenna - Setup Rápido

## ✅ Checklist de Setup

Execute os comandos na ordem abaixo:

### 1. Ambiente Virtual (obrigatório)
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 3. Configurar .env
```powershell
# Copie o arquivo de exemplo
copy .env.example .env

# Edite .env e configure:
# - DB_NAME, DB_USER, DB_PASSWORD
# - SECRET_KEY (use: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

### 4. PostgreSQL
```sql
-- Criar database
CREATE DATABASE projetoravenna;
```

### 5. Migrations
```powershell
# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate
```

### 6. Popular Dados Iniciais
```powershell
python scripts/populate_initial_data.py
```

### 7. Rodar Servidor
```powershell
python manage.py runserver
```

### 8. Acessar
- **Django Admin**: http://localhost:8000/admin/ (admin/admin123)
- **API Swagger**: http://localhost:8000/api/docs/
- **API ReDoc**: http://localhost:8000/api/redoc/

---

## 🔐 Login JWT (via Swagger ou Postman)

```bash
POST /api/auth/token/
{
  "username": "admin",
  "password": "admin123"
}

# Response:
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {...}
}

# Usar token:
Authorization: Bearer eyJ...
```

---

## 🧪 Testar Endpoints

Via Swagger (http://localhost:8000/api/docs/):

1. Login → Obter token
2. Authorize → Colar token
3. Testar endpoints:
   - GET /api/produtos/
   - POST /api/mesas/{id}/abrir/
   - GET /api/dashboard/resumo-dia/

---

## ⚠️ Troubleshooting

**Erro: No module named 'rest_framework_simplejwt'**
```powershell
pip install djangorestframework-simplejwt
```

**Erro: relation does not exist**
```powershell
python manage.py migrate
```

**Erro: FATAL: database "projetoravenna" does not exist**
```sql
CREATE DATABASE projetoravenna;
```

---

**Pronto! Backend rodando em ~10 minutos!** 🚀
