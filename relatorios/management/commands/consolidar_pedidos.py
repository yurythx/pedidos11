from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum
from vendas.models import Pedido, ItemPedido
from estoque.models import StockMovement
from financeiro.models import LedgerEntry


class Command(BaseCommand):
    def handle(self, *args, **options):
        prontos = 0
        faturados = 0
        atualizados = 0
        for ped in Pedido.objects.all():
            itens_q = ItemPedido.objects.filter(pedido=ped).aggregate(Sum("quantidade"))["quantidade__sum"] or 0
            mov_out = StockMovement.objects.filter(pedido=ped, tipo=StockMovement.Tipo.OUT).aggregate(Sum("quantidade"))["quantidade__sum"] or 0
            receita_vista = LedgerEntry.objects.filter(pedido=ped, debit_account="Caixa", credit_account="Receita de Vendas").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            receita_prazo = LedgerEntry.objects.filter(pedido=ped, debit_account="Clientes", credit_account="Receita de Vendas").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            ready = mov_out == itens_q and itens_q > 0
            invoiced = (receita_vista > 0 or receita_prazo > 0) and ped.total > 0
            if ready:
                prontos += 1
            if invoiced:
                faturados += 1
            new_status = ped.status
            if ready and not invoiced:
                new_status = Pedido.Status.PREPARANDO
            elif ready and invoiced:
                new_status = Pedido.Status.ENVIADO
            elif not ready and not invoiced:
                new_status = Pedido.Status.PENDENTE
            if new_status != ped.status:
                ped.status = new_status
                ped.save(update_fields=["status"])
                atualizados += 1
        self.stdout.write(f"Pedidos prontos: {prontos}")
        self.stdout.write(f"Pedidos faturados: {faturados}")
        self.stdout.write(f"Pedidos com status atualizado: {atualizados}")
