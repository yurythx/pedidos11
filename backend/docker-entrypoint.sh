#!/bin/bash
set -e

echo "🔄 Aguardando banco de dados..."
sleep 5
echo "✅ Continuando..."

echo "🔄 Criando diretório static..."
mkdir -p /app/static
echo "✅ Diretório static criado"

echo "🔄 Executando migrações..."
python manage.py migrate --noinput

echo "🔄 Criando dados iniciais do sistema..."
python manage.py shell << 'PYEOF'
import os
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from tenant.models import Empresa
from locations.models import Endereco
from stock.models import Deposito
try:
    from financial.models import Caixa
except ImportError:
    Caixa = None
try:
    from catalog.models import Categoria
except ImportError:
    Categoria = None

User = get_user_model()

# 1. CRIAR EMPRESA PADRÃO
print("📊 Criando empresa...")
empresa, created = Empresa.objects.get_or_create(
    cnpj='00.000.000/0001-91',  # CNPJ válido para testes
    defaults={
        'razao_social': 'Projeto Nix - Empresa Padrão',
        'nome_fantasia': 'Nix ERP',
        'is_active': True
    }
)
if created:
    print(f"✅ Empresa criada: {empresa.nome_fantasia}")
else:
    print(f"✅ Empresa já existe: {empresa.nome_fantasia}")

# 2. CRIAR ENDEREÇO DA EMPRESA
print("📍 Criando endereço da empresa...")
endereco, created = Endereco.objects.get_or_create(
    content_type=ContentType.objects.get_for_model(empresa),
    object_id=empresa.id,
    defaults={
        'empresa': empresa,
        'tipo': 'COMERCIAL',
        'logradouro': 'Rua Principal',
        'numero': '100',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'uf': 'SP',
        'cep': '01001-000'
    }
)
if created:
    print(f"✅ Endereço criado: {endereco.logradouro}")
else:
    print(f"✅ Endereço já existe")

# 3. CRIAR SUPERUSUÁRIO
print("👤 Criando superusuário...")
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@projetonix.com',
        password='admin123',
        empresa=empresa,
        first_name='Administrador',
        last_name='Sistema'
    )
    print(f"✅ Superusuário criado: admin/admin123")
else:
    print(f"✅ Superusuário já existe: admin")

# 4. CRIAR DEPÓSITO PRINCIPAL
print("📦 Criando depósito principal...")
deposito, created = Deposito.objects.get_or_create(
    empresa=empresa,
    codigo='DEP001',
    defaults={
        'nome': 'Depósito Principal',
        'is_padrao': True
    }
)
if created:
    print(f"✅ Depósito criado: {deposito.nome}")
else:
    print(f"✅ Depósito já existe: {deposito.nome}")

# 5. CRIAR CAIXA PRINCIPAL
print("💰 Criando caixa principal...")
if Caixa is not None:
    caixa, created = Caixa.objects.get_or_create(
        empresa=empresa,
        nome='Caixa Principal',
        defaults={
            'ativo': True
        }
    )
    if created:
        print(f"✅ Caixa criado: {caixa.nome}")
    else:
        print(f"✅ Caixa já existe: {caixa.nome}")
else:
    print("⚠️  Modelo Caixa não disponível")

# 6. CRIAR CATEGORIAS PADRÃO
print("📁 Criando categorias padrão...")
if Categoria is not None:
    categorias_padrao = [
        {'nome': 'Bebidas', 'descricao': 'Bebidas em geral'},
        {'nome': 'Alimentos', 'descricao': 'Alimentos diversos'},
        {'nome': 'Limpeza', 'descricao': 'Produtos de limpeza'},
        {'nome': 'Higiene', 'descricao': 'Produtos de higiene'},
    ]
    
    for cat_data in categorias_padrao:
        cat, created = Categoria.objects.get_or_create(
            empresa=empresa,
            nome=cat_data['nome'],
            defaults={
                'descricao': cat_data['descricao']
            }
        )
        if created:
            print(f"  ✅ Categoria criada: {cat.nome}")
    
    print(f"✅ {len(categorias_padrao)} categorias padrão criadas/verificadas")
else:
    print("⚠️  Modelo Categoria não disponível")

print("")
print("=" * 60)
print("✨ DADOS INICIAIS CRIADOS COM SUCESSO!")
print("=" * 60)
print("")
print("📊 Resumo:")
print(f"  - Empresa: {empresa.nome_fantasia}")
print(f"  - CNPJ: {empresa.cnpj}")
print(f"  - Superusuário: admin / admin123")
print(f"  - Depósito: {deposito.nome}")
print("")
print("🌐 Acesse o sistema:")
print("  - Admin: http://seu-dominio:8002/admin")
print("  - Login: admin / admin123")
print("")
PYEOF

echo "🚀 Iniciando servidor..."
exec "$@"
