import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenant.models import Empresa

User = get_user_model()

def create_suporte():
    # 1. Garantir que existe uma empresa padrão
    empresa, created = Empresa.objects.get_or_create(
        cnpj='00.000.000/0000-00',
        defaults={
            'nome_fantasia': 'Empresa Suporte',
            'razao_social': 'Empresa Suporte LTDA',
            'is_active': True
        }
    )
    if created:
        print(f"Empresa '{empresa.nome_fantasia}' criada.")
    else:
        print(f"Empresa '{empresa.nome_fantasia}' encontrada.")

    # 2. Criar ou atualizar o usuário suporte
    username = 'suporte'
    email = 'suporte@pedidos11.com'
    password = 'suporte123'

    try:
        user = User.objects.get(username=username)
        print(f"Usuário '{username}' encontrado. Atualizando senha e permissões...")
    except User.DoesNotExist:
        user = User(username=username, email=email)
        print(f"Criando usuário '{username}'...")

    user.set_password(password)
    user.empresa = empresa
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.cargo = 'ADMIN' # Assumindo que 'ADMIN' é uma opção válida em TipoCargo
    user.save()
    
    print(f"Usuário '{username}' configurado com sucesso! Senha: '{password}'")

if __name__ == '__main__':
    create_suporte()
