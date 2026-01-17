from django.test import TestCase
from decimal import Decimal
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito, Movimentacao, TipoMovimentacao
from sales.models import Venda, ItemVenda, StatusVenda
from sales.services import VendaService
from stock.services import StockService
from financial.services import FinanceiroService
from datetime import date

class VendaFinanceiroFIFOTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa Teste',
            razao_social='Empresa Teste LTDA',
            cnpj='11222333000181',
            email='contato@empresa.test',
        )
        self.user = CustomUser.objects.create_user(
            username='tester',
            email='tester@empresa.test',
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
            nome='Produto Final',
            categoria=self.categoria,
            tipo=TipoProduto.FINAL,
            preco_venda=Decimal('50.00'),
            preco_custo=Decimal('30.00'),
        )
        self.deposito = Deposito.objects.create(
            empresa=self.empresa,
            nome='Depósito Teste',
            is_padrao=True,
        )
        self.venda = Venda.objects.create(
            empresa=self.empresa,
            vendedor=self.user,
            tipo_pagamento='DINHEIRO',
            observacoes='Teste integração serviços',
        )
        ItemVenda.objects.create(
            empresa=self.empresa,
            venda=self.venda,
            produto=self.produto,
            quantidade=Decimal('2.000'),
            preco_unitario=self.produto.preco_venda,
            desconto=Decimal('0.00'),
        )
        StockService.dar_entrada_com_lote(
            produto=self.produto,
            deposito=self.deposito,
            quantidade=Decimal('10.000'),
            codigo_lote='LOTE-TST',
            data_validade=date.today().replace(year=date.today().year + 1),
        )

    def test_finalizar_venda_gera_cr_e_fifo(self):
        valid = VendaService.validar_estoque_disponivel(
            venda_id=self.venda.id,
            deposito_id=self.deposito.id,
        )
        self.assertTrue(valid['disponivel'])
        venda_fin = VendaService.finalizar_venda(
            venda_id=self.venda.id,
            deposito_id=self.deposito.id,
            usuario=self.user.username,
            usar_lotes=True,
            gerar_conta_receber=True,
        )
        self.assertEqual(venda_fin.status, StatusVenda.FINALIZADA)
        self.assertTrue(venda_fin.contas_receber.exists())
        cr = venda_fin.contas_receber.first()
        FinanceiroService.baixar_conta_receber(
            conta_id=cr.id,
            tipo_pagamento='DINHEIRO',
        )
        cr.refresh_from_db()
        self.assertEqual(cr.status, 'PAGA')
        movs = Movimentacao.objects.filter(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
            tipo=TipoMovimentacao.SAIDA,
            documento__startswith='VENDA-',
        )
        self.assertTrue(movs.exists())
        self.assertTrue(any(m.lote_id for m in movs))
