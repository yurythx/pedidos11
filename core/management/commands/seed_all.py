from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Aplica seeds de dados usando comandos específicos de cada app."

    def handle(self, *args, **options):
        # contas financeiras
        try:
            call_command('seed_contas_financeiras')
        except Exception:
            try:
                call_command('seed_accounts')
            except Exception:
                self.stdout.write(self.style.WARNING('financeiro.seed_contas_financeiras/seed_accounts não disponível'))
        # clientes
        try:
            call_command('seed_clientes')
        except Exception:
            self.stdout.write(self.style.WARNING('cadastro.seed_clientes não disponível'))
        # estoque inicial
        try:
            call_command('seed_estoque_inicial')
        except Exception:
            try:
                call_command('seed_defaults')
            except Exception:
                self.stdout.write(self.style.WARNING('estoque.seed_estoque_inicial/seed_defaults não disponível'))
        # demo opcional
        try:
            call_command('seed_demo')
        except Exception:
            self.stdout.write(self.style.WARNING('vendas.seed_demo não disponível'))
        self.stdout.write(self.style.SUCCESS('Seeds executados'))
