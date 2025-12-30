from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Cria grupos padrão e atribui permissões por app, adiciona usuário suporte ao grupo Admin"

    def handle(self, *args, **options):
        mapping = {
            'Admin': None,
            'Cadastro': ['cadastro'],
            'Catálogo': ['catalogo'],
            'Vendas': ['vendas'],
            'Estoque': ['estoque'],
            'Compras': ['compras'],
            'Financeiro': ['financeiro'],
            'Relatórios': ['relatorios'],
        }
        for gname, apps in mapping.items():
            group, _ = Group.objects.get_or_create(name=gname)
            perms = Permission.objects.all() if apps is None else Permission.objects.filter(content_type__app_label__in=apps)
            group.permissions.set(perms)
        user = User.objects.filter(username='suporte').first()
        if user:
            admin = Group.objects.get(name='Admin')
            user.groups.add(admin)
        self.stdout.write(self.style.SUCCESS('Grupos e permissões configurados'))
