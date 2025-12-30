from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Cria dados iniciais (clientes, fornecedores, endereços, produtos, estoque e financeiro) marcados como 'init'"

    def handle(self, *args, **options):
        from cadastro.models import Address, Supplier, Customer, Categoria, Produto
        from estoque.models import Deposito, StockMovement, StockReceipt, StockReceiptItem
        from financeiro.models import Account, CostCenter, LedgerEntry, Title, TitleParcel
        from compras.models import PurchaseOrder, PurchaseItem
        from vendas.models import Pedido, ItemPedido
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()

        # Endereços
        addresses = []
        cidades = ['São Paulo', 'Rio de Janeiro', 'Curitiba', 'Belo Horizonte', 'Porto Alegre']
        for i in range(5):
            addr, _ = Address.objects.get_or_create(
                logradouro=f'Rua Init {i+1}',
                numero=str(100+i),
                bairro='Centro',
                cidade=cidades[i % len(cidades)],
                estado='SP',
                cep=f'0100{i}000',
                defaults={'pais': 'Brasil', 'referencia': 'INIT'}
            )
            addresses.append(addr)

        # Fornecedores
        suppliers = []
        for i in range(5):
            sup, _ = Supplier.objects.get_or_create(
                nome=f'Fornecedor Init {i+1}',
                defaults={'email': f'for{i+1}@init.local', 'telefone': '11999999999', 'documento': f'INIT-F-{i+1}'}
            )
            sup.enderecos.add(addresses[i])
            suppliers.append(sup)

        # Clientes
        customers = []
        for i in range(5):
            cli, _ = Customer.objects.get_or_create(
                nome=f'Cliente Init {i+1}',
                defaults={'email': f'cli{i+1}@init.local', 'telefone': '11988888888', 'documento': f'INIT-C-{i+1}'}
            )
            cli.enderecos.add(addresses[i])
            customers.append(cli)

        # Categoria e Produtos
        cat, _ = Categoria.objects.get_or_create(nome='Init Categoria')
        produtos = []
        for i in range(5):
            preco = Decimal('10.00') + Decimal(i * 5)
            prod, _ = Produto.objects.get_or_create(
                nome=f'Produto Init {i+1}',
                categoria=cat,
                defaults={
                    'preco': preco,
                    'custo': preco * Decimal('0.6'),
                    'unidade': 'UN',
                    'marca': 'InitBrand',
                    'descricao': 'INIT',
                    'atributos': {'seed': 'init'}
                }
            )
            produtos.append(prod)

        # Estoque: depósito e movimentos
        dep, _ = Deposito.objects.get_or_create(nome='Depósito Init')
        for prod in produtos:
            StockMovement.objects.get_or_create(
                produto=prod,
                tipo=StockMovement.Tipo.IN,
                quantidade=10,
                origem_slug='init',
                defaults={'responsavel': user, 'deposito': dep, 'observacao': 'INIT entrada'}
            )
            StockMovement.objects.get_or_create(
                produto=prod,
                tipo=StockMovement.Tipo.OUT,
                quantidade=2,
                origem_slug='init',
                defaults={'responsavel': user, 'deposito': dep, 'observacao': 'INIT saída'}
            )

        # Financeiro: contas e lançamentos básicos
        caixa, _ = Account.objects.get_or_create(nome='Caixa Init', codigo='INIT-CX', tipo=Account.Tipo.ATIVO)
        estoque_conta, _ = Account.objects.get_or_create(nome='Estoque Init', codigo='INIT-ES', tipo=Account.Tipo.ATIVO)
        receita, _ = Account.objects.get_or_create(nome='Receita Init', codigo='INIT-RC', tipo=Account.Tipo.RECEITA)
        despesa, _ = Account.objects.get_or_create(nome='Despesa Init', codigo='INIT-DP', tipo=Account.Tipo.DESPESA)
        cc, _ = CostCenter.objects.get_or_create(nome='Init CC', codigo='INIT-CC')
        # Entradas e saídas iniciais
        LedgerEntry.objects.get_or_create(
            descricao='INIT aporte de caixa',
            debit_account=caixa.codigo,
            credit_account='INIT-CAP',
            valor=Decimal('1000.00'),
            defaults={'usuario': user, 'debit_account_ref': caixa, 'credit_account_ref': None, 'cost_center': cc}
        )
        LedgerEntry.objects.get_or_create(
            descricao='INIT venda inicial',
            debit_account=caixa.codigo,
            credit_account=receita.codigo,
            valor=Decimal('200.00'),
            defaults={'usuario': user, 'debit_account_ref': caixa, 'credit_account_ref': receita, 'cost_center': cc}
        )
        LedgerEntry.objects.get_or_create(
            descricao='INIT despesa setup',
            debit_account=despesa.codigo,
            credit_account=caixa.codigo,
            valor=Decimal('150.00'),
            defaults={'usuario': user, 'debit_account_ref': despesa, 'credit_account_ref': caixa, 'cost_center': cc}
        )

        # Títulos iniciais (AR/AP) com parcelas
        hoje = timezone.now().date()
        ar, _ = Title.objects.get_or_create(tipo=Title.Tipo.AR, descricao='INIT recebível', valor=Decimal('300.00'), due_date=hoje)
        ap, _ = Title.objects.get_or_create(tipo=Title.Tipo.AP, descricao='INIT pagável', valor=Decimal('180.00'), due_date=hoje)
        TitleParcel.objects.get_or_create(title=ar, valor=Decimal('300.00'), due_date=hoje)
        TitleParcel.objects.get_or_create(title=ap, valor=Decimal('180.00'), due_date=hoje)

        # Ordem de Compra INIT com recebimento
        po, _ = PurchaseOrder.objects.get_or_create(
            fornecedor=suppliers[0],
            documento='INIT-PO-001',
            defaults={'responsavel': user, 'cost_center': cc, 'deposito': dep, 'status': PurchaseOrder.Status.RECEBIDO}
        )
        total_po = Decimal('0.00')
        for prod in produtos[:3]:
            custo = prod.custo or (prod.preco * Decimal('0.6'))
            item, _ = PurchaseItem.objects.get_or_create(order=po, produto=prod, quantidade=5, defaults={'custo_unitario': custo})
            total_po += (Decimal(item.quantidade) * item.custo_unitario)
        if po.total != total_po:
            po.total = total_po
            po.save()
        rc, _ = StockReceipt.objects.get_or_create(
            fornecedor_ref=suppliers[0],
            documento='INIT-RC-001',
            defaults={'responsavel': user, 'deposito': dep, 'compra': po, 'fornecedor': suppliers[0].nome, 'observacao': 'INIT recebimento'}
        )
        for pi in po.itens.all():
            StockReceiptItem.objects.get_or_create(recebimento=rc, produto=pi.produto, quantidade=pi.quantidade, defaults={'custo_unitario': pi.custo_unitario})
        # Financeiro da compra: título AP e lançamento estoque x AP
        ap_po, _ = Title.objects.get_or_create(tipo=Title.Tipo.AP, descricao='INIT compra recebida', valor=po.total, due_date=hoje)
        LedgerEntry.objects.get_or_create(
            descricao='INIT lançamento compra recebida',
            debit_account=estoque_conta.codigo,
            credit_account='INIT-AP',
            valor=po.total,
            defaults={'usuario': user, 'debit_account_ref': estoque_conta, 'credit_account_ref': None, 'cost_center': cc}
        )

        # Pedido de Venda INIT com itens
        pv, _ = Pedido.objects.get_or_create(usuario=user, defaults={'status': Pedido.Status.ENTREGUE, 'cost_center': cc})
        total_pv = Decimal('0.00')
        for prod in produtos[:2]:
            item, created = ItemPedido.objects.get_or_create(pedido=pv, produto=prod, quantidade=1, defaults={'preco_unitario': prod.preco})
            if created:
                total_pv += (Decimal(item.quantidade) * item.preco_unitario)
        if total_pv > 0:
            pv.total = total_pv
            pv.save()
            ar_pv, _ = Title.objects.get_or_create(tipo=Title.Tipo.AR, descricao='INIT venda pedido', valor=pv.total, due_date=hoje)
            LedgerEntry.objects.get_or_create(
                descricao='INIT lançamento venda pedido',
                debit_account=caixa.codigo,
                credit_account=receita.codigo,
                valor=pv.total,
                defaults={'usuario': user, 'debit_account_ref': caixa, 'credit_account_ref': receita, 'cost_center': cc}
            )

        self.stdout.write(self.style.SUCCESS('Seed init concluído'))
