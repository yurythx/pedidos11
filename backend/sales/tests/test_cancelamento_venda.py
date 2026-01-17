from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito, Saldo, Movimentacao, TipoMovimentacao
from sales.models import Venda, ItemVenda, StatusVenda
from sales.services import VendaService
from stock.services import StockService

class CancelamentoVendaTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa Teste',
            razao_social='Empresa Teste LTDA',
            cnpj='11222333000181',
            email='contato@empresa.test',
        )
        self.user = CustomUser.objects.create_user(
            username='tester2',
            email='tester2@empresa.test',
            password='123456',
            empresa=self.empresa,
            cargo=TipoCargo.GERENTE,
        )
        self.categoria = Categoria.objects.create(
            empresa=self.empresa,
            nome='Categoria Teste',
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Produto Final 2',
            categoria=self.categoria,
            tipo=TipoProduto.FINAL,
            preco_venda=Decimal('40.00'),
            preco_custo=Decimal('20.00'),
        )
        self.deposito = Deposito.objects.create(
            empresa=self.empresa,
            nome='Depósito Teste 2',
            is_padrao=True,
        )
        StockService.dar_entrada_com_lote(
            produto=self.produto,
            deposito=self.deposito,
            quantidade=Decimal('10.000'),
            codigo_lote='LOTE-CANC',
            data_validade=date.today() + timedelta(days=365),
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
            quantidade=Decimal('3.000'),
            preco_unitario=self.produto.preco_venda,
            desconto=Decimal('0.00'),
        )

    def test_cancelar_venda_devolve_estoque(self):
        VendaService.finalizar_venda(
            venda_id=self.venda.id,
            deposito_id=self.deposito.id,
            usuario=self.user.username,
            usar_lotes=True,
            gerar_conta_receber=False,
        )
        saldo_pos = Saldo.objects.get(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
        )
        self.assertEqual(saldo_pos.quantidade, Decimal('7.000'))
        VendaService.cancelar_venda(
            venda_id=self.venda.id,
            motivo='Teste cancelamento',
            usuario=self.user.username,
        )
        saldo_final = Saldo.objects.get(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
        )
        self.assertEqual(saldo_final.quantidade, Decimal('10.000'))
        venda = Venda.objects.get(id=self.venda.id)
        self.assertEqual(venda.status, StatusVenda.CANCELADA)
        movs_saida = Movimentacao.objects.filter(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
            tipo=TipoMovimentacao.SAIDA,
            documento__startswith='VENDA-',
        )
        movs_entrada = Movimentacao.objects.filter(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
            tipo=TipoMovimentacao.ENTRADA,
            documento__startswith='CANCEL-VENDA-',
        )
        self.assertTrue(movs_saida.exists())
        self.assertTrue(movs_entrada.exists())
