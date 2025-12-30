from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Rollback cadastro_* para vendas_* via migrate cadastro 0002"

    def handle(self, *args, **options):
        call_command('migrate', 'cadastro', '0002')
        self.stdout.write('Rollback executado: tabelas vendas_* restauradas')
