from django.core.management.base import BaseCommand
from financeiro.models import Account, CostCenter


class Command(BaseCommand):
    help = "Seed default financial accounts and cost centers"

    def handle(self, *args, **options):
        defaults = [
            {"nome": "Caixa", "codigo": "1.1.1", "tipo": Account.Tipo.ATIVO},
            {"nome": "Receita de Vendas", "codigo": "4.1.1", "tipo": Account.Tipo.RECEITA},
            {"nome": "Estoque", "codigo": "1.2.3", "tipo": Account.Tipo.ATIVO},
            {"nome": "Custo das Vendas", "codigo": "3.1.1", "tipo": Account.Tipo.DESPESA},
        ]
        for d in defaults:
            Account.objects.get_or_create(codigo=d["codigo"], defaults=d)
        CostCenter.objects.get_or_create(codigo="LJ1", defaults={"nome": "Loja 1"})
        self.stdout.write(self.style.SUCCESS("Default accounts and cost centers seeded"))
