from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Categoria, Produto, Pedido, ItemPedido
from .services import PedidoService
from financeiro.models import LedgerEntry, Account, CostCenter
from estoque.services import EstoqueService


class PedidoServiceTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nome="Burgers")
        self.l1 = Produto.objects.create(nome="X-Burger", categoria=self.cat, preco=Decimal("25.90"), disponivel=True)
        self.l2 = Produto.objects.create(nome="X-Salada", categoria=self.cat, preco=Decimal("29.50"), disponivel=True)
        self.user = get_user_model().objects.create_user(username="u1", password="pass123")
        self.pedido = Pedido.objects.create(usuario=self.user)

    def test_calcular_total(self):
        i1 = ItemPedido.objects.create(pedido=self.pedido, produto=self.l1, quantidade=2, preco_unitario=self.l1.preco)
        i2 = ItemPedido.objects.create(pedido=self.pedido, produto=self.l2, quantidade=1, preco_unitario=self.l2.preco)
        total = PedidoService.calcular_total([i1, i2])
        self.assertEqual(total, Decimal("81.30"))  # 2*25.90 + 1*29.50

    def test_validate_disponibilidade_raises_when_unavailable(self):
        self.l2.disponivel = False
        self.l2.save(update_fields=["disponivel"])
        payload = [{"produto": self.l1.slug, "quantidade": 1}, {"produto": self.l2.slug, "quantidade": 1}]
        with self.assertRaises(Exception):
            PedidoService.validate_disponibilidade(payload)

    def test_criar_itens_captura_preco_atual(self):
        itens = PedidoService.criar_itens(self.pedido, [{"produto": self.l1.slug, "quantidade": 3}])
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0].preco_unitario, self.l1.preco)


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cat = Categoria.objects.create(nome="Bebidas")
        self.l_suco = Produto.objects.create(nome="Suco Laranja", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        self.l_refri = Produto.objects.create(nome="Refrigerante", categoria=self.cat, preco=Decimal("8.50"), disponivel=True)
        self.user = get_user_model().objects.create_user(username="user1", password="pass123")
        self.user2 = get_user_model().objects.create_user(username="user2", password="pass123")
        EstoqueService.registrar_entrada(self.l_suco, 10, origem_slug="test")
        EstoqueService.registrar_entrada(self.l_refri, 10, origem_slug="test")

    def auth(self, username="user1", password="pass123"):
        url = reverse("token_obtain_pair")
        resp = self.client.post(url, {"username": username, "password": password}, format="json")
        self.assertEqual(resp.status_code, 200)
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_criacao_pedido_fluxo_completo(self):
        self.auth()
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1.2.3", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Custo das Vendas", defaults={"codigo": "3.1.1", "tipo": Account.Tipo.DESPESA})
        CostCenter.objects.create(nome="Loja 1", codigo="LJ1")
        url = reverse("pedido-list")
        payload = {
            "itens_payload": [
                {"produto": self.l_suco.slug, "quantidade": 2},
                {"produto": self.l_refri.slug, "quantidade": 1},
            ],
            "cost_center": "LJ1"
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        pedido_slug = resp.data["slug"]
        self.assertTrue(pedido_slug)
        # Verifica total
        self.assertEqual(resp.data["total"], "28.50")  # 2*10.00 + 1*8.50
        # Recupera detalhe
        detail = self.client.get(reverse("pedido-detail", kwargs={"slug": pedido_slug}))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(len(detail.data["itens"]), 2)
        slugs = {i["produto_slug"] for i in detail.data["itens"]}
        self.assertSetEqual(slugs, {self.l_suco.slug, self.l_refri.slug})
        lancs = LedgerEntry.objects.filter(pedido__slug=pedido_slug)
        self.assertTrue(lancs.exists())
        self.assertTrue(all(le.cost_center and le.cost_center.codigo == "LJ1" for le in lancs))

    def test_pedido_usa_cost_center_padrao(self):
        self.auth()
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1.2.3", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Custo das Vendas", defaults={"codigo": "3.1.1", "tipo": Account.Tipo.DESPESA})
        centro = CostCenter.objects.create(nome="Loja 2", codigo="LJ2")
        from financeiro.models import UserDefaultCostCenter
        UserDefaultCostCenter.objects.create(user=self.user, cost_center=centro)
        url = reverse("pedido-list")
        payload = {
            "itens_payload": [
                {"produto": self.l_suco.slug, "quantidade": 1},
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        detail = self.client.get(resp.data["url"] if "url" in resp.data else reverse("pedido-detail", kwargs={"slug": resp.data["slug"]}))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["cost_center_codigo"], "LJ2")

    def test_listagem_restrita_por_usuario(self):
        # user1 cria pedido
        self.auth("user1")
        self.client.post(reverse("pedido-list"), {"itens_payload": [{"produto": self.l_suco.slug, "quantidade": 1}]}, format="json")
        # user2 cria pedido
        self.client.credentials()
        self.auth("user2")
        self.client.post(reverse("pedido-list"), {"itens_payload": [{"produto": self.l_refri.slug, "quantidade": 1}]}, format="json")
        # user2 lista apenas seus pedidos
        resp = self.client.get(reverse("pedido-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_proibe_itens_duplicados(self):
        self.auth()
        resp = self.client.post(
            reverse("pedido-list"),
            {"itens_payload": [{"produto": self.l_suco.slug, "quantidade": 1}, {"produto": self.l_suco.slug, "quantidade": 2}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_criacao_pedido_com_chave_produto(self):
        self.auth()
        url = reverse("pedido-list")
        payload = {
            "itens_payload": [
                {"produto": self.l_suco.slug, "quantidade": 1},
                {"produto": self.l_refri.slug, "quantidade": 3},
            ]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        total = resp.data["total"]
        self.assertEqual(total, "35.50")


class ProdutoFilterOrderingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cat_bebidas = Categoria.objects.create(nome="Bebidas")
        self.cat_burgers = Categoria.objects.create(nome="Burgers")
        self.a = Produto.objects.create(nome="Água", categoria=self.cat_bebidas, preco=Decimal("5.00"), disponivel=True)
        self.b = Produto.objects.create(nome="Suco", categoria=self.cat_bebidas, preco=Decimal("8.00"), disponivel=True)
        self.c = Produto.objects.create(nome="X-Burger", categoria=self.cat_burgers, preco=Decimal("25.00"), disponivel=True)
        self.d = Produto.objects.create(nome="X-Salada", categoria=self.cat_burgers, preco=Decimal("22.00"), disponivel=False)

    def test_filtra_por_categoria_slug(self):
        url = reverse("catalogo-produto-list")
        resp = self.client.get(url, {"categoria": self.cat_bebidas.slug})
        self.assertEqual(resp.status_code, 200)
        nomes = [i["nome"] for i in resp.data]
        self.assertListEqual(sorted(nomes), ["Suco", "Água"])

    def test_filtra_por_texto(self):
        url = reverse("catalogo-produto-list")
        resp = self.client.get(url, {"q": "burger"})
        self.assertEqual(resp.status_code, 200)
        nomes = [i["nome"] for i in resp.data]
        self.assertListEqual(nomes, ["X-Burger"])

    def test_ordena_por_preco_asc_desc(self):
        url = reverse("catalogo-produto-list")
        resp_asc = self.client.get(url, {"categoria": self.cat_bebidas.slug, "ordering": "preco"})
        self.assertEqual(resp_asc.status_code, 200)
        precos_asc = [Decimal(i["preco"]) for i in resp_asc.data]
        self.assertListEqual(precos_asc, [Decimal("5.00"), Decimal("8.00")])

        resp_desc = self.client.get(url, {"categoria": self.cat_bebidas.slug, "ordering": "-preco"})
        self.assertEqual(resp_desc.status_code, 200)
        precos_desc = [Decimal(i["preco"]) for i in resp_desc.data]
        self.assertListEqual(precos_desc, [Decimal("8.00"), Decimal("5.00")])

    def test_categoria_action_produtos_retorna_disponiveis(self):
        url = reverse("catalogo-categoria-produtos", kwargs={"slug": self.cat_burgers.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        nomes = [i["nome"] for i in resp.data]
        self.assertListEqual(nomes, ["X-Burger"])

    def test_alias_produtos_lista_e_detalhe(self):
        # Lista via alias
        url = reverse("catalogo-produto-list")
        resp = self.client.get(url, {"categoria": self.cat_bebidas.slug})
        self.assertEqual(resp.status_code, 200)
        nomes = [i["nome"] for i in resp.data]
        self.assertListEqual(sorted(nomes), ["Suco", "Água"])
        # Detalhe via alias
        detail = self.client.get(reverse("catalogo-produto-detail", kwargs={"slug": self.a.slug}))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["slug"], self.a.slug)


class ProdutoCreateValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(username="admin", password="p", is_staff=True)
        self.client.force_authenticate(self.admin)
        self.cat = Categoria.objects.create(nome="Bebidas")

    def test_criar_produto_admin(self):
        url = reverse("catalogo-produto-list")
        payload = {
            "nome": "Suco de Uva",
            "categoria": self.cat.slug,
            "preco": "9.90",
            "custo": "6.00",
            "descricao": "Garrafa 1L",
            "disponivel": True,
            "ean": "7891234567890",
            "ncm": "20098900",
            "cfop": "5102",
            "unidade": "UN",
            "marca": "Acme"
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data.get("slug"))
        self.assertTrue(resp.data.get("sku"))
        self.assertEqual(resp.data.get("ean"), "7891234567890")
        self.assertEqual(resp.data.get("unidade"), "UN")
        self.assertEqual(resp.data.get("marca"), "Acme")
        self.assertEqual(resp.data.get("ncm"), "20098900")
        self.assertEqual(resp.data.get("cfop"), "5102")

    def test_valida_ean_invalido(self):
        url = reverse("catalogo-produto-list")
        payload = {"nome": "Água", "categoria": self.cat.slug, "preco": "5.00", "custo": "3.00", "ean": "X123"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_valida_preco_negativo(self):
        url = reverse("produto-list")
        payload = {"nome": "Água", "categoria": self.cat.slug, "preco": "-1.00", "custo": "3.00"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_busca_por_q_em_sku_e_ean(self):
        # cria dois produtos com sku e ean definidos
        p1 = Produto.objects.create(nome="Refri Cola", categoria=self.cat, preco=Decimal("7.00"), disponivel=True, sku="cola-001", ean="7890000000001")
        p2 = Produto.objects.create(nome="Refri Limo", categoria=self.cat, preco=Decimal("7.50"), disponivel=True, sku="limo-001", ean="7890000000002")
        url = reverse("produto-list")
        r_sku = self.client.get(url, {"q": "cola-001"})
        self.assertEqual(r_sku.status_code, 200)
        slugs_sku = [i["slug"] for i in r_sku.data]
        self.assertIn(p1.slug, slugs_sku)
        r_ean = self.client.get(url, {"q": "7890000000002"})
        self.assertEqual(r_ean.status_code, 200)
        slugs_ean = [i["slug"] for i in r_ean.data]
        self.assertIn(p2.slug, slugs_ean)

    def test_filtros_avancados_por_marca_unidade_preco(self):
        Produto.objects.create(nome="Suco Uva", categoria=self.cat, preco=Decimal("10.00"), disponivel=True, marca="Acme", unidade="UN")
        Produto.objects.create(nome="Suco Caixa", categoria=self.cat, preco=Decimal("20.00"), disponivel=True, marca="Beta", unidade="CX")
        url = reverse("produto-list")
        r_marca = self.client.get(url, {"marca": "acm"})
        self.assertEqual(r_marca.status_code, 200)
        nomes_marca = [i["nome"] for i in r_marca.data]
        self.assertIn("Suco Uva", nomes_marca)
        r_un = self.client.get(url, {"unidade": "CX"})
        nomes_un = [i["nome"] for i in r_un.data]
        self.assertIn("Suco Caixa", nomes_un)
        r_preco = self.client.get(url, {"preco_min": "15", "preco_max": "25"})
        precos = [Decimal(i["preco"]) for i in r_preco.data]
        self.assertTrue(all(Decimal("15") <= p <= Decimal("25") for p in precos))

    def test_produto_imagens_crud_admin(self):
        p = Produto.objects.create(nome="Agua", categoria=self.cat, preco=Decimal("5.00"), disponivel=True)
        url = reverse("catalogo-produto-imagem-list")
        from django.core.files.uploadedfile import SimpleUploadedFile
        img = SimpleUploadedFile("f.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00IHDR", content_type="image/png")
        resp = self.client.post(url, {"produto": p.slug, "imagem": img, "alt": "Foto", "pos": 1}, format="multipart")
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get(url, {"produto": p.slug})
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(len(list_resp.data) >= 1)

    def test_catalogo_atributos_e_variacoes(self):
        # cria atributo e valor
        url_attr = reverse("catalogo-produto-atributo-list")
        resp_attr = self.client.post(url_attr, {"codigo": "COR", "nome": "Cor", "tipo": "TEXT"}, format="json")
        self.assertEqual(resp_attr.status_code, 201)
        attr_codigo = resp_attr.data["codigo"]
        p = Produto.objects.create(nome="Refri", categoria=self.cat, preco=Decimal("7.00"), disponivel=True)
        url_val = reverse("catalogo-produto-atributo-valor-list")
        resp_val = self.client.post(url_val, {"produto": p.slug, "atributo": attr_codigo, "valor_texto": "Cola"}, format="json")
        self.assertEqual(resp_val.status_code, 201)
        # cria variação
        url_var = reverse("catalogo-produto-variacao-list")
        resp_var = self.client.post(url_var, {"produto": p.slug, "sku": "refri-cola-1l", "nome": "Refri Cola 1L", "preco": "8.00", "custo": "5.00", "disponivel": True}, format="json")
        self.assertEqual(resp_var.status_code, 201)
        list_var = self.client.get(url_var, {"produto": p.slug})
        self.assertEqual(list_var.status_code, 200)
        self.assertTrue(len(list_var.data) >= 1)
