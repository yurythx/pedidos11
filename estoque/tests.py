from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from rest_framework.test import APIClient
from django.urls import reverse
from vendas.models import Categoria, Produto, Pedido, ItemPedido
from .services import EstoqueService


class EstoqueServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="u", password="p")
        self.cat = Categoria.objects.create(nome="Insumos")
        self.l1 = Produto.objects.create(nome="X-Burger", categoria=self.cat, preco=Decimal("25.00"), disponivel=True)
        self.l2 = Produto.objects.create(nome="Suco", categoria=self.cat, preco=Decimal("8.00"), disponivel=True)
        EstoqueService.registrar_entrada(self.l1, 10, origem_slug="init")
        EstoqueService.registrar_entrada(self.l2, 5, origem_slug="init")
        self.pedido = Pedido.objects.create(usuario=self.user)

    def test_saldo_produto(self):
        self.assertEqual(EstoqueService.saldo_produto(self.l1), 10)
        self.assertEqual(EstoqueService.saldo_produto(self.l2), 5)

    def test_registrar_saida_reduz_saldo(self):
        item = ItemPedido.objects.create(pedido=self.pedido, produto=self.l1, quantidade=3, preco_unitario=self.l1.preco)
        EstoqueService.registrar_saida(self.pedido, [item])
        self.assertEqual(EstoqueService.saldo_produto(self.l1), 7)

    def test_bloqueia_saida_sem_estoque(self):
        item = ItemPedido.objects.create(pedido=self.pedido, produto=self.l2, quantidade=6, preco_unitario=self.l2.preco)
        with self.assertRaises(Exception):
            EstoqueService.registrar_saida(self.pedido, [item])


class EstoqueAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="admin", password="p", is_staff=True)
        self.client.force_authenticate(self.user)
        self.cat = Categoria.objects.create(nome="API")
        self.l = Produto.objects.create(nome="Produto", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        # Pedido com centro de custo
        from financeiro.models import CostCenter
        self.cc = CostCenter.objects.create(nome="Loja 1", codigo="LJ1")
        from vendas.models import Pedido, ItemPedido
        self.pedido = Pedido.objects.create(usuario=self.user, cost_center=self.cc)
        ItemPedido.objects.create(pedido=self.pedido, produto=self.l, quantidade=1, preco_unitario=self.l.preco)

    def test_entrada_e_saldo(self):
        url_entrada = reverse("estoque-movimento-entrada")
        resp = self.client.post(url_entrada, {"produto": self.l.slug, "quantidade": 7}, format="json")
        self.assertEqual(resp.status_code, 201)
        url_saldo = reverse("estoque-movimento-saldo")
        saldo = self.client.get(url_saldo, {"produto": self.l.slug})
        self.assertEqual(saldo.status_code, 200)
        self.assertEqual(saldo.data["saldo"], 7)

    def test_ajuste_negativo(self):
        EstoqueService.registrar_entrada(self.l, 5, origem_slug="init")
        url_ajuste = reverse("estoque-movimento-ajuste")
        resp = self.client.post(url_ajuste, {"produto": self.l.slug, "quantidade": -2}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(EstoqueService.saldo_produto(self.l), 3)

    def test_historico_filtra_por_cost_center(self):
        url_hist = reverse("estoque-movimento-historico")
        EstoqueService.registrar_entrada(self.l, 2, origem_slug="init")
        EstoqueService.registrar_saida(self.pedido, list(self.pedido.itens.all()))
        resp_all = self.client.get(url_hist, {"produto": self.l.slug})
        self.assertEqual(resp_all.status_code, 200)
        self.assertTrue(len(resp_all.data) >= 1)
        resp_cc = self.client.get(url_hist, {"produto": self.l.slug, "cost_center": "LJ1"})
        self.assertEqual(resp_cc.status_code, 200)
        url_csv = reverse("estoque-movimento-historico-csv")
        resp_csv = self.client.get(url_csv, {"produto": self.l.slug, "cost_center": "LJ1"})
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv["Content-Type"], "text/csv")

    def test_saldo_por_deposito_e_transferencia(self):
        from estoque.models import Deposito
        dep1 = Deposito.objects.create(nome="Central")
        dep2 = Deposito.objects.create(nome="Loja 1")
        url_entrada = reverse("estoque-movimento-entrada")
        resp_in = self.client.post(url_entrada, {"produto": self.l.slug, "quantidade": 5, "deposito": dep1.slug}, format="json")
        self.assertEqual(resp_in.status_code, 201)
        url_saldo = reverse("estoque-movimento-saldo")
        saldo1 = self.client.get(url_saldo, {"produto": self.l.slug, "deposito": dep1.slug})
        self.assertEqual(saldo1.status_code, 200)
        self.assertEqual(saldo1.data["saldo"], 5)
        url_transfer = reverse("estoque-movimento-transferir")
        resp_tr = self.client.post(url_transfer, {"produto": self.l.slug, "quantidade": 2, "origem": dep1.slug, "destino": dep2.slug}, format="json")
        self.assertEqual(resp_tr.status_code, 201)
        saldo1_after = self.client.get(url_saldo, {"produto": self.l.slug, "deposito": dep1.slug})
        saldo2_after = self.client.get(url_saldo, {"produto": self.l.slug, "deposito": dep2.slug})
        self.assertEqual(saldo1_after.data["saldo"], 3)
        self.assertEqual(saldo2_after.data["saldo"], 2)

    def test_estornar_recebimento(self):
        # cria recebimento via serviço e estorna via API
        from estoque.models import StockReceipt, Deposito
        dep = Deposito.objects.create(nome="CD")
        url_rec = reverse("estoque-recebimento-list")
        payload = {"documento": "NF-1", "deposito": dep.slug, "itens_payload": [{"produto": self.l.slug, "quantidade": 4}]}
        resp = self.client.post(url_rec, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        rid = resp.data["id"]
        url_saldo = reverse("estoque-movimento-saldo")
        saldo_dep = self.client.get(url_saldo, {"produto": self.l.slug, "deposito": dep.slug})
        self.assertEqual(saldo_dep.data["saldo"], 4)
        url_estornar = reverse("estoque-recebimento-estornar", kwargs={"pk": rid})
        resp_est = self.client.post(url_estornar, {}, format="json")
        self.assertEqual(resp_est.status_code, 200)
        saldo_dep2 = self.client.get(url_saldo, {"produto": self.l.slug, "deposito": dep.slug})
        self.assertEqual(saldo_dep2.data["saldo"], 0)
