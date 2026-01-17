from django.test import TestCase
from decimal import Decimal
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito, Movimentacao, TipoMovimentacao
from stock.services import StockService
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class SaldoNegativoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa Saldo',
            razao_social='Empresa Saldo LTDA',
            cnpj='11222333000181',
            email='saldo@empresa.test',
        )
        self.user = CustomUser.objects.create_user(
            username='saldo',
            email='saldo@empresa.test',
            password='123456',
            empresa=self.empresa,
            cargo=TipoCargo.ESTOQUISTA,
        )
        self.categoria = Categoria.objects.create(
            empresa=self.empresa,
            nome='Cat Saldo',
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Produto Saldo',
            categoria=self.categoria,
            tipo=TipoProduto.FINAL,
            preco_venda=Decimal('10.00'),
            preco_custo=Decimal('5.00'),
        )
        self.deposito = Deposito.objects.create(
            empresa=self.empresa,
            nome='Depósito Saldo',
            is_padrao=True,
        )
        StockService.dar_entrada_com_lote(
            produto=self.produto,
            deposito=self.deposito,
            quantidade=Decimal('2.000'),
            codigo_lote='LOTE-SALDO',
            data_validade=date.today() + timedelta(days=90),
        )

    def test_impede_saldo_negativo(self):
        with self.assertRaises(ValidationError):
            Movimentacao.objects.create(
                empresa=self.empresa,
                produto=self.produto,
                deposito=self.deposito,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=Decimal('3.000'),
                valor_unitario=self.produto.preco_custo,
                documento='TEST-SALDO-NEG',
                usuario=self.user.username,
            )
