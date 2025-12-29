from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from vendas.models import Categoria, Produto, Pedido, ItemPedido
from financeiro.services import FinanceiroService
from financeiro.models import LedgerEntry, Account, CostCenter


class FinanceiroServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="u", password="p")
        self.cat = Categoria.objects.create(nome="Test")
        self.l = Produto.objects.create(nome="Produto", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        self.pedido = Pedido.objects.create(usuario=self.user)
        self.item = ItemPedido.objects.create(pedido=self.pedido, produto=self.l, quantidade=2, preco_unitario=self.l.preco)
        self.pedido.total = Decimal("20.00")
        self.pedido.save(update_fields=["total"])

    def test_registrar_receita_venda(self):
        FinanceiroService.registrar_receita_venda(self.pedido)
        lancs = LedgerEntry.objects.filter(pedido=self.pedido)
        self.assertEqual(lancs.count(), 1)
        self.assertEqual(lancs.first().valor, Decimal("20.00"))


class FinanceiroAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="admin", password="p", is_staff=True)
        self.client.force_authenticate(self.user)
        self.cat = Categoria.objects.create(nome="Finance")
        self.l = Produto.objects.create(nome="ProdutoF", categoria=self.cat, preco=Decimal("15.00"), disponivel=True)
        self.pedido = Pedido.objects.create(usuario=self.user)
        ItemPedido.objects.create(pedido=self.pedido, produto=self.l, quantidade=1, preco_unitario=self.l.preco)
        self.pedido.total = Decimal("15.00")
        self.pedido.save(update_fields=["total"])
        FinanceiroService.registrar_receita_venda(self.pedido)

    def test_resumo(self):
        url = reverse("financeiro-lancamento-resumo")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total_receita"], "15.00")

    def test_registrar_custo_venda(self):
        self.pedido2 = Pedido.objects.create(usuario=self.user)
        self.l.custo = Decimal("4.00")
        self.l.save(update_fields=["custo"])
        ItemPedido.objects.create(pedido=self.pedido2, produto=self.l, quantidade=3, preco_unitario=self.l.preco)
        FinanceiroService.registrar_custo_venda(self.pedido2)
        lancs = LedgerEntry.objects.filter(pedido=self.pedido2, debit_account="Custo das Vendas")
        self.assertEqual(lancs.count(), 1)
        self.assertEqual(lancs.first().valor, Decimal("12.00"))

    def test_contas_e_centros_resumo(self):
        caixa = Account.objects.create(nome="Caixa", codigo="1.1.1", tipo=Account.Tipo.ATIVO)
        receita = Account.objects.create(nome="Receita de Vendas", codigo="4.1.1", tipo=Account.Tipo.RECEITA)
        estoque = Account.objects.create(nome="Estoque", codigo="1.2.3", tipo=Account.Tipo.ATIVO)
        cogs = Account.objects.create(nome="Custo das Vendas", codigo="3.1.1", tipo=Account.Tipo.DESPESA)
        centro = CostCenter.objects.create(nome="Loja 1", codigo="LJ1")
        le1 = LedgerEntry.objects.create(pedido=self.pedido, descricao="Venda", debit_account="Caixa", credit_account="Receita de Vendas", valor=Decimal("20.00"), debit_account_ref=caixa, credit_account_ref=receita, cost_center=centro)
        le2 = LedgerEntry.objects.create(pedido=self.pedido, descricao="COGS", debit_account="Custo das Vendas", credit_account="Estoque", valor=Decimal("8.00"), debit_account_ref=cogs, credit_account_ref=estoque, cost_center=centro)
        url_contas = reverse("financeiro-lancamento-contas-resumo")
        resp_contas = self.client.get(url_contas, {"side": "debit"})
        self.assertEqual(resp_contas.status_code, 200)
        accounts = [a["account"] for a in resp_contas.data]
        self.assertIn("Caixa", accounts)
        self.assertIn("Custo das Vendas", accounts)
        url_centros = reverse("financeiro-lancamento-centros-resumo")
        resp_centros = self.client.get(url_centros)
        self.assertEqual(resp_centros.status_code, 200)
        centros = [c["centro_codigo"] for c in resp_centros.data]
        self.assertIn("LJ1", centros)
        resp_contas_cc = self.client.get(url_contas, {"side": "debit", "cost_center": "LJ1"})
        self.assertEqual(resp_contas_cc.status_code, 200)
        resp_centros_cc = self.client.get(url_centros, {"cost_center": "LJ1"})
        self.assertEqual(resp_centros_cc.status_code, 200)
        url_balanco = reverse("financeiro-lancamento-balanco")
        resp_bal = self.client.get(url_balanco, {"cost_center": "LJ1"})
        self.assertEqual(resp_bal.status_code, 200)
        self.assertTrue(resp_bal.data["balanced"])
        url_resumo_csv = reverse("financeiro-lancamento-resumo-csv")
        self.assertEqual(self.client.get(url_resumo_csv).status_code, 200)
        url_contas_csv = reverse("financeiro-lancamento-contas-resumo-csv")
        self.assertEqual(self.client.get(url_contas_csv, {"side": "debit"}).status_code, 200)
        url_centros_csv = reverse("financeiro-lancamento-centros-resumo-csv")
        self.assertEqual(self.client.get(url_centros_csv).status_code, 200)

    def test_user_default_cost_center_api(self):
        from django.contrib.auth import get_user_model
        su = get_user_model().objects.create_superuser(username="super", password="p")
        self.client.force_authenticate(su)
        centro = CostCenter.objects.create(nome="Loja 3", codigo="LJ3")
        url_defaults = reverse("financeiro-default-list")
        resp_post = self.client.post(url_defaults, {"user": self.user.id, "cost_center": centro.id}, format="json")
        self.assertEqual(resp_post.status_code, 201)
        resp_list = self.client.get(url_defaults)
        self.assertEqual(resp_list.status_code, 200)
