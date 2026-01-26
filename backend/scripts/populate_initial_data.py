"""
Script para popular dados iniciais do Projeto Nix.
Execute após rodar migrations: python manage.py shell < scripts/populate_initial_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from stock.models import Deposito
from restaurant.models import SetorImpressao
from catalog.models import Categoria
from decimal import Decimal

def criar_dados_iniciais():
    """Cria dados iniciais para teste/desenvolvimento."""
    
    print("🚀 Criando dados iniciais...\n")
    
    # 1. Criar Empresa
    print("📦 Criando empresa demo...")
    empresa, created = Empresa.objects.get_or_create(
        cnpj='00000000000191',
        defaults={
            'nome_fantasia': 'Restaurante Demo',
            'razao_social': 'Restaurante Demo LTDA',
            'inscricao_estadual': '123456789',
        }
    )
    if created:
        print(f"   ✅ Empresa criada: {empresa.nome_fantasia}")
    else:
        print(f"   ℹ️  Empresa já existe: {empresa.nome_fantasia}")
    
    # 2. Criar Superusuário
    print("\n👤 Criando superusuário...")
    if not CustomUser.objects.filter(username='admin').exists():
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@demo.com',
            password='admin123',
            empresa=empresa,
            cargo=TipoCargo.ADMIN,
            first_name='Administrador',
            last_name='Sistema'
        )
        print(f"   ✅ Superusuário criado: {admin.username} / admin123")
    else:
        print("   ℹ️  Superusuário já existe: admin")
    
    # 3. Criar usuários de teste
    print("\n👥 Criando usuários de teste...")
    usuarios_teste = [
        ('garcom1', 'Garçom', 'Silva', TipoCargo.VENDEDOR),
        ('gerente1', 'Gerente', 'Santos', TipoCargo.GERENTE),
    ]
    
    for username, first, last, cargo in usuarios_teste:
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(
                username=username,
                email=f'{username}@demo.com',
                password='senha123',
                empresa=empresa,
                cargo=cargo,
                first_name=first,
                last_name=last
            )
            print(f"   ✅ Usuário criado: {username} / senha123 ({cargo})")
        else:
            print(f"   ℹ️  Usuário já existe: {username}")
    
    # 4. Criar Depósito
    print("\n📦 Criando depósito...")
    deposito, created = Deposito.objects.get_or_create(
        empresa=empresa,
        codigo='LP01',
        defaults={
            'nome': 'Loja Principal',
            'is_padrao': True
        }
    )
    if created:
        print(f"   ✅ Depósito criado: {deposito.nome}")
    else:
        print(f"   ℹ️  Depósito já existe: {deposito.nome}")
    
    # 5. Criar Setores de Impressão (Food Service)
    print("\n🍳 Criando setores de impressão...")
    setores = [
        ('Cozinha', '#EF4444', 1),
        ('Bar', '#3B82F6', 2),
        ('Copa', '#10B981', 3),
        ('Churrasco', '#F59E0B', 4),
    ]
    
    for nome, cor, ordem in setores:
        setor, created = SetorImpressao.objects.get_or_create(
            empresa=empresa,
            nome=nome,
            defaults={'cor': cor, 'ordem': ordem}
        )
        if created:
            print(f"   ✅ Setor criado: {nome} ({cor})")
        else:
            print(f"   ℹ️  Setor já existe: {nome}")
    
    # 6. Criar Categorias
    print("\n📁 Criando categorias...")
    categorias = [
        ('Bebidas', 1),
        ('Lanches', 2),
        ('Pratos', 3),
        ('Sobremesas', 4),
        ('Petiscos', 5),
    ]
    
    for nome, ordem in categorias:
        cat, created = Categoria.objects.get_or_create(
            empresa=empresa,
            nome=nome,
            defaults={'ordem': ordem}
        )
        if created:
            print(f"   ✅ Categoria criada: {nome}")
        else:
            print(f"   ℹ️  Categoria já existe: {nome}")
    
    # 7. Criar Mesas (Restaurant)
    print("\n🪑 Criando mesas...")
    from restaurant.models import Mesa
    for i in range(1, 11):  # Mesas 1 a 10
        mesa, created = Mesa.objects.get_or_create(
            empresa=empresa,
            numero=i,
            defaults={'capacidade': 4}
        )
        if created:
            print(f"   ✅ Mesa {i} criada")
    
    print(f"\n   ℹ️  Total de mesas: {Mesa.objects.filter(empresa=empresa).count()}")
    
    # 8. Criar Comandas
    print("\n🎫 Criando comandas...")
    from restaurant.models import Comanda
    for i in range(1, 21):  # Comandas A01 a A20
        codigo = f"A{i:02d}"
        comanda, created = Comanda.objects.get_or_create(
            empresa=empresa,
            codigo=codigo
        )
        if created:
            print(f"   ✅ Comanda {codigo} criada")
    
    print(f"\n   ℹ️  Total de comandas: {Comanda.objects.filter(empresa=empresa).count()}")
    
    print("\n" + "="*50)
    print("✅ Dados iniciais criados com sucesso!")
    print("="*50)
    print("\n📋 Credenciais de acesso:")
    print("   Admin: admin / admin123")
    print("   Garçom: garcom1 / senha123")
    print("   Gerente: gerente1 / senha123")
    print("\n🌐 Acesse:")
    print("   Django Admin (IP):      http://192.168.1.121:8002/admin/")
    print("   Django Admin (Domínio): http://api.projetohavoc.shop:8002/admin/")
    print("   API Swagger (IP):       http://192.168.1.121:8002/api/docs/")
    print("\n")

if __name__ == '__main__':
    criar_dados_iniciais()
