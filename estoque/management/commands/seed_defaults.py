from django.core.management.base import BaseCommand
from cadastro.models import Address, Supplier, Customer
from estoque.models import Deposito, MotivoAjuste


class Command(BaseCommand):
    help = "Cria dados padrão para estoque/cadastro (depósitos, motivos, fornecedor e cliente)"

    def handle(self, *args, **options):
        dep_central, _ = Deposito.objects.get_or_create(nome="Deposito Central")
        dep_loja1, _ = Deposito.objects.get_or_create(nome="Loja 1")
        self.stdout.write(f"DEPOSITO_CENTRAL {dep_central.slug}")
        self.stdout.write(f"DEPOSITO_LOJA1 {dep_loja1.slug}")

        for code, name in [
            ("INVENTARIO", "Ajuste de Inventário"),
            ("QUEBRA", "Quebra/Dano"),
            ("DEVOLUCAO", "Devolução"),
        ]:
            MotivoAjuste.objects.get_or_create(codigo=code, defaults={"nome": name})
        self.stdout.write("MOTIVOS_OK")

        addr1, _ = Address.objects.get_or_create(logradouro="Rua A", cidade="Rondonópolis")
        forn, _ = Supplier.objects.get_or_create(nome="Fornecedor X")
        forn.enderecos.add(addr1)
        self.stdout.write(f"FORNECEDOR {forn.slug}")

        addr2, _ = Address.objects.get_or_create(logradouro="Av. B", cidade="Rondonópolis")
        cli, _ = Customer.objects.get_or_create(nome="Cliente Y")
        cli.enderecos.add(addr2)
        self.stdout.write(f"CLIENTE {cli.slug}")

        self.stdout.write("SEED_DEFAULTS_OK")
