from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from vendas.models import Pedido, ItemPedido
from estoque.services import EstoqueService
from financeiro.services import FinanceiroService


class Command(BaseCommand):
    def handle(self, *args, **options):
        fixed = 0
        for ped in Pedido.objects.all():
            itens = list(ItemPedido.objects.filter(pedido=ped))
            movs = ped.movimentos_estoque.filter(tipo="OUT").count()
            if itens and movs == 0:
                with transaction.atomic():
                    for it in itens:
                        saldo = EstoqueService.saldo_produto(it.produto)
                        if saldo < it.quantidade:
                            EstoqueService.registrar_entrada(it.produto, quantidade=(it.quantidade - saldo), origem_slug="repair")
                    EstoqueService.registrar_saida(ped, itens)
                    FinanceiroService.registrar_receita_venda(ped)
                    FinanceiroService.registrar_custo_venda(ped)
                    fixed += 1
        self.stdout.write(f"Pedidos reparados: {fixed}")
