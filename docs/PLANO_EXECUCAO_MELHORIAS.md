# 🚀 Plano de Execução - Melhorias Projeto Nix

**Status:** 📋 Planejamento  
**Início Previsto:** Imediato  
**Duração Estimada:** 12 semanas (3 sprints)

---

## 📊 Overview do Plano

Este documento detalha **passo a passo** as ações necessárias para elevar o Projeto Nix a um nível de produção enterprise-grade. Cada tarefa inclui comandos específicos, arquivos a modificar e critérios de aceitação.

---

## 🔴 SPRINT 1 - Fundação Sólida (Semanas 1-4)

**Objetivo:** Garantir segurança, qualidade e automação básica

### Semana 1: Segurança Crítica

#### Task 1.1: Corrigir SECRET_KEY

**Arquivo:** `backend/config/settings.py`

**Ação:**
```python
# ANTES (linha 12):
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-IN-PRODUCTION')

# DEPOIS:
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set!")
```

**Gerar SECRET_KEY segura:**
```bash
cd backend
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Adicionar ao .env:**
```bash
SECRET_KEY=<resultado_do_comando_acima>
```

**Critério de Aceitação:** ✅ Servidor não inicia sem SECRET_KEY válida

---

#### Task 1.2: Proteger .env de versionamento

**Arquivo:** `.gitignore`

**Ação:**
```bash
# Verificar se .env está no .gitignore
cat .gitignore | grep .env

# Se não estiver, adicionar:
echo "" >> .gitignore
echo "# Environment variables" >> .gitignore
echo ".env" >> .gitignore
echo "backend/.env" >> .gitignore
echo "frontend/.env.local" >> .gitignore
```

**Remover .env do histórico (se já versionado):**
```bash
git rm --cached .env
git rm --cached backend/.env
git commit -m "Remove .env files from version control"
```

**Critério de Aceitação:** ✅ .env não aparece em `git status`

---

#### Task 1.3: Ativar HTTPS em Produção

**Arquivo:** `backend/config/settings.py`

**Ação:**
```python
# Substituir linhas 281-291 por:
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Forçar HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Critério de Aceitação:** ✅ Com DEBUG=False, servidor redireciona HTTP → HTTPS

---

#### Task 1.4: Migrar Tokens para httpOnly Cookies

**Complexidade:** Alta ⚠️  
**Estimativa:** 2-3 dias

**Backend - Criar endpoint de login com cookies:**

**Novo arquivo:** `backend/authentication/views_cookie.py`
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([AllowAny])
def cookie_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=401)
    
    refresh = RefreshToken.for_user(user)
    
    response = Response({
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'empresa_id': str(user.empresa_id),
            'cargo': user.cargo,
        }
    })
    
    # Set httpOnly cookies
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=not settings.DEBUG,  # True em produção
        samesite='Strict',
        max_age=60 * 15,  # 15 minutos
    )
    
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Strict',
        max_age=60 * 60 * 24 * 7,  # 7 dias
    )
    
    return response

@api_view(['POST'])
def cookie_logout(request):
    response = Response({'detail': 'Logged out'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
```

**Frontend - Atualizar axios interceptor:**

**Arquivo:** `frontend/src/lib/http/axios.ts`
```typescript
// Modificar interceptor de request (linha 33):
api.interceptors.request.use((config: any) => {
  // Cookies são enviados automaticamente pelo browser
  // Remover lógica de Authorization header manual
  return config
})

// Adicionar configuração para enviar cookies:
const api = axios.create({
  baseURL: env.apiUrl,
  withCredentials: true,  // ADICIONAR ESTA LINHA
})
```

**Critério de Aceitação:** 
- ✅ Login funciona com cookies
- ✅ Tokens não ficam visíveis no localStorage
- ✅ Refresh automático funciona

---

### Semana 2: Infraestrutura de Testes

#### Task 2.1: Configurar Pytest e Coverage (Backend)

**Instalar dependências:**
```bash
cd backend
pip install pytest pytest-django pytest-cov factory-boy faker
```

**Atualizar requirements.txt:**
```bash
pip freeze | grep -E "(pytest|factory|faker)" >> requirements.txt
```

**Criar:** `backend/pytest.ini`
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
testpaths = .
addopts = 
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=60
    --strict-markers
    -v
```

**Criar:** `backend/conftest.py`
```python
import pytest
from django.contrib.auth import get_user_model
from tenant.models import Empresa

@pytest.fixture
def empresa():
    return Empresa.objects.create(
        nome='Empresa Teste',
        cnpj='12345678901234',
        email='teste@empresa.com'
    )

@pytest.fixture
def user(empresa):
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@test.com',
        empresa=empresa,
        cargo='ADMIN'
    )

@pytest.fixture
def api_client(user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client
```

**Rodar testes:**
```bash
cd backend
pytest
```

**Critério de Aceitação:** ✅ Testes rodam e geram relatório de cobertura

---

#### Task 2.2: Criar Testes para Módulos Críticos

**Criar:** `backend/catalog/tests/test_produtos.py`
```python
import pytest
from catalog.models import Produto, Categoria

@pytest.mark.django_db
class TestProduto:
    def test_create_produto(self, empresa):
        categoria = Categoria.objects.create(
            nome='Bebidas',
            empresa=empresa
        )
        produto = Produto.objects.create(
            nome='Coca-Cola',
            tipo='SIMPLES',
            preco_venda=5.00,
            categoria=categoria,
            empresa=empresa
        )
        assert produto.nome == 'Coca-Cola'
        assert produto.preco_venda == 5.00
    
    def test_produto_requires_empresa(self):
        with pytest.raises(Exception):
            Produto.objects.create(nome='Teste')
    
    def test_calcular_margem(self, empresa):
        produto = Produto.objects.create(
            nome='Teste',
            tipo='SIMPLES',
            preco_custo=10.00,
            preco_venda=15.00,
            empresa=empresa
        )
        margem = produto.calcular_margem()
        assert margem == 50.0  # (15-10)/10 * 100
```

**Criar:** `backend/sales/tests/test_vendas.py`
```python
import pytest
from sales.models import Venda
from catalog.models import Produto
from decimal import Decimal

@pytest.mark.django_db
class TestVenda:
    def test_create_venda(self, empresa, user):
        venda = Venda.objects.create(
            empresa=empresa,
            vendedor=user,
            status='ABERTA'
        )
        assert venda.status == 'ABERTA'
        assert venda.valor_total == Decimal('0.00')
    
    def test_adicionar_item_venda(self, empresa, user):
        produto = Produto.objects.create(
            nome='Produto Teste',
            tipo='SIMPLES',
            preco_venda=10.00,
            empresa=empresa
        )
        venda = Venda.objects.create(
            empresa=empresa,
            vendedor=user
        )
        # Usar service para adicionar item
        from sales.services import VendaService
        item = VendaService.adicionar_item(
            venda=venda,
            produto=produto,
            quantidade=2
        )
        venda.refresh_from_db()
        assert venda.valor_total == Decimal('20.00')
```

**Meta:** 20+ testes criados na Semana 2

**Critério de Aceitação:** ✅ Cobertura alcança 40%+

---

#### Task 2.3: Configurar Vitest (Frontend)

**Atualizar:** `frontend/package.json`
```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "vitest": "^1.4.0",
    "jsdom": "^27.4.0"
  }
}
```

**Instalar:**
```bash
cd frontend
npm install
```

**Criar:** `frontend/vitest.config.ts`
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './vitest.setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', '**/*.config.*'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**Criar:** `frontend/vitest.setup.ts`
```typescript
import '@testing-library/jest-dom'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
```

**Criar testes de exemplo:** `frontend/src/features/auth/__tests__/login.test.tsx`
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
// Componente de login (a ser criado)

describe('Login', () => {
  it('should render login form', () => {
    render(<LoginPage />)
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })
  
  it('should submit form with credentials', async () => {
    const mockLogin = vi.fn()
    render(<LoginPage onLogin={mockLogin} />)
    
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    await userEvent.type(screen.getByLabelText(/password/i), 'password123')
    await userEvent.click(screen.getByRole('button', { name: /login/i }))
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      })
    })
  })
})
```

**Rodar:**
```bash
npm run test
```

**Critério de Aceitação:** ✅ Testes rodam com sucesso

---

### Semana 3: CI/CD Pipeline

#### Task 3.1: GitHub Actions - Backend CI

**Criar:** `.github/workflows/backend-ci.yml`
```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      
      - name: Run linting
        run: |
          pip install black flake8
          black --check backend/
          flake8 backend/ --max-line-length=120
      
      - name: Run tests
        env:
          DATABASE: postgres
          SQL_ENGINE: django.db.backends.postgresql
          SQL_DATABASE: test_db
          SQL_USER: postgres
          SQL_PASSWORD: postgres
          SQL_HOST: localhost
          SQL_PORT: 5432
          SECRET_KEY: test-secret-key-for-ci
          DEBUG: True
        run: |
          cd backend
          pytest --cov --cov-fail-under=60
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend
```

**Critério de Aceitação:** ✅ Pipeline roda em cada push

---

#### Task 3.2: GitHub Actions - Frontend CI

**Criar:** `.github/workflows/frontend-ci.yml`
```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run linting
        run: |
          cd frontend
          npm run lint || echo "Configurar ESLint"
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
      
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_API_URL: http://localhost:8000/api
```

**Critério de Aceitação:** ✅ Build e testes rodam automaticamente

---

### Semana 4: Observabilidade Básica

#### Task 4.1: Integrar Sentry

**Backend:**
```bash
cd backend
pip install sentry-sdk
```

**Atualizar:** `backend/config/settings.py`
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=os.environ.get("ENVIRONMENT", "production"),
    )
```

**Frontend:**
```bash
cd frontend
npm install @sentry/nextjs
```

**Criar:** `frontend/sentry.client.config.ts`
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
})
```

**Critério de Aceitação:** ✅ Erros são reportados no Sentry

---

#### Task 4.2: Logging Estruturado

**Atualizar:** `backend/config/settings.py`
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

**Instalar:**
```bash
pip install python-json-logger
```

**Critério de Aceitação:** ✅ Logs em formato JSON

---

## 🟡 SPRINT 2 - Frontend Core (Semanas 5-8)

### Semana 5-6: Catálogo e Estoque

#### Task 5.1: CRUD de Produtos

**Criar:** `frontend/src/features/catalog/components/ProductForm.tsx`
**Criar:** `frontend/src/features/catalog/api/products.ts`
**Criar:** `frontend/app/produtos/novo/page.tsx`

**Features:**
- Lista de produtos com paginação
- Formulário de criação/edição
- Filtros (categoria, tipo, preço)
- Upload de imagem

**Critério de Aceitação:** 
- ✅ CRUD completo funcional
- ✅ Validações com Zod
- ✅ Loading states

---

#### Task 5.2: Gestão de Estoque

**Criar movimentações:**
- Entrada de mercadoria
- Saída manual
- Transferência entre depósitos

**Critério de Aceitação:** ✅ Movimentações refletem em saldo

---

### Semana 7-8: Vendas e Financeiro

#### Task 6.1: PDV Básico

**Componentes principais:**
- Seleção de produtos
- Carrinho de compras
- Finalização de venda
- Impressão de cupom (opcional)

**Critério de Aceitação:** ✅ Venda completa E2E funciona

---

#### Task 6.2: Contas a Receber/Pagar

**Features:**
- Listagem com filtros
- Lançamento manual
- Baixa de contas
- Dashboard de fluxo de caixa

**Critério de Aceitação:** ✅ Integração com vendas

---

## 🟢 SPRINT 3 - Avançado (Semanas 9-12)

### Semana 9-10: Restaurant e KDS

#### Task 7.1: Gestão de Mesas

**Features:**
- Mapa visual de mesas
- Abrir/Fechar mesa
- Adicionar pedidos
- Dividir conta

---

#### Task 7.2: Kitchen Display System

**Features:**
- Painel de produção em tempo real
- Filtro por setor (cozinha, bar)
- Marcar item como pronto

**Considerar:** WebSocket para updates em tempo real

---

### Semana 11: NFe Upload

#### Task 8.1: Interface de Upload

**Features:**
- Drag & drop de XML
- Preview de dados
- Matching de produtos
- Confirmação de importação

---

### Semana 12: Performance e Deploy

#### Task 9.1: Otimizações

**Backend:**
- Configurar Redis cache
- Otimizar queries N+1
- Adicionar índices

**Frontend:**
- Code splitting
- Lazy loading
- Image optimization

---

#### Task 9.2: Deploy Pipeline

**Criar:** `.github/workflows/deploy.yml`
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and push Docker images
        run: |
          docker build -t projetonix/backend:${{ github.sha }} ./backend
          docker build -t projetonix/frontend:${{ github.sha }} ./frontend
          docker push projetonix/backend:${{ github.sha }}
          docker push projetonix/frontend:${{ github.sha }}
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/projetonix
            docker-compose pull
            docker-compose up -d
```

**Critério de Aceitação:** ✅ Deploy automatizado funciona

---

## 📈 KPIs de Acompanhamento

### Semanalmente
- [ ] Novos testes criados: XX
- [ ] Cobertura de código: XX%
- [ ] Bugs abertos vs fechados
- [ ] Velocidade do sprint (story points)

### Mensalmente
- [ ] Features completadas vs planejadas
- [ ] Tempo médio de PR review
- [ ] Uptime (após deploy)
- [ ] Performance (tempo de resposta)

---

## ✅ Definition of Done

Cada task só está completa quando:

1. ✅ Código implementado
2. ✅ Testes escritos e passando
3. ✅ Documentação atualizada
4. ✅ Code review aprovado
5. ✅ CI/CD verde
6. ✅ Deploy em staging testado

---

## 🎯 Quick Wins (Primeiras 2 Semanas)

Ações que geram impacto imediato:

1. ✅ Corrigir SECRET_KEY (30 min)
2. ✅ Adicionar .env ao .gitignore (5 min)
3. ✅ Configurar pytest (1h)
4. ✅ Criar 10 testes básicos (2h)
5. ✅ Setup GitHub Actions (2h)
6. ✅ Integrar Sentry (1h)

**Total de esforço:** ~1 dia  
**Impacto:** Segurança + Qualidade + Automação

---

## 📞 Suporte

Para dúvidas sobre este plano:
- Documentação: Veja `ANALISE_DETALHADA_PROJETO.md`
- Issues: Abra issue no GitHub com tag `improvement-plan`

---

**Última atualização:** 25/01/2026  
**Versão:** 1.0  
**Próxima revisão:** Após Sprint 1
