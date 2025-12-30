from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Verifica existência e contagem de vendas_* e cadastro_*"

    def handle(self, *args, **options):
        bases = ['produto', 'produtoimagem', 'produtoatributo', 'produtoatributovalor', 'produtovariacao']
        cur = connection.cursor()
        def count(table):
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                return cur.fetchone()[0]
            except Exception:
                return None
        for b in bases:
            old = f"vendas_{b}"
            new = f"cadastro_{b}"
            c_old = count(old)
            c_new = count(new)
            self.stdout.write(f"{old}={c_old if c_old is not None else 'missing'}; {new}={c_new if c_new is not None else 'missing'}")
