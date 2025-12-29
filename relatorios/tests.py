from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from vendas.models import Categoria, Produto, Pedido, ItemPedido


class RelatoriosAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(username="admin", password="p", is_staff=True)
        self.client.force_authenticate(self.admin)
        self.cat_b = Categoria.objects.create(nome="Bebidas")
        self.cat_l = Categoria.objects.create(nome="Sanduíches")
        self.suco = Produto.objects.create(nome="Suco", categoria=self.cat_b, preco=Decimal("8.00"), disponivel=True)
        self.agua = Produto.objects.create(nome="Água", categoria=self.cat_b, preco=Decimal("5.00"), disponivel=True)
        self.burger = Produto.objects.create(nome="X-Burger", categoria=self.cat_l, preco=Decimal("25.00"), disponivel=True)
        self.user = get_user_model().objects.create_user(username="report_user", password="p")
        # Pedido 1
        p1 = Pedido.objects.create(usuario=self.user)
        ItemPedido.objects.create(pedido=p1, produto=self.suco, quantidade=2, preco_unitario=self.suco.preco)
        ItemPedido.objects.create(pedido=p1, produto=self.agua, quantidade=1, preco_unitario=self.agua.preco)
        p1.total = Decimal("21.00")
        p1.save(update_fields=["total"])
        # Pedido 2
        p2 = Pedido.objects.create(usuario=self.user)
        ItemPedido.objects.create(pedido=p2, produto=self.burger, quantidade=2, preco_unitario=self.burger.preco)
        p2.total = Decimal("50.00")
        p2.save(update_fields=["total"])

    def test_faturamento(self):
        url = reverse("relatorios-faturamento")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total_faturamento"], "71.00")
        self.assertEqual(resp.data["pedidos"], 2)
        resp_cc = self.client.get(url, {"cost_center": "LJ1"})
        self.assertEqual(resp_cc.status_code, 200)

    def test_itens_mais_vendidos(self):
        url = reverse("relatorios-itens")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        slugs = [i["produto_slug"] for i in resp.data]
        self.assertIn(self.burger.slug, slugs)
        self.assertIn(self.suco.slug, slugs)
        resp_cc = self.client.get(url, {"cost_center": "LJ1"})
        self.assertEqual(resp_cc.status_code, 200)

    def test_vendas_por_categoria(self):
        url = reverse("relatorios-categorias")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        cats = {i["categoria_slug"]: i for i in resp.data}
        self.assertIn(self.cat_b.slug, cats)
        self.assertIn(self.cat_l.slug, cats)
        resp_cc = self.client.get(url, {"cost_center": "LJ1"})
        self.assertEqual(resp_cc.status_code, 200)

    def test_csv_endpoints(self):
        r1 = self.client.get(reverse("relatorios-faturamento-csv"))
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1["Content-Type"], "text/csv")
        r2 = self.client.get(reverse("relatorios-itens-csv"))
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2["Content-Type"], "text/csv")
        r3 = self.client.get(reverse("relatorios-categorias-csv"))
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3["Content-Type"], "text/csv")

    def test_estoque_depositos_relatorios(self):
        # cria alguns movimentos para alimentar relatório
        from estoque.models import StockMovement, Deposito
        dep = Deposito.objects.create(nome="Central")
        StockMovement.objects.create(produto=self.suco, tipo=StockMovement.Tipo.IN, quantidade=5, deposito=dep)
        StockMovement.objects.create(produto=self.suco, tipo=StockMovement.Tipo.OUT, quantidade=2, deposito=dep)
        url = reverse("relatorios-estoque-depositos")
        resp = self.client.get(url, {"produto": self.suco.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.data, list))
        url_csv = reverse("relatorios-estoque-depositos-csv")
        resp_csv = self.client.get(url_csv, {"produto": self.suco.slug})
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv["Content-Type"], "text/csv")

    def test_ajustes_motivo_relatorios(self):
        from estoque.models import StockMovement, MotivoAjuste
        motivo = MotivoAjuste.objects.create(codigo="INVENTARIO", nome="Inventário")
        StockMovement.objects.create(produto=self.suco, tipo=StockMovement.Tipo.ADJUST, quantidade=-1, motivo_ajuste=motivo)
        url = reverse("relatorios-ajustes-motivo")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.data, list))
        url_csv = reverse("relatorios-ajustes-motivo-csv")
        resp_csv = self.client.get(url_csv)
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv["Content-Type"], "text/csv")
