from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Aplica rename de vendas_* para cadastro_* via migrate cadastro 0003"

    def handle(self, *args, **options):
        call_command('migrate', 'cadastro', '0003')
        self.stdout.write('Rename aplicado: tabelas cadastro_* ativas')
