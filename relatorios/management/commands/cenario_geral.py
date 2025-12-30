import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cadastro.models import Address, Supplier, Customer
from vendas.models import Categoria, Produto, Pedido, ItemPedido
from compras.models import PurchaseOrder, PurchaseItem
from estoque.models import Deposito, StockReceipt, StockReceiptItem
from estoque.services import EstoqueService
from financeiro.models import Account, CostCenter, LedgerEntry
from financeiro.services import FinanceiroService


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        usuario, _ = User.objects.get_or_create(username="cenario_user", defaults={"password": "p", "is_staff": True})
        Account.objects.get_or_create(nome="Caixa", defaults={"codigo": "1.1.1", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Receita de Vendas", defaults={"codigo": "4.1.1", "tipo": Account.Tipo.RECEITA})
        Account.objects.get_or_create(nome="Estoque", defaults={"codigo": "1.2.3", "tipo": Account.Tipo.ATIVO})
        Account.objects.get_or_create(nome="Custo das Vendas", defaults={"codigo": "3.1.1", "tipo": Account.Tipo.DESPESA})
        Account.objects.get_or_create(nome="Fornecedores", defaults={"codigo": "2.1.1", "tipo": Account.Tipo.PASSIVO})
        Account.objects.get_or_create(nome="Clientes", defaults={"codigo": "1.1.2", "tipo": Account.Tipo.ATIVO})
        cc, _ = CostCenter.objects.get_or_create(nome="Loja 1", codigo="LJ1")
        dep_end = Address.objects.create(logradouro="Av Central", numero="1000", cidade="São Paulo", estado="SP", cep="01000000")
        deposito, _ = Deposito.objects.get_or_create(nome="Depósito Central", defaults={"endereco": dep_end})
        enderecos = []
        for i in range(10):
            e = Address.objects.create(
                logradouro=f"Rua {i+1}",
                numero=str(100 + i),
                bairro="Centro",
                cidade="São Paulo",
                estado="SP",
                cep=f"0100{i}000",
            )
            enderecos.append(e)
        fornecedores = []
        for i in range(10):
            nome_f = f"Fornecedor {i+1}"
            f, _ = Supplier.objects.get_or_create(nome=nome_f)
            f.email = f"forn{i+1}@exemplo.com"
            f.telefone = f"+55 11 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            f.documento = f"{random.randint(10000000000,99999999999)}"
            f.save()
            f.enderecos.add(enderecos[i % len(enderecos)])
            fornecedores.append(f)
        clientes = []
        for i in range(10):
            c = Customer.objects.create(
                nome=f"Cliente {i+1}",
                email=f"cli{i+1}@exemplo.com",
                telefone=f"+55 11 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                documento=f"{random.randint(10000000000,99999999999)}",
            )
            c.enderecos.add(enderecos[i % len(enderecos)])
            clientes.append(c)
        categorias = []
        for nome in ["Bebidas", "Lanches", "Doces", "Higiene", "Limpeza"]:
            categorias.append(Categoria.objects.get_or_create(nome=nome)[0])
        produtos = []
        unidades = ["UN", "CX", "KG", "LT"]
        marcas = ["Acme", "Beta", "Zeta", "Omega"]
        for i in range(20):
            cat = categorias[i % len(categorias)]
            preco = Decimal(random.randint(500, 10000)) / Decimal("100")
            custo = (preco * Decimal("0.6")).quantize(Decimal("0.01"))
            p = Produto.objects.create(
                nome=f"Produto {i+1}",
                categoria=cat,
                preco=preco,
                custo=custo,
                descricao=f"Descricao do produto {i+1}",
                unidade=random.choice(unidades),
                marca=random.choice(marcas),
                ean=str(random.randint(7890000000000, 7899999999999)),
                ncm="20098900",
                cfop="5102",
                disponivel=True,
            )
            produtos.append(p)
        compras = []
        # Criar ordens de compra e recebimentos vinculados
        for i in range(10):
            forn = fornecedores[i % len(fornecedores)]
            po = PurchaseOrder.objects.create(fornecedor=forn, responsavel=usuario, cost_center=cc, deposito=deposito, documento=f"NF-{1000+i}")
            escolhidos = random.sample(produtos, k=2)
            total_po = Decimal("0.00")
            for pr in escolhidos:
                q = random.randint(10, 50)
                item = PurchaseItem.objects.create(order=po, produto=pr, quantidade=q, custo_unitario=pr.custo)
                total_po += item.subtotal()
            po.total = total_po
            po.save(update_fields=["total"])
            FinanceiroService.registrar_compra(po)
            recibo = StockReceipt.objects.create(fornecedor=forn.nome, fornecedor_ref=forn, documento=f"RC-{po.slug}", responsavel=usuario, deposito=deposito, compra=po)
            for it in po.itens.all():
                StockReceiptItem.objects.create(recebimento=recibo, produto=it.produto, quantidade=it.quantidade, custo_unitario=it.custo_unitario)
                EstoqueService.registrar_entrada(it.produto, quantidade=it.quantidade, origem_slug=po.slug, responsavel=usuario, observacao="Entrada via compra", deposito=deposito)
            compras.append(po)
        # Opcional: pagar metade das compras para gerar saída de caixa
        for po in compras[:5]:
            FinanceiroService.registrar_pagamento_compra(po, valor=po.total)
        # Garantir estoque para todos os produtos
        for pr in produtos:
            if EstoqueService.saldo_produto(pr, deposito=deposito) <= 0:
                EstoqueService.registrar_entrada(pr, quantidade=random.randint(20, 60), origem_slug="seed-extra", responsavel=usuario, observacao="Ajuste de seed", deposito=deposito)
        pedidos = []
        for i in range(10):
            pedido = Pedido.objects.create(usuario=usuario, cost_center=cc)
            escolhidos = random.sample(produtos, k=3)
            itens = []
            for pr in escolhidos:
                q = random.randint(1, 3)
                item = ItemPedido.objects.create(pedido=pedido, produto=pr, quantidade=q, preco_unitario=pr.preco)
                itens.append(item)
            total = sum((it.quantidade * it.preco_unitario for it in itens), Decimal("0.00"))
            pedido.total = total
            pedido.save(update_fields=["total"])
            EstoqueService.registrar_saida(pedido, itens, deposito=deposito)
            if i < 5:
                FinanceiroService.registrar_receita_venda(pedido, cost_center_code=cc.codigo)
            else:
                metade = (total / Decimal("2")).quantize(Decimal("0.01"))
                restante = (total - metade).quantize(Decimal("0.01"))
                parcelas = [
                    {"valor": str(metade), "due_date": (options.get("today") if options.get("today") else None) or __import__("datetime").date.today().isoformat()},
                    {"valor": str(restante), "due_date": (__import__("datetime").date.today() + __import__("datetime").timedelta(days=30)).isoformat()},
                ]
                FinanceiroService.registrar_venda_a_prazo(pedido, cost_center_code=cc.codigo, parcelas=parcelas)
                FinanceiroService.receber_venda(pedido, valor=metade)
            FinanceiroService.registrar_custo_venda(pedido, cost_center_code=cc.codigo)
            pedidos.append(pedido)
        caixa_total = sum((l.valor for l in LedgerEntry.objects.filter(debit_account="Caixa")), Decimal("0.00"))
        self.stdout.write(f"Categorias: {len(categorias)}")
        self.stdout.write(f"Produtos: {len(produtos)}")
        self.stdout.write(f"Fornecedores: {len(fornecedores)}")
        self.stdout.write(f"Clientes: {len(clientes)}")
        self.stdout.write(f"Endereços: {len(enderecos)}")
        self.stdout.write(f"Compras: {len(compras)}")
        self.stdout.write(f"Pedidos: {len(pedidos)}")
        self.stdout.write(f"Caixa gerado: {caixa_total:.2f}")
