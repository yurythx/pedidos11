# Projeto Nix - Guia de Setup e Inicialização

## 🎯 Apps Implementados

✅ **tenant** - Empresas (multi-tenancy)  
✅ **authentication** - Usuários customizados  
✅ **partners** - Clientes e Fornecedores  
✅ **core** - Infraestrutura base  
✅ **locations** - Endereços  
✅ **catalog** - Produtos e Categorias  
✅ **stock** - Estoque e Movimentações  
✅ **sales** - Vendas

---

## 🚀 Setup Inicial

### 1. Criar ambiente virtual

```powershell
# Criar venv
python -m venv venv

# Ativar venv
.\venv\Scripts\Activate

# Verificar
python --version
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar banco de dados PostgreSQL

```powershell
# Criar banco de dados
# Opção A: via psql
psql -U postgres
CREATE DATABASE projetonix;
\q

# Opção B: via pgAdmin (interface gráfica)
# Criar novo database chamado "projetonix"
```

### 4. Configurar variáveis de ambiente

```powershell
# Copiar .env.example para .env
copy .env.example .env

# Editar .env com suas configurações
notepad .env
```

### 5. Criar migrations

```powershell
# Ordem de criação (importante por causa das dependências):
python manage.py makemigrations tenant
python manage.py makemigrations authentication
python manage.py makemigrations core
python manage.py makemigrations locations
python manage.py makemigrations catalog
python manage.py makemigrations stock
python manage.py makemigrations partners
python manage.py makemigrations sales

# Aplicar migrations
python manage.py migrate
```

### 6. Criar superusuário

```powershell
python manage.py createsuperuser
# Username: admin
# Email: admin@projetonix.com
# Password: ******
# Empresa: (será pedido - criar manualmente antes ou via dados iniciais)
```

---

## 📊 Dados Iniciais (Fixtures)

### Criar empresa inicial via Django Shell

```powershell
python manage.py shell
```

```python
from tenant.models import Empresa

# Criar empresa padrão
empresa = Empresa.objects.create(
    nome_fantasia='Empresa Demo',
    razao_social='Empresa Demo LTDA',
    cnpj='11222333000181',  # CNPJ fictício válido
    email='contato@empresademo.com',
    telefone='(11) 98765-4321'
)

print(f"Empresa criada: {empresa}")
```

### Criar usuário admin via Shell

```python
from authentication.models import CustomUser, TipoCargo
from tenant.models import Empresa

# Buscar empresa
empresa = Empresa.objects.first()

# Criar admin
admin = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@projetonix.com',
    password='admin123',  # MUDAR EM PRODUÇÃO!
    empresa=empresa,
    cargo=TipoCargo.ADMIN,
    first_name='Administrador',
    last_name='Sistema'
)

print(f"Admin criado: {admin}")
```

### Criar depósito padrão

```python
from stock.models import Deposito

deposito = Deposito.objects.create(
    empresa=empresa,
    nome='Loja Principal',
    codigo='LP01',
    is_padrao=True
)

print(f"Depósito criado: {deposito}")
```

### Criar categorias exemplo

```python
from catalog.models import Categoria

categorias = [
    Categoria.objects.create(empresa=empresa, nome='Eletrônicos'),
    Categoria.objects.create(empresa=empresa, nome='Alimentos'),
    Categoria.objects.create(empresa=empresa, nome='Bebidas'),
    Categoria.objects.create(empresa=empresa, nome='Limpeza'),
]

print(f"{len(categorias)} categorias criadas")
```

### Criar produtos exemplo

```python
from catalog.models import Produto, Categoria
from decimal import Decimal

eletronicos = Categoria.objects.get(nome='Eletrônicos')

produtos = [
    Produto.objects.create(
        empresa=empresa,
        nome='Mouse Gamer',
        categoria=eletronicos,
        preco_venda=Decimal('89.90'),
        preco_custo=Decimal('45.00'),
        sku='MOUSE-001'
    ),
    Produto.objects.create(
        empresa=empresa,
        nome='Teclado Mecânico',
        categoria=eletronicos,
        preco_venda=Decimal('299.90'),
        preco_custo=Decimal('150.00'),
        sku='TEC-001'
    ),
]

print(f"{len(produtos)} produtos criados")
```

### Adicionar estoque inicial

```python
from stock.models import Movimentacao, TipoMovimentacao
from catalog.models import Produto
from stock.models import Deposito

deposito = Deposito.objects.get(is_padrao=True)

for produto in Produto.objects.all():
    Movimentacao.objects.create(
        empresa=empresa,
        produto=produto,
        deposito=deposito,
        tipo=TipoMovimentacao.ENTRADA,
        quantidade=Decimal('100.000'),
        valor_unitario=produto.preco_custo,
        documento='EST-INICIAL',
        observacao='Estoque inicial do sistema'
    )

print("Estoque inicial criado")
```

---

## 🏃 Rodar o Projeto

### Development Server

```powershell
python manage.py runserver
```

Acessar:
- **Django Admin**: http://localhost:8000/admin/
- **API Swagger**: http://localhost:8000/api/docs/
- **API ReDoc**: http://localhost:8000/api/redoc/

---

## 🧪 Testar no Django Admin

1. Acessar http://localhost:8000/admin/
2. Login com credenciais do superuser
3. Testar cada módulo:
   - ✅ Empresas (Tenant)
   - ✅ Usuários (Authentication)
   - ✅ Clientes/Fornecedores (Partners)
   - ✅ Categorias e Produtos (Catalog)
   - ✅ Depósitos e Movimentações (Stock)
   - ✅ Vendas (Sales)

---

## 📁 Estrutura de Diretórios

```
pedidos11/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tenant/
│   ├── models.py (Empresa)
│   └── ...
├── authentication/
│   ├── models.py (CustomUser)
│   └── ...
├── partners/
│   ├── models.py (Cliente, Fornecedor)
│   └── ...
├── core/
│   ├── models.py (TenantModel)
│   ├── managers.py (TenantManager)
│   └── ...
├── locations/
│   ├── models.py (Endereco)
│   └── ...
├── catalog/
│   ├── models.py (Categoria, Produto)
│   └── ...
├── stock/
│   ├── models.py (Deposito, Saldo, Movimentacao)
│   └── ...
├── sales/
│   ├── models.py (Venda, ItemVenda)
│   ├── services.py (VendaService)
│   ├── signals.py
│   └── ...
├── doc/
│   ├── implementation_plan.md
│   ├── walkthrough.md
│   ├── sales_documentation.md
│   └── roadmap.md
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🔧 Comandos Úteis

### Migrations

```powershell
# Ver SQL das migrations
python manage.py sqlmigrate tenant 0001

# Reverter migration
python manage.py migrate tenant 0001

# Reset de app
python manage.py migrate tenant zero
```

### Shell

```powershell
# Django shell padrão
python manage.py shell

# IPython (se instalado)
python manage.py shell -i ipython
```

### Criar dados de teste

```powershell
python manage.py shell < scripts/create_initial_data.py
```

### Limpar database

```powershell
python manage.py flush
```

---

## ✅ Checklist de Configuração

- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] PostgreSQL instalado e rodando
- [ ] Database `projetonix` criado
- [ ] Arquivo `.env` configurado
- [ ] Migrations criadas e aplicadas
- [ ] Empresa padrão criada
- [ ] Superusuário criado
- [ ] Depósito padrão criado
- [ ] Categorias exemplo criadas
- [ ] Produtos exemplo criados
- [ ] Estoque inicial adicionado
- [ ] Django Admin acessível
- [ ] Documentação API (Swagger) acessível

---

## 🎉 Próximos Passos

Agora que o backend está rodando, você pode:

1. **Testar no Django Admin** - Criar vendas manualmente
2. **Implementar API REST** - Endpoints para o frontend
3. **Criar testes** - Unitários e de integração
4. **Frontend** - Conectar aplicação React/Vue
5. **Deploy** - Preparar para produção

Consulte o [roadmap.md](file:///C:/Users/yuri.menezes/Desktop/Projetos/pedidos11/doc/roadmap.md) para ver todas as features planejadas!
