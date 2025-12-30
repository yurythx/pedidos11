from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum
from vendas.models import Produto, Pedido, ItemPedido
from compras.models import PurchaseOrder, PurchaseItem
from estoque.models import StockMovement, StockReceiptItem
from financeiro.models import LedgerEntry, Title, TitleParcel


class Command(BaseCommand):
    def handle(self, *args, **options):
        erros = []
        for p in Produto.objects.all():
            saldo = 0
            for mv in StockMovement.objects.filter(produto=p).values("tipo", "quantidade"):
                if mv["tipo"] == StockMovement.Tipo.IN:
                    saldo += mv["quantidade"]
                elif mv["tipo"] == StockMovement.Tipo.OUT:
                    saldo -= mv["quantidade"]
                else:
                    saldo += mv["quantidade"]
            if saldo < 0:
                erros.append(f"Saldo negativo para produto {p.slug}: {saldo}")
        for po in PurchaseOrder.objects.all():
            total_itens = sum((i.subtotal() for i in po.itens.all()), Decimal("0"))
            if po.total != total_itens:
                erros.append(f"PO {po.slug} total {po.total} difere de itens {total_itens}")
            le = LedgerEntry.objects.filter(compra=po, debit_account="Estoque", credit_account="Fornecedores").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            if le != po.total:
                erros.append(f"PO {po.slug} ledger {le} difere do total {po.total}")
            itens_recibo = StockReceiptItem.objects.filter(recebimento__compra=po).aggregate(Sum("quantidade"))["quantidade__sum"] or 0
            movimentos_in = StockMovement.objects.filter(origem_slug=po.slug, tipo=StockMovement.Tipo.IN).aggregate(Sum("quantidade"))["quantidade__sum"] or 0
            if itens_recibo != movimentos_in:
                erros.append(f"PO {po.slug} recebidos {itens_recibo} difere de movimentos IN {movimentos_in}")
        for ped in Pedido.objects.all():
            total_itens = sum((i.subtotal() for i in ped.itens.all()), Decimal("0"))
            if ped.total != total_itens:
                erros.append(f"Pedido {ped.slug} total {ped.total} difere de itens {total_itens}")
            mov_out = StockMovement.objects.filter(pedido=ped, tipo=StockMovement.Tipo.OUT).aggregate(Sum("quantidade"))["quantidade__sum"] or 0
            itens_q = sum((i.quantidade for i in ped.itens.all()), 0)
            if mov_out != itens_q:
                erros.append(f"Pedido {ped.slug} OUT {mov_out} difere de itens {itens_q}")
            receita_vista = LedgerEntry.objects.filter(pedido=ped, debit_account="Caixa", credit_account="Receita de Vendas").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            receita_prazo = LedgerEntry.objects.filter(pedido=ped, debit_account="Clientes", credit_account="Receita de Vendas").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            if receita_vista == 0 and receita_prazo == 0 and ped.total > 0:
                erros.append(f"Pedido {ped.slug} sem receita registrada")
            cogs = LedgerEntry.objects.filter(pedido=ped, debit_account="Custo das Vendas", credit_account="Estoque").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
            esperado_cogs = sum((i.quantidade * i.produto.custo for i in ped.itens.all()), Decimal("0"))
            if cogs != esperado_cogs:
                erros.append(f"Pedido {ped.slug} COGS {cogs} difere de esperado {esperado_cogs}")
            if receita_prazo > 0:
                t = Title.objects.filter(pedido=ped, tipo=Title.Tipo.AR).first()
                if not t:
                    erros.append(f"Pedido {ped.slug} sem AR")
                else:
                    parcelas = TitleParcel.objects.filter(title=t).count()
                    if parcelas == 0:
                        erros.append(f"Pedido {ped.slug} AR sem parcelas")
                    recebimentos = LedgerEntry.objects.filter(pedido=ped, credit_account="Clientes", debit_account="Caixa").aggregate(Sum("valor"))["valor__sum"] or Decimal("0")
                    if recebimentos <= 0:
                        erros.append(f"Pedido {ped.slug} a prazo sem recebimento parcial")
        if erros:
            for e in erros:
                self.stdout.write(e)
        else:
            self.stdout.write("Fluxos OK")
