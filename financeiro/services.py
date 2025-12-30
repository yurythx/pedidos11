"""Serviços financeiros da aplicação.

Este módulo centraliza regras contábeis e de títulos (AR/AP), incluindo:
- registro de receitas de venda e custo das vendas (COGS);
- registro de compras e pagamentos a fornecedores;
- geração de títulos a receber (AR) e a pagar (AP), com suporte a parcelas;
- recebimentos de vendas com validação de saldo;
- estornos de compras.
"""
from decimal import Decimal
from django.db import transaction
from vendas.models import Pedido
from .models import LedgerEntry, Account, CostCenter


class FinanceiroService:
    """Facade de operações financeiras e contábeis.

    Métodos estáticos para manter atomicidade e uso simples em views/serializers.
    """
    @staticmethod
    def registrar_receita_venda(pedido: Pedido, cost_center_code: str | None = None):
        """Registra a receita de uma venda à vista.

        - Debita Caixa e credita Receita de Vendas.
        - Opcionalmente associa centro de custo.
        """
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
        """Registra o custo das vendas (COGS) do pedido.

        - Debita Custo das Vendas e credita Estoque.
        - Soma custo de cada item do pedido.
        """
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

    @staticmethod
    def registrar_compra(order):
        """Registra uma compra e gera título AP se não existir.

        - Debita Estoque e credita Fornecedores.
        - Cria Title AP com vencimento padrão de 30 dias.
        """
        from .models import LedgerEntry, Account, Title
        from decimal import Decimal
        from django.utils import timezone
        from datetime import timedelta
        total = Decimal(order.total or 0)
        if total <= 0:
            return
        estoque = Account.objects.filter(nome="Estoque").first()
        fornecedores = Account.objects.filter(nome="Fornecedores").first()
        LedgerEntry.objects.create(
            compra=order,
            descricao=f"Compra {order.slug}",
            debit_account="Estoque",
            credit_account="Fornecedores",
            valor=total,
            debit_account_ref=estoque,
            credit_account_ref=fornecedores,
            cost_center=order.cost_center,
        )
        if not Title.objects.filter(compra=order).exists():
            Title.objects.create(
                tipo=Title.Tipo.AP,
                compra=order,
                descricao=f"AP {order.slug}",
                valor=total,
                due_date=(timezone.now().date() + timedelta(days=30)),
                status=Title.Status.ABERTO,
                usuario=order.responsavel,
                cost_center=order.cost_center,
            )

    @staticmethod
    def registrar_pagamento_compra(order, valor):
        """Registra pagamento de compra (baixa parcial/total de AP).

        - Debita Fornecedores e credita Caixa.
        - Atualiza livro razão e mantém controle por centro de custo.
        """
        from .models import LedgerEntry, Account
        from decimal import Decimal
        v = Decimal(valor or 0)
        if v <= 0:
            return
        caixa = Account.objects.filter(nome="Caixa").first()
        fornecedores = Account.objects.filter(nome="Fornecedores").first()
        LedgerEntry.objects.create(
            compra=order,
            descricao=f"Pagamento Compra {order.slug}",
            debit_account="Fornecedores",
            credit_account="Caixa",
            valor=v,
            debit_account_ref=fornecedores,
            credit_account_ref=caixa,
            cost_center=order.cost_center,
        )

    @staticmethod
    def registrar_venda_a_prazo(pedido: Pedido, cost_center_code: str | None = None, parcelas: list | None = None):
        """Registra venda a prazo e gera AR e parcelas opcionais.

        - Debita Clientes e credita Receita de Vendas.
        - Cria Title AR, com due_date último vencimento se houver parcelas.
        - Cria TitleParcel para cada parcela fornecida.
        """
        from .models import LedgerEntry, Account, CostCenter, Title, TitleParcel
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal as D
        if pedido.total <= 0:
            return
        cc = None
        if cost_center_code:
            cc = CostCenter.objects.filter(codigo=cost_center_code).first()
        clientes = Account.objects.filter(nome="Clientes").first()
        receita = Account.objects.filter(nome="Receita de Vendas").first()
        LedgerEntry.objects.create(
            pedido=pedido,
            descricao=f"Venda a prazo {pedido.slug}",
            debit_account="Clientes",
            credit_account="Receita de Vendas",
            valor=pedido.total,
            debit_account_ref=clientes,
            credit_account_ref=receita,
            cost_center=cc or pedido.cost_center,
        )
        if not Title.objects.filter(pedido=pedido).exists():
            due = (timezone.now().date() + timedelta(days=30))
            total = D(pedido.total)
            if parcelas:
                total = sum(D(str(p.get('valor'))) for p in parcelas)
                import datetime
                last_due = max([datetime.date.fromisoformat(p.get('due_date')) for p in parcelas])
                due = last_due
            t = Title.objects.create(
                tipo=Title.Tipo.AR,
                pedido=pedido,
                descricao=f"AR {pedido.slug}",
                valor=total,
                due_date=due,
                status=Title.Status.ABERTO,
                usuario=pedido.usuario,
                cost_center=pedido.cost_center,
            )
            if parcelas:
                import datetime
                for p in parcelas:
                    TitleParcel.objects.create(
                        title=t,
                        valor=D(str(p.get('valor'))),
                        due_date=datetime.date.fromisoformat(p.get('due_date')),
                    )

    @staticmethod
    def receber_venda(pedido: Pedido, valor: Decimal):
        """Registra recebimento de venda (baixa de AR).

        - Valida que o valor não excede o outstanding.
        - Debita Caixa e credita Clientes.
        """
        from .models import LedgerEntry, Account
        from decimal import Decimal as D
        from django.db.models import Sum
        if valor <= 0:
            return
        sale = LedgerEntry.objects.filter(pedido=pedido, debit_account='Clientes').aggregate(Sum('valor'))['valor__sum'] or D('0')
        recv = LedgerEntry.objects.filter(pedido=pedido, credit_account='Clientes').aggregate(Sum('valor'))['valor__sum'] or D('0')
        outstanding = D(sale) - D(recv)
        if D(valor) > outstanding:
            raise ValueError("Valor excede o saldo a receber.")
        caixa = Account.objects.filter(nome="Caixa").first()
        clientes = Account.objects.filter(nome="Clientes").first()
        LedgerEntry.objects.create(
            pedido=pedido,
            descricao=f"Recebimento {pedido.slug}",
            debit_account="Caixa",
            credit_account="Clientes",
            valor=D(valor),
            debit_account_ref=caixa,
            credit_account_ref=clientes,
            cost_center=pedido.cost_center,
        )

    @staticmethod
    def registrar_estorno_compra(order):
        """Registra estorno de compra (reversão contábil).

        - Debita Fornecedores e credita Estoque.
        """
        from .models import LedgerEntry, Account
        from decimal import Decimal
        total = Decimal(order.total or 0)
        if total <= 0:
            return
        fornecedores = Account.objects.filter(nome="Fornecedores").first()
        estoque = Account.objects.filter(nome="Estoque").first()
        LedgerEntry.objects.create(
            compra=order,
            descricao=f"Estorno Compra {order.slug}",
            debit_account="Fornecedores",
            credit_account="Estoque",
            valor=total,
            debit_account_ref=fornecedores,
            credit_account_ref=estoque,
            cost_center=order.cost_center,
        )
