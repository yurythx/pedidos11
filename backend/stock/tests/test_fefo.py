from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito, Movimentacao, TipoMovimentacao, Lote
from sales.models import Venda, ItemVenda
from sales.services import VendaService
from stock.services import StockService

class FIFOTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa FEFO',
            razao_social='Empresa FEFO LTDA',
            cnpj='11222333000181',
            email='fefo@empresa.test',
        )
        self.user = CustomUser.objects.create_user(
            username='fefo',
            email='fefo@empresa.test',
            password='123456',
            empresa=self.empresa,
            cargo=TipoCargo.GERENTE,
        )
        self.categoria = Categoria.objects.create(
            empresa=self.empresa,
            nome='Cat FEFO',
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Produto FEFO',
            categoria=self.categoria,
            tipo=TipoProduto.FINAL,
            preco_venda=Decimal('10.00'),
            preco_custo=Decimal('5.00'),
        )
        self.deposito = Deposito.objects.create(
            empresa=self.empresa,
            nome='Depósito FEFO',
            is_padrao=True,
        )
        StockService.dar_entrada_com_lote(
            produto=self.produto,
            deposito=self.deposito,
            quantidade=Decimal('5.000'),
            codigo_lote='LOTE-A',
            data_validade=date.today() + timedelta(days=30),
        )
        StockService.dar_entrada_com_lote(
            produto=self.produto,
            deposito=self.deposito,
            quantidade=Decimal('5.000'),
            codigo_lote='LOTE-B',
            data_validade=date.today() + timedelta(days=120),
        )
        self.venda = Venda.objects.create(
            empresa=self.empresa,
            vendedor=self.user,
            tipo_pagamento='DINHEIRO',
        )
        ItemVenda.objects.create(
            empresa=self.empresa,
            venda=self.venda,
            produto=self.produto,
            quantidade=Decimal('7.000'),
            preco_unitario=self.produto.preco_venda,
            desconto=Decimal('0.00'),
        )

    def test_consumo_fifo_por_validade(self):
        VendaService.finalizar_venda(
            venda_id=self.venda.id,
            deposito_id=self.deposito.id,
            usuario=self.user.username,
            usar_lotes=True,
            gerar_conta_receber=False,
        )
        movs = Movimentacao.objects.filter(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
            tipo=TipoMovimentacao.SAIDA,
            documento__startswith='VENDA-',
        ).select_related('lote')
        self.assertTrue(movs.exists())
        qtd_lote_a = sum(m.quantidade for m in movs if m.lote and m.lote.codigo_lote == 'LOTE-A')
        qtd_lote_b = sum(m.quantidade for m in movs if m.lote and m.lote.codigo_lote == 'LOTE-B')
        self.assertEqual(qtd_lote_a, Decimal('5.000'))
        self.assertEqual(qtd_lote_b, Decimal('2.000'))
