"""
Script para criar usuários iniciais via Django shell.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo

# Criar empresa se não existir
empresa, created = Empresa.objects.get_or_create(
    cnpj='00000000000191',
    defaults={
        'nome_fantasia': 'Restaurante Demo',
        'razao_social': 'Restaurante Demo LTDA',
    }
)
print(f"{'✅ Empresa criada' if created else 'ℹ️  Empresa já existe'}: {empresa.nome_fantasia}")

# Criar superusuário "suporte"
if not CustomUser.objects.filter(username='suporte').exists():
    suporte = CustomUser.objects.create_superuser(
        username='suporte',
        email='suporte@demo.com',
        password='suporte123',
        empresa=empresa,
        cargo=TipoCargo.ADMIN,
        first_name='Suporte',
        last_name='Técnico'
    )
    print(f"✅ Superusuário criado: {suporte.username} / suporte123")
else:
    print("ℹ️  Usuário 'suporte' já existe")

# Criar admin também
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
    print(f"✅ Superusuário criado: {admin.username} / admin123")
else:
    print("ℹ️  Usuário 'admin' já existe")

print("\n✅ Setup completo!")
print("🌐 Acesse Admin em:")
print("   http://192.168.1.121:8002/admin/")
print("   http://api.projetohavoc.shop:8002/admin/")
print("👤 Login: suporte / suporte123")
print("👤 Login: admin / admin123")
