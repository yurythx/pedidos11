from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import json
from django.conf import settings


class Command(BaseCommand):
    help = "Executa chamadas de API internas para validar o fluxo de produto end-to-end"

    def handle(self, *args, **options):
        if isinstance(getattr(settings, "ALLOWED_HOSTS", []), list) and "testserver" not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append("testserver")
        call_command("seed_demo")
        call_command("seed_defaults")
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True})
        if not admin.has_usable_password():
            admin.set_password("p")
            admin.save(update_fields=["password"])
        client = APIClient()
        client.force_authenticate(user=admin)
        self.stdout.write("AUTH: force_authenticate admin")
        produtos = client.get("/api/v1/vendas/produtos/")
        self.stdout.write(f"PRODUTOS_STATUS {produtos.status_code}")
        try:
            data_prods = produtos.data
        except Exception:
            data_prods = json.loads(produtos.content.decode())
        self.stdout.write(f"PRODUTOS_COUNT {len(data_prods)}")
        slug = data_prods[0]["slug"] if data_prods else None
        self.stdout.write(f"PRODUTO_ESCOLHIDO {slug}")
        # defaults criados por seed_defaults
        forn_slug_default = "fornecedor-x"
        dep_slug_default = "deposito-central"
        dep2_slug_default = "loja-1"
        if slug:
            entrada = client.post("/api/v1/estoque/movimentos/entrada/", {"produto": slug, "quantidade": 5, "deposito": dep_slug_default}, format="json")
            self.stdout.write(f"ENTRADA_STATUS {entrada.status_code}")
            try:
                entrada_data = entrada.data
            except Exception:
                entrada_data = json.loads(entrada.content.decode())
            self.stdout.write(f"ENTRADA {json.dumps(entrada_data)}")
            fornecedor_payload = {"nome": "Fornecedor X", "enderecos_payload": [{"logradouro": "Rua A", "cidade": "Rondonópolis"}]}
            fornecedor = client.post("/api/v1/cadastro/fornecedores/", fornecedor_payload, format="json")
            forn_slug = forn_slug_default
            try:
                data_forn = fornecedor.data if hasattr(fornecedor, "data") else json.loads(fornecedor.content.decode())
                if fornecedor.status_code in (200, 201) and isinstance(data_forn, dict) and data_forn.get("slug"):
                    forn_slug = data_forn.get("slug")
            except Exception:
                pass
            recibo_payload = {"fornecedor": forn_slug, "documento": "NF-123", "itens_payload": [{"produto": slug, "quantidade": 3}]}
            recibo = client.post("/api/v1/estoque/recebimentos/", recibo_payload, format="json")
            self.stdout.write(f"RECEBIMENTO_STATUS {recibo.status_code}")
            try:
                recibo_data = recibo.data
            except Exception:
                recibo_data = json.loads(recibo.content.decode())
            self.stdout.write(f"RECEBIMENTO {json.dumps(recibo_data)}")
            saldo_dep = client.get(f"/api/v1/estoque/movimentos/saldo/?produto={slug}&deposito={dep_slug_default}")
            self.stdout.write(f"SALDO_DEPOSITO_STATUS {saldo_dep.status_code}")
            self.stdout.write(f"SALDO_DEPOSITO {saldo_dep.content.decode()}")
            # transferir 2 unidades para um deposito destino
            transfer = client.post("/api/v1/estoque/movimentos/transferir/", {"produto": slug, "quantidade": 2, "origem": dep_slug_default, "destino": dep2_slug_default}, format="json")
            self.stdout.write(f"TRANSFER_STATUS {transfer.status_code}")
            self.stdout.write(f"TRANSFER {transfer.content.decode()}")
        ped_payload = {"itens_payload": [{"produto": slug, "quantidade": 2}], "cost_center": "LJ1"} if slug else {"itens_payload": [], "cost_center": "LJ1"}
        pedido = client.post("/api/v1/vendas/pedidos/", ped_payload, format="json")
        self.stdout.write(f"PEDIDO_STATUS {pedido.status_code}")
        try:
            pedido_data = pedido.data
        except Exception:
            pedido_data = json.loads(pedido.content.decode())
        self.stdout.write(f"PEDIDO {json.dumps(pedido_data)}")
        slug_ped = pedido_data.get("slug")
        if slug_ped:
            detalhe = client.get(f"/api/v1/vendas/pedidos/{slug_ped}/")
            self.stdout.write(f"DETALHE_STATUS {detalhe.status_code}")
            try:
                detalhe_data = detalhe.data
            except Exception:
                detalhe_data = json.loads(detalhe.content.decode())
            self.stdout.write(f"DETALHE_TOTAL {detalhe_data.get('total')}")
            self.stdout.write(f"DETALHE_ITENS {json.dumps(detalhe_data.get('itens'))}")
        resumo = client.get("/api/v1/financeiro/lancamentos/resumo/?cost_center=LJ1")
        self.stdout.write(f"FIN_STATUS {resumo.status_code}")
        try:
            resumo_data = resumo.data
        except Exception:
            resumo_data = json.loads(resumo.content.decode())
        self.stdout.write(f"FIN_RESUMO {json.dumps(resumo_data)}")
        rel_fat = client.get("/api/v1/relatorios/faturamento/?cost_center=LJ1")
        self.stdout.write(f"REL_FAT_STATUS {rel_fat.status_code}")
        if rel_fat.status_code == 200:
            try:
                fat_data = rel_fat.data
            except Exception:
                fat_data = json.loads(rel_fat.content.decode())
            self.stdout.write(f"REL_FAT {json.dumps(fat_data)}")
        rel_itens = client.get("/api/v1/relatorios/itens/?limit=5&cost_center=LJ1")
        self.stdout.write(f"REL_ITENS_STATUS {rel_itens.status_code}")
        if rel_itens.status_code == 200:
            try:
                rel_data = rel_itens.data
            except Exception:
                rel_data = json.loads(rel_itens.content.decode())
            self.stdout.write(f"REL_ITENS {json.dumps(rel_data)}")
        else:
            self.stdout.write("REL_ITENS skipped due to non-200")
        rel_cat = client.get("/api/v1/relatorios/categorias/?cost_center=LJ1")
        self.stdout.write(f"REL_CAT_STATUS {rel_cat.status_code}")
        if rel_cat.status_code == 200:
            try:
                cat_data = rel_cat.data
            except Exception:
                cat_data = json.loads(rel_cat.content.decode())
            self.stdout.write(f"REL_CAT {json.dumps(cat_data)}")
