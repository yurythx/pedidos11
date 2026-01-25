# 🐳 DOCKER - INÍCIO ULTRA-RÁPIDO

**Rode tudo com 1 comando em 2 minutos!**

---

## ⚡ MÉTODO MAIS FÁCIL (Docker)

### Pré-requisito
- ✅ Docker Desktop instalado
- ✅ Docker Compose (incluído no Desktop)

---

## 🚀 RODAR TUDO (1 Comando!)

```bash
# Na raiz do projeto
cd "c:\Users\allle\OneDrive\Área de Trabalho\Projetos\pedidos11"

# Rodar tudo de uma vez
docker-compose up -d
```

**Isso vai:**
1. ✅ Criar banco PostgreSQL
2. ✅ Rodar migrations automaticamente
3. ✅ Criar superusuário padrão (admin/admin123)
4. ✅ Iniciar backend em http://localhost:8000
5. ✅ Iniciar frontend em http://localhost:3000

**Tempo:** ~2 minutos (primeira vez)

---

## ✅ ACESSAR

Após `docker-compose up`:

- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:8000/api/v1
- 👤 **Django Admin:** http://localhost:8000/admin
  - **User:** admin
  - **Password:** admin123

---

## 📊 COMANDOS ÚTEIS

### Ver logs em tempo real
```bash
docker-compose logs -f
```

### Ver logs específicos
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Parar tudo
```bash
docker-compose down
```

### Parar e deletar volumes
```bash
docker-compose down -v
```

### Reconstruir containers
```bash
docker-compose up -d --build
```

### Ver status
```bash
docker-compose ps
```

---

## 🔧 COMANDOS DJANGO

### Criar migrations
```bash
docker-compose exec backend python manage.py makemigrations
```

### Executar migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Criar superusuário adicional
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Shell do Django
```bash
docker-compose exec backend python manage.py shell
```

### Acessar banco
```bash
docker-compose exec db psql -U nix_user -d nix_db
```

---

## 🔧 COMANDOS FRONTEND

### Instalar nova dependência
```bash
docker-compose exec frontend npm install <package>
```

### Rebuild do Next.js
```bash
docker-compose exec frontend npm run build
```

### Shell do container
```bash
docker-compose exec frontend sh
```

---

## 🎨 CRIAR DADOS DE TESTE

```bash
# Acessar shell do Django
docker-compose exec backend python manage.py shell
```

```python
# Criar categorias
from apps.catalog.models import Categoria

categorias = [
    {'nome': 'Bebidas', 'ativo': True},
    {'nome': 'Alimentos', 'ativo': True},
    {'nome': 'Limpeza', 'ativo': True},
]

for cat in categorias:
    Categoria.objects.get_or_create(**cat)

# Criar depósito
from apps.inventory.models import Deposito

Deposito.objects.get_or_create(
    nome='Depósito Principal',
    codigo='DEP001',
    defaults={'is_padrao': True, 'ativo': True}
)

print("✅ Dados criados!")
```

---

## 🐛 TROUBLESHOOTING

### Port já em uso
```bash
# Parar containers
docker-compose down

# Mudar porta no docker-compose.yml
# Trocar "3000:3000" por "3001:3000"
```

### Container não inicia
```bash
# Ver logs
docker-compose logs backend

# Reconstruir
docker-compose up -d --build
```

### Banco não conecta
```bash
# Verificar health check
docker-compose ps

# Restart do banco
docker-compose restart db
```

### Frontend não atualiza
```bash
# Limpar cache
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

---

## 🔄 WORKFLOW DE DESENVOLVIMENTO

### Desenvolvimento Normal
```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Trabalhar normalmente
# Hot reload está ativo em ambos serviços

# Parar ao finalizar
docker-compose down
```

### Adicionar nova migração
```bash
# 1. Alterar models no código
# 2. Criar migration
docker-compose exec backend python manage.py makemigrations

# 3. Aplicar
docker-compose exec backend python manage.py migrate
```

### Adicionar pacote NPM
```bash
# 1. Instalar
docker-compose exec frontend npm install <package>

# 2. Rebuild (se necessário)
docker-compose restart frontend
```

---

## 📦 VOLUMES

O Docker Compose cria 3 volumes:

1. **postgres_data** - Dados do banco
2. **static_volume** - Arquivos estáticos do Django
3. **media_volume** - Uploads de mídia

### Backup do banco
```bash
docker-compose exec db pg_dump -U nix_user nix_db > backup.sql
```

### Restore do banco
```bash
cat backup.sql | docker-compose exec -T db psql -U nix_user -d nix_db
```

---

## ⚙️ VARIÁVEIS DE AMBIENTE

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://nix_user:nix_password@db:5432/nix_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🚀 PRODUÇÃO

### Build otimizado
```bash
# Criar docker-compose.prod.yml
# Usar gunicorn para backend
# Usar nginx para servir frontend
# Usar PostgreSQL externo
```

### Deploy básico
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 COMPARAÇÃO

### Docker vs Manual

| Aspecto | Docker | Manual |
|---------|--------|--------|
| **Setup** | 1 comando | ~15 minutos |
| **Dependências** | Automático | Manual |
| **Banco** | PostgreSQL | SQLite |
| **Isolamento** | Total | Ambiente local |
| **Portabilidade** | Máxima | Limitada |
| **Primeiro uso** | 2-3 min | 10-15 min |

---

## ✅ CHECKLIST DOCKER

- [ ] Docker Desktop instalado
- [ ] `docker-compose up -d` executado
- [ ] Frontend em http://localhost:3000
- [ ] Backend em http://localhost:8000
- [ ] Admin acessível (admin/admin123)
- [ ] Criar dados de teste
- [ ] Testar PDV
- [ ] Fazer uma venda

---

## 🎯 VANTAGENS DO DOCKER

1. ✅ **Setup em 1 comando**
2. ✅ **Ambiente consistente**
3. ✅ **PostgreSQL incluído**
4. ✅ **Fácil compartilhar com equipe**
5. ✅ **Isolamento total**
6. ✅ **Fácil resetar** (docker-compose down -v)
7. ✅ **Preparado para produção**

---

## 🎊 RESUMO

**Para começar:**
```bash
docker-compose up -d
```

**Para parar:**
```bash
docker-compose down
```

**Para resetar tudo:**
```bash
docker-compose down -v
docker-compose up -d
```

---

## 💡 DICA

Se preferir ver os logs enquanto roda:
```bash
docker-compose up
```

Para rodar em background:
```bash
docker-compose up -d
```

---

**Com Docker, você tem o ambiente completo em 2 minutos!** 🐳

**Última atualização:** 25/01/2026
