from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from financeiro.models import CostCenter, UserDefaultCostCenter
from financeiro.services import FinanceiroService
from vendas.models import Categoria, Produto, Pedido, ItemPedido
from decimal import Decimal


class Command(BaseCommand):
    help = "Cria dados de demonstração: grupos, usuários, centros, categorias, produtos e pedidos"

    def handle(self, *args, **options):
        for name in ["operacao", "estoque", "financeiro"]:
            Group.objects.get_or_create(name=name)
        call_command("seed_accounts")
        cc1, _ = CostCenter.objects.get_or_create(codigo="LJ1", defaults={"nome": "Loja 1"})
        cc3, _ = CostCenter.objects.get_or_create(codigo="LJ3", defaults={"nome": "Loja 3"})
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True})
        if not admin.has_usable_password():
            admin.set_password("p")
            admin.save(update_fields=["password"])
        su, _ = User.objects.get_or_create(username="super", defaults={"is_staff": True, "is_superuser": True})
        if not su.has_usable_password():
            su.set_password("p")
            su.save(update_fields=["password"])
        user, _ = User.objects.get_or_create(username="user")
        if not user.has_usable_password():
            user.set_password("p")
            user.save(update_fields=["password"])
        UserDefaultCostCenter.objects.get_or_create(user=admin, cost_center=cc1)
        cat_b, _ = Categoria.objects.get_or_create(nome="Bebidas")
        cat_l, _ = Categoria.objects.get_or_create(nome="Sanduíches")
        suco, _ = Produto.objects.get_or_create(nome="Suco", categoria=cat_b, defaults={"preco": Decimal("8.00"), "disponivel": True})
        agua, _ = Produto.objects.get_or_create(nome="Água", categoria=cat_b, defaults={"preco": Decimal("5.00"), "disponivel": True})
        burger, _ = Produto.objects.get_or_create(nome="X-Burger", categoria=cat_l, defaults={"preco": Decimal("25.00"), "disponivel": True, "custo": Decimal("10.00")})
        p1, _ = Pedido.objects.get_or_create(usuario=user, defaults={})
        if p1.itens.count() == 0:
            ItemPedido.objects.create(pedido=p1, produto=suco, quantidade=2, preco_unitario=suco.preco)
            ItemPedido.objects.create(pedido=p1, produto=agua, quantidade=1, preco_unitario=agua.preco)
            p1.total = Decimal("21.00")
            p1.cost_center = cc1
            p1.save(update_fields=["total", "cost_center"])
            FinanceiroService.registrar_receita_venda(p1, cost_center_code=cc1.codigo)
        p2, _ = Pedido.objects.get_or_create(usuario=user, defaults={})
        if p2.itens.count() == 0:
            ItemPedido.objects.create(pedido=p2, produto=burger, quantidade=2, preco_unitario=burger.preco)
            p2.total = Decimal("50.00")
            p2.cost_center = cc1
            p2.save(update_fields=["total", "cost_center"])
            FinanceiroService.registrar_receita_venda(p2, cost_center_code=cc1.codigo)
            FinanceiroService.registrar_custo_venda(p2, cost_center_code=cc1.codigo)
        self.stdout.write("Seed de demonstração concluído")
