from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Categoria, Produto


class CatalogoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(username="admin", password="p", is_staff=True)
        self.client.force_authenticate(self.admin)
        self.cat = Categoria.objects.create(nome="Bebidas")

    def test_criar_categoria_e_produto(self):
        r_cat = self.client.post(reverse("catalogo-categoria-list"), {"nome": "Burgers"}, format="json")
        self.assertEqual(r_cat.status_code, 201)
        slug_cat = r_cat.data["slug"]
        r_prod = self.client.post(reverse("catalogo-produto-list"), {"nome": "X-Burger", "categoria": slug_cat, "preco": "25.00", "disponivel": True}, format="json")
        self.assertEqual(r_prod.status_code, 201)
        self.assertTrue(r_prod.data.get("slug"))
        self.assertTrue(r_prod.data.get("sku"))

    def test_listar_filtrar_e_detalhar(self):
        p1 = Produto.objects.create(nome="Suco", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        p2 = Produto.objects.create(nome="Água", categoria=self.cat, preco=Decimal("5.00"), disponivel=True)
        url = reverse("catalogo-produto-list")
        r = self.client.get(url, {"categoria": self.cat.slug, "ordering": "preco"})
        self.assertEqual(r.status_code, 200)
        precos = [Decimal(i["preco"]) for i in r.data]
        self.assertListEqual(precos, [Decimal("5.00"), Decimal("10.00")])
        d = self.client.get(reverse("catalogo-produto-detail", kwargs={"slug": p1.slug}))
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.data["slug"], p1.slug)

    def test_categoria_action_produtos(self):
        Produto.objects.create(nome="Suco Uva", categoria=self.cat, preco=Decimal("10.00"), disponivel=True)
        Produto.objects.create(nome="Suco Caixa", categoria=self.cat, preco=Decimal("20.00"), disponivel=False)
        url = reverse("catalogo-categoria-produtos", kwargs={"slug": self.cat.slug})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        nomes = [i["nome"] for i in r.data]
        self.assertListEqual(sorted(nomes), ["Suco Uva"])

    def test_atributos_valores_variacoes(self):
        p = Produto.objects.create(nome="Refri", categoria=self.cat, preco=Decimal("7.00"), disponivel=True)
        url_attr = reverse("catalogo-produto-atributo-list")
        r_attr = self.client.post(url_attr, {"codigo": "COR", "nome": "Cor", "tipo": "TEXT"}, format="json")
        self.assertEqual(r_attr.status_code, 201)
        url_val = reverse("catalogo-produto-atributo-valor-list")
        r_val = self.client.post(url_val, {"produto": p.slug, "atributo": "COR", "valor_texto": "Cola"}, format="json")
        self.assertEqual(r_val.status_code, 201)
        url_var = reverse("catalogo-produto-variacao-list")
        r_var = self.client.post(url_var, {"produto": p.slug, "sku": "refri-cola-1l", "nome": "Refri Cola 1L", "preco": "8.00", "custo": "5.00", "disponivel": True}, format="json")
        self.assertEqual(r_var.status_code, 201)
        r_list = self.client.get(url_var, {"produto": p.slug})
        self.assertEqual(r_list.status_code, 200)
        self.assertTrue(len(r_list.data) >= 1)
