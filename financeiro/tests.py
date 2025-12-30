from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from vendas.models import Categoria, Produto, Pedido, ItemPedido
from financeiro.services import FinanceiroService
from financeiro.models import LedgerEntry, Account, CostCenter
from cadastro.models import Supplier
from financeiro.models import Title
from financeiro.models import TitleParcel


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
        caixa, _ = Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        receita, _ = Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        estoque, _ = Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1.2.3", "tipo": Account.Tipo.ATIVO})
        cogs, _ = Account.objects.get_or_create(nome="Custo das Vendas", defaults={"codigo": "3.1.1", "tipo": Account.Tipo.DESPESA})
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

    def test_venda_a_prazo_e_recebimento(self):
        # contas necessárias
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.3.1", "tipo": Account.Tipo.ATIVO})
        # cria pedido a prazo
        url = reverse("pedido-list")
        from estoque.services import EstoqueService
        EstoqueService.registrar_entrada(self.l, 5, origem_slug="seed")
        payload = {"itens_payload": [{"produto": self.l.slug, "quantidade": 2}], "payment_type": "PRAZO"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        pedido_slug = resp.data["slug"]
        lancs = LedgerEntry.objects.filter(pedido__slug=pedido_slug, debit_account="Clientes", credit_account="Receita de Vendas")
        self.assertTrue(lancs.exists())
        # receber parte
        url_recv = reverse("financeiro-lancamento-receber-venda")
        recv = self.client.post(url_recv, {"pedido": pedido_slug, "valor": "10.00"}, format="json")
        self.assertEqual(recv.status_code, 200)
        cash = LedgerEntry.objects.filter(pedido__slug=pedido_slug, debit_account="Caixa", credit_account="Clientes")
        self.assertTrue(cash.exists())
        # saldo de caixa
        url_saldo = reverse("financeiro-lancamento-saldo-caixa")
        sal = self.client.get(url_saldo)
        self.assertEqual(sal.status_code, 200)
        url_ar = reverse("financeiro-lancamento-a-receber")
        lista = self.client.get(url_ar)
        self.assertEqual(lista.status_code, 200)
        self.assertTrue(any(i["pedido"] == pedido_slug for i in lista.data))
        url_ar_cli = reverse("financeiro-lancamento-a-receber-cliente")
        lista_cli = self.client.get(url_ar_cli)
        self.assertEqual(lista_cli.status_code, 200)
        etag = lista.headers.get('ETag')
        self.assertIsNotNone(etag)
        cached = self.client.get(url_ar, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(cached.status_code, 304)
        url_pos = reverse("financeiro-lancamento-posicao-pedido")
        pos = self.client.get(url_pos, {"pedido": pedido_slug})
        self.assertEqual(pos.status_code, 200)
        # idempotência no recebimento
        url_recv = reverse("financeiro-lancamento-receber-venda")
        idem_key = "key123"
        r1 = self.client.post(url_recv, {"pedido": pedido_slug, "valor": "5.00"}, format="json", HTTP_IDEMPOTENCY_KEY=idem_key)
        self.assertEqual(r1.status_code, 200)
        count_before = LedgerEntry.objects.filter(pedido__slug=pedido_slug, debit_account="Caixa", credit_account="Clientes").count()
        r2 = self.client.post(url_recv, {"pedido": pedido_slug, "valor": "5.00"}, format="json", HTTP_IDEMPOTENCY_KEY=idem_key)
        self.assertEqual(r2.status_code, 200)
        count_after = LedgerEntry.objects.filter(pedido__slug=pedido_slug, debit_account="Caixa", credit_account="Clientes").count()
        self.assertEqual(count_before, count_after)

    def test_aging_ar_e_livro_caixa(self):
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.3.1", "tipo": Account.Tipo.ATIVO})
        url = reverse("pedido-list")
        from estoque.services import EstoqueService
        EstoqueService.registrar_entrada(self.l, 10, origem_slug="seed")
        p1 = self.client.post(url, {"itens_payload": [{"produto": self.l.slug, "quantidade": 2}], "payment_type": "PRAZO"}, format="json").data["slug"]
        p2 = self.client.post(url, {"itens_payload": [{"produto": self.l.slug, "quantidade": 1}], "payment_type": "PRAZO"}, format="json").data["slug"]
        from financeiro.models import LedgerEntry
        import datetime
        from django.utils import timezone
        now = timezone.now()
        le1 = LedgerEntry.objects.filter(pedido__slug=p1, debit_account="Clientes").first()
        le2 = LedgerEntry.objects.filter(pedido__slug=p2, debit_account="Clientes").first()
        le1.criado_em = now - datetime.timedelta(days=10)
        le1.save(update_fields=["criado_em"])
        le2.criado_em = now - datetime.timedelta(days=45)
        le2.save(update_fields=["criado_em"])
        url_aging = reverse("financeiro-lancamento-a-receber-aging")
        ag = self.client.get(url_aging, {"end": now.isoformat()})
        self.assertEqual(ag.status_code, 200)
        buckets = [i["bucket"] for i in ag.data]
        self.assertIn("0-30", buckets)
        self.assertIn("31-60", buckets)
        url_aging_csv = reverse("financeiro-lancamento-a-receber-aging-csv")
        self.assertEqual(self.client.get(url_aging_csv, {"end": now.isoformat()}).status_code, 200)
        url_lc = reverse("financeiro-lancamento-livro-caixa")
        lc = self.client.get(url_lc)
        self.assertEqual(lc.status_code, 200)
        url_lc_csv = reverse("financeiro-lancamento-livro-caixa-csv")
        self.assertEqual(self.client.get(url_lc_csv).status_code, 200)
        url_cli = reverse("financeiro-lancamento-cliente-posicao")
        cli = self.client.get(url_cli, {"end": now.isoformat()})
        self.assertEqual(cli.status_code, 200)
        url_cli_csv = reverse("financeiro-lancamento-cliente-posicao-csv")
        first = self.client.get(url_cli_csv, {"end": now.isoformat()})
        self.assertEqual(first.status_code, 200)
        etag = first.headers.get('ETag')
        second = self.client.get(url_cli_csv, {"end": now.isoformat()}, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(second.status_code, 304)

    def test_titulos_ap_ar_fluxo(self):
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.3.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Fornecedores", defaults={"codigo": "2.1.1", "tipo": Account.Tipo.PASSIVO})
        from estoque.services import EstoqueService
        EstoqueService.registrar_entrada(self.l, 10, origem_slug="seed")
        url_ped = reverse("pedido-list")
        ped_slug = self.client.post(url_ped, {"itens_payload": [{"produto": self.l.slug, "quantidade": 2}], "payment_type": "PRAZO"}, format="json").data["slug"]
        import datetime
        due = datetime.date.today() + datetime.timedelta(days=30)
        url_titles = reverse("financeiro-titulo-list")
        t_ar = self.client.post(url_titles, {"tipo": "AR", "pedido": ped_slug, "valor": "30.00", "due_date": due.isoformat()}, format="json")
        self.assertEqual(t_ar.status_code, 201)
        ridx = reverse("financeiro-titulo-receber", kwargs={"pk": t_ar.data["id"]})
        rec = self.client.post(ridx, {"valor": "10.00"}, format="json")
        self.assertEqual(rec.status_code, 200)
        self.assertEqual(Title.objects.get(id=t_ar.data["id"]).valor_pago, Decimal("10.00"))
        forn = Supplier.objects.create(nome="ABC Forn")
        from compras.models import PurchaseOrder, PurchaseItem
        po = PurchaseOrder.objects.create(fornecedor=forn, documento="NF1", responsavel=self.user)
        PurchaseItem.objects.create(order=po, produto=self.l, quantidade=1, custo_unitario=Decimal("5.00"))
        po.total = Decimal("5.00")
        po.save(update_fields=["total"])
        t_ap = self.client.post(url_titles, {"tipo": "AP", "compra": po.slug, "valor": "5.00", "due_date": due.isoformat()}, format="json")
        self.assertEqual(t_ap.status_code, 201)
        pidx = reverse("financeiro-titulo-pagar", kwargs={"pk": t_ap.data["id"]})
        pag = self.client.post(pidx, {"valor": "2.00"}, format="json")
        self.assertEqual(pag.status_code, 200)
        self.assertEqual(Title.objects.get(id=t_ap.data["id"]).valor_pago, Decimal("2.00"))
        pser = self.client.post(reverse("financeiro-titulo-add-parcela"), {"title": t_ar.data["id"], "valor": "20.00", "due_date": due.isoformat()}, format="json")
        self.assertEqual(pser.status_code, 201)
        pid = pser.data["id"]
        rpp = self.client.post(reverse("financeiro-titulo-receber-parcela", kwargs={"pk": t_ar.data["id"]}), {"parcela": pid, "valor": "10.00"}, format="json")
        self.assertEqual(rpp.status_code, 200)
        self.assertEqual(TitleParcel.objects.get(id=pid).valor_pago, Decimal("10.00"))
        url_due = reverse("financeiro-lancamento-a-receber-aging-due")
        self.assertEqual(self.client.get(url_due, {"end": due.isoformat()}).status_code, 200)
        url_due_csv = reverse("financeiro-lancamento-a-receber-aging-due-csv")
        self.assertEqual(self.client.get(url_due_csv, {"end": due.isoformat()}).status_code, 200)
        url_titles_csv = reverse("financeiro-titulo-csv")
        self.assertEqual(self.client.get(url_titles_csv, {"tipo": "AR", "ordering": "due_date"}).status_code, 200)
        first = self.client.get(url_titles_csv, {"tipo": "AR"})
        etag = first.headers.get('ETag')
        second = self.client.get(url_titles_csv, {"tipo": "AR"}, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(second.status_code, 304)

    def test_venda_a_prazo_parcelas(self):
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.3.1", "tipo": Account.Tipo.ATIVO})
        from estoque.services import EstoqueService
        EstoqueService.registrar_entrada(self.l, 10, origem_slug="seed")
        url_ped = reverse("pedido-list")
        import datetime
        d1 = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        d2 = (datetime.date.today() + datetime.timedelta(days=40)).isoformat()
        resp = self.client.post(url_ped, {"itens_payload": [{"produto": self.l.slug, "quantidade": 2}], "payment_type": "PRAZO", "parcelas": [{"valor": "10.00", "due_date": d1}, {"valor": "20.00", "due_date": d2}]}, format="json")
        self.assertEqual(resp.status_code, 201)
        from financeiro.models import Title
        t = Title.objects.filter(pedido__slug=resp.data["slug"]).first()
        self.assertIsNotNone(t)
        self.assertEqual(t.valor, Decimal("30.00"))
        from financeiro.models import TitleParcel
        self.assertEqual(TitleParcel.objects.filter(title=t).count(), 2)
        url_titles = reverse("financeiro-titulo-list")
        lst = self.client.get(url_titles, {"ordering": "due_date"})
        self.assertEqual(lst.status_code, 200)
        import datetime
        dates = [i["due_date"] for i in lst.data["results"]] if "results" in lst.data else [i["due_date"] for i in lst.data]
        if dates:
            parsed = [datetime.date.fromisoformat(d) for d in dates if d]
            self.assertEqual(parsed, sorted(parsed))
        pid = TitleParcel.objects.filter(title=t).first().id
        upd = self.client.post(reverse("financeiro-titulo-update-parcela", kwargs={"pk": t.id}), {"parcela": pid, "valor": "15.00"}, format="json")
        self.assertEqual(upd.status_code, 200)
        from financeiro.models import Title
        self.assertEqual(Title.objects.get(id=t.id).valor, Decimal("35.00"))
        rem = self.client.post(reverse("financeiro-titulo-remove-parcela", kwargs={"pk": t.id}), {"parcela": pid}, format="json")
        self.assertEqual(rem.status_code, 200)
        url_due_csv = reverse("financeiro-lancamento-a-receber-aging-due-csv")
        first = self.client.get(url_due_csv, {"end": d2})
        etag = first.headers.get('ETag')
        second = self.client.get(url_due_csv, {"end": d2}, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(second.status_code, 304)

    def test_venda_a_prazo_parcelas_inconsistentes(self):
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.3.1", "tipo": Account.Tipo.ATIVO})
        from estoque.services import EstoqueService
        EstoqueService.registrar_entrada(self.l, 10, origem_slug="seed")
        url_ped = reverse("pedido-list")
        import datetime
        d1 = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        d2 = (datetime.date.today() + datetime.timedelta(days=40)).isoformat()
        resp = self.client.post(url_ped, {"itens_payload": [{"produto": self.l.slug, "quantidade": 2}], "payment_type": "PRAZO", "parcelas": [{"valor": "10.00", "due_date": d1}, {"valor": "10.00", "due_date": d2}]}, format="json")
        self.assertEqual(resp.status_code, 400)

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
