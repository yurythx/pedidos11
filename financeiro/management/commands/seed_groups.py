from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Cria grupos de acesso: operacao, estoque, financeiro"

    def handle(self, *args, **options):
        created = []
        for name in ["operacao", "estoque", "financeiro"]:
            g, was_created = Group.objects.get_or_create(name=name)
            created.append((name, was_created))
        for name, was_created in created:
            self.stdout.write(f"{name}: {'created' if was_created else 'exists'}")
