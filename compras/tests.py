from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from cadastro.models import Supplier
from vendas.models import Categoria, Produto
from estoque.services import EstoqueService
from estoque.models import StockMovement
from financeiro.models import LedgerEntry, Account, CostCenter


class ComprasAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="fin", password="p", is_staff=True)
        self.client.force_authenticate(self.user)
        self.cat = Categoria.objects.create(nome="Insumos")
        self.prod = Produto.objects.create(nome="Farinha", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        self.fornec = Supplier.objects.create(nome="Fornecedor A")
        self.cc = CostCenter.objects.create(nome="Loja 1", codigo="LJ1")
        # garantir contas (caso seed não tenha rodado nesta base)
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1000", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1100", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Fornecedores", defaults={"codigo": "2000", "tipo": Account.Tipo.PASSIVO})
        # saldo inicial 0
        self.assertEqual(EstoqueService.saldo_produto(self.prod), 0)

    def test_criar_receber_e_pagar_compra(self):
        # criar compra
        url = reverse("compras-list")
        payload = {
            "fornecedor": self.fornec.slug,
            "documento": "NF-123",
            "cost_center": self.cc.codigo,
            "itens_payload": [
                {"produto": self.prod.slug, "quantidade": 5, "custo_unitario": "7.50"}
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        order_slug = resp.data["slug"]
        self.assertEqual(resp.data["total"], "37.50")
        # receber
        url_receber = reverse("compras-receber", kwargs={"slug": order_slug})
        rcv = self.client.post(url_receber, {}, format="json")
        self.assertEqual(rcv.status_code, 200)
        # saldo após recebimento
        self.assertEqual(EstoqueService.saldo_produto(self.prod), 5)
        # custo do produto atualizado
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.custo, Decimal("7.50"))
        # lançamento financeiro da compra
        lancs = LedgerEntry.objects.filter(descricao__startswith="Compra", credit_account="Fornecedores")
        self.assertTrue(lancs.exists())
        self.assertEqual(lancs.first().valor, Decimal("37.50"))
        # pagar
        url_pagar = reverse("compras-pagar", kwargs={"slug": order_slug})
        pay = self.client.post(url_pagar, {"valor": "20.00"}, format="json")
        self.assertEqual(pay.status_code, 200)
        lanc_pay = LedgerEntry.objects.filter(descricao__startswith="Pagamento Compra", debit_account="Fornecedores", credit_account="Caixa")
        self.assertTrue(lanc_pay.exists())
        self.assertEqual(lanc_pay.first().valor, Decimal("20.00"))
        # valor pago acumulado
        self.assertEqual(pay.data["valor_pago"], "20.00")

    def test_receber_compra_aplica_custo_medio(self):
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1100", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Fornecedores", defaults={"codigo": "2000", "tipo": Account.Tipo.PASSIVO})
        self.prod.custo = Decimal("5.00")
        self.prod.save(update_fields=["custo"])
        EstoqueService.registrar_entrada(self.prod, 10, origem_slug="seed")
        url = reverse("compras-list")
        payload = {
            "fornecedor": self.fornec.slug,
            "documento": "NF-999",
            "cost_center": self.cc.codigo,
            "itens_payload": [
                {"produto": self.prod.slug, "quantidade": 10, "custo_unitario": "7.00"}
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        order_slug = resp.data["slug"]
        url_receber = reverse("compras-receber", kwargs={"slug": order_slug})
        rcv = self.client.post(url_receber, {}, format="json")
        self.assertEqual(rcv.status_code, 200)
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.custo, Decimal("6.00"))

    def test_receber_compra_em_deposito_especifico(self):
        from estoque.models import Deposito
        dep = Deposito.objects.create(nome="CD")
        url = reverse("compras-list")
        payload = {
            "fornecedor": self.fornec.slug,
            "documento": "NF-DEP",
            "cost_center": self.cc.codigo,
            "deposito": dep.slug,
            "itens_payload": [
                {"produto": self.prod.slug, "quantidade": 3, "custo_unitario": "6.00"}
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        order_slug = resp.data["slug"]
        url_receber = reverse("compras-receber", kwargs={"slug": order_slug})
        rcv = self.client.post(url_receber, {}, format="json")
        self.assertEqual(rcv.status_code, 200)
        saldo_dep = EstoqueService.saldo_produto(self.prod, deposito=dep)
        self.assertEqual(saldo_dep, 3)

    def test_pagamento_nao_pode_exceder_total_e_quita_status(self):
        from compras.models import PurchaseOrder
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1000", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Fornecedores", defaults={"codigo": "2000", "tipo": Account.Tipo.PASSIVO})
        url = reverse("compras-list")
        payload = {
            "fornecedor": self.fornec.slug,
            "documento": "NF-PAY",
            "cost_center": self.cc.codigo,
            "itens_payload": [
                {"produto": self.prod.slug, "quantidade": 2, "custo_unitario": "10.00"}
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        order_slug = resp.data["slug"]
        # receber para permitir pagamento
        self.client.post(reverse("compras-receber", kwargs={"slug": order_slug}), {}, format="json")
        # pagar parcial
        pg = self.client.post(reverse("compras-pagar", kwargs={"slug": order_slug}), {"valor": "10.00"}, format="json")
        self.assertEqual(pg.status_code, 200)
        # tentar pagar acima do saldo
        over = self.client.post(reverse("compras-pagar", kwargs={"slug": order_slug}), {"valor": "20.00"}, format="json")
        self.assertEqual(over.status_code, 400)
        # pagar o restante e validar status quitado
        rest = self.client.post(reverse("compras-pagar", kwargs={"slug": order_slug}), {"valor": "10.00"}, format="json")
        self.assertEqual(rest.status_code, 200)
        self.assertEqual(rest.data["status"], PurchaseOrder.Status.QUITADO)

    def test_relatorio_csv_compras(self):
        url = reverse("compras-list")
        self.client.post(url, {"fornecedor": self.fornec.slug, "documento": "NF-CSV", "itens_payload": [{"produto": self.prod.slug, "quantidade": 1, "custo_unitario": "5.00"}]}, format="json")
        resp_csv = self.client.get(reverse("compras-csv"))
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv["Content-Type"], "text/csv")

    def test_cancelar_compra_sem_pagamento(self):
        from compras.models import PurchaseOrder
        url = reverse("compras-list")
        payload = {
            "fornecedor": self.fornec.slug,
            "documento": "NF-CAN",
            "cost_center": self.cc.codigo,
            "itens_payload": [
                {"produto": self.prod.slug, "quantidade": 4, "custo_unitario": "6.00"}
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        order_slug = resp.data["slug"]
        self.client.post(reverse("compras-receber", kwargs={"slug": order_slug}), {}, format="json")
        saldo_before = EstoqueService.saldo_produto(self.prod)
        cancel = self.client.post(reverse("compras-cancelar", kwargs={"slug": order_slug}), {}, format="json")
        self.assertEqual(cancel.status_code, 200)
        saldo_after = EstoqueService.saldo_produto(self.prod)
        self.assertEqual(saldo_after, saldo_before - 4)
        self.assertEqual(cancel.data["status"], PurchaseOrder.Status.CANCELADO)

    def test_saldo_por_fornecedor(self):
        url = reverse("compras-list")
        self.client.post(url, {"fornecedor": self.fornec.slug, "documento": "NF-A", "itens_payload": [{"produto": self.prod.slug, "quantidade": 2, "custo_unitario": "10.00"}]}, format="json")
        self.client.post(url, {"fornecedor": self.fornec.slug, "documento": "NF-B", "itens_payload": [{"produto": self.prod.slug, "quantidade": 1, "custo_unitario": "20.00"}]}, format="json")
        # receber ambas e pagar parcialmente primeira
        from compras.models import PurchaseOrder
        from django.db.models import Sum
        from rest_framework.reverse import reverse as drf_reverse
        orders = PurchaseOrder.objects.all()
        for o in orders:
            self.client.post(reverse("compras-receber", kwargs={"slug": o.slug}), {}, format="json")
        first = orders.first()
        self.client.post(reverse("compras-pagar", kwargs={"slug": first.slug}), {"valor": "10.00"}, format="json")
        resp = self.client.get(reverse("compras-saldo"))
        self.assertEqual(resp.status_code, 200)
        items = [i for i in resp.data if i["fornecedor"] == self.fornec.slug]
        self.assertTrue(items)

class VendasEstoqueIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cat = Categoria.objects.create(nome="Bebidas")
        self.prod = Produto.objects.create(nome="Suco", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        # entrada de estoque
        EstoqueService.registrar_entrada(self.prod, 5, origem_slug="seed")
        # contas necessárias
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1000", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "3000", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1100", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Custo das Vendas", defaults={"codigo": "4000", "tipo": Account.Tipo.DESPESA})
        self.user = get_user_model().objects.create_user(username="u1", password="p")
        # JWT
        url_token = reverse("token_obtain_pair")
        tok = self.client.post(url_token, {"username": "u1", "password": "p"}, format="json")
        self.assertEqual(tok.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok.data['access']}")

    def test_saida_no_estoque_ao_criar_pedido(self):
        saldo_before = EstoqueService.saldo_produto(self.prod)
        url_pedido = reverse("pedido-list")
        resp = self.client.post(url_pedido, {"itens_payload": [{"produto": self.prod.slug, "quantidade": 2}]}, format="json")
        self.assertEqual(resp.status_code, 201)
        # saldo após pedido
        saldo_after = EstoqueService.saldo_produto(self.prod)
        self.assertEqual(saldo_after, saldo_before - 2)
        # movimentos de estoque OUT vinculados ao pedido
        pedido_slug = resp.data["slug"]
        mvs = StockMovement.objects.filter(produto__slug=self.prod.slug, tipo=StockMovement.Tipo.OUT, origem_slug=pedido_slug)
        self.assertTrue(mvs.exists())
        self.assertEqual(mvs.first().quantidade, 2)
