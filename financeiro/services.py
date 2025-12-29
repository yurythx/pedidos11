from decimal import Decimal
from django.db import transaction
from vendas.models import Pedido
from .models import LedgerEntry, Account, CostCenter


class FinanceiroService:
    @staticmethod
    def registrar_receita_venda(pedido: Pedido, cost_center_code: str | None = None):
        with transaction.atomic():
            if pedido.total <= 0:
                return
            cc = None
            if cost_center_code:
                cc = CostCenter.objects.filter(codigo=cost_center_code).first()
            caixa = Account.objects.filter(nome="Caixa").first()
            receita = Account.objects.filter(nome="Receita de Vendas").first()
            LedgerEntry.objects.create(
                pedido=pedido,
                descricao=f"Venda {pedido.slug}",
                debit_account="Caixa",
                credit_account="Receita de Vendas",
                valor=pedido.total,
                debit_account_ref=caixa,
                credit_account_ref=receita,
                cost_center=cc,
            )

    @staticmethod
    def registrar_custo_venda(pedido: Pedido, cost_center_code: str | None = None):
        with transaction.atomic():
            total_custo = sum((i.quantidade * i.produto.custo for i in pedido.itens.all()), Decimal("0.00"))
            if total_custo <= 0:
                return
            cc = None
            if cost_center_code:
                cc = CostCenter.objects.filter(codigo=cost_center_code).first()
            cogs = Account.objects.filter(nome="Custo das Vendas").first()
            estoque = Account.objects.filter(nome="Estoque").first()
            LedgerEntry.objects.create(
                pedido=pedido,
                descricao=f"COGS {pedido.slug}",
                debit_account="Custo das Vendas",
                credit_account="Estoque",
                valor=total_custo,
                debit_account_ref=cogs,
                credit_account_ref=estoque,
                cost_center=cc,
            )
