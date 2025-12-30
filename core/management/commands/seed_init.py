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

        addresses = []
        cidades = ['São Paulo', 'Rio de Janeiro', 'Curitiba', 'Belo Horizonte', 'Porto Alegre', 'Fortaleza', 'Recife', 'Natal', 'Brasília', 'Manaus']
        for i in range(20):
            addr, _ = Address.objects.get_or_create(
                logradouro=f'Rua Init {i+1}',
                numero=str(100+i),
                bairro='Centro',
                cidade=cidades[i % len(cidades)],
                estado='SP',
                cep=f'010{i:02d}000',
                defaults={'pais': 'Brasil', 'referencia': 'INIT'}
            )
            addresses.append(addr)

        suppliers = []
        for i in range(20):
            sup, _ = Supplier.objects.get_or_create(
                nome=f'Fornecedor Init {i+1}',
                defaults={'email': f'for{i+1}@init.local', 'telefone': '11999999999', 'documento': f'INIT-F-{i+1}'}
            )
            sup.enderecos.add(addresses[i])
            suppliers.append(sup)

        customers = []
        for i in range(20):
            cli, _ = Customer.objects.get_or_create(
                nome=f'Cliente Init {i+1}',
                defaults={'email': f'cli{i+1}@init.local', 'telefone': '11988888888', 'documento': f'INIT-C-{i+1}'}
            )
            cli.enderecos.add(addresses[i])
            customers.append(cli)

        categorias = []
        for i in range(20):
            c, _ = Categoria.objects.get_or_create(nome=f'Init Categoria {i+1}')
            categorias.append(c)
        produtos = []
        for i in range(20):
            preco = Decimal('10.00') + Decimal(i * 3)
            cat = categorias[i % len(categorias)]
            prod, _ = Produto.objects.get_or_create(
                nome=f'Produto Init {i+1}',
                categoria=cat,
                defaults={
                    'preco': preco,
                    'custo': (preco * Decimal('0.6')).quantize(Decimal('0.01')),
                    'unidade': 'UN',
                    'marca': 'InitBrand',
                    'descricao': f'INIT produto {i+1} categoria {cat.nome}',
                    'atributos': {'seed': 'init', 'categoria': cat.slug}
                }
            )
            produtos.append(prod)

        # Estoque: depósito e movimentos
        dep, _ = Deposito.objects.get_or_create(nome='Depósito Init')

        # Financeiro: contas e lançamentos básicos
        caixa, _ = Account.objects.get_or_create(nome='Caixa Init', codigo='INIT-CX', tipo=Account.Tipo.ATIVO)
        estoque_conta, _ = Account.objects.get_or_create(nome='Estoque Init', codigo='INIT-ES', tipo=Account.Tipo.ATIVO)
        receita, _ = Account.objects.get_or_create(nome='Receita Init', codigo='INIT-RC', tipo=Account.Tipo.RECEITA)
        despesa, _ = Account.objects.get_or_create(nome='Despesa Init', codigo='INIT-DP', tipo=Account.Tipo.DESPESA)
        cc, _ = CostCenter.objects.get_or_create(nome='Init CC', codigo='INIT-CC')
        base_entries = [
            ('INIT aporte de caixa', caixa.codigo, 'INIT-CAP', Decimal('1500.00')),
            ('INIT venda inicial', caixa.codigo, receita.codigo, Decimal('300.00')),
            ('INIT despesa setup', despesa.codigo, caixa.codigo, Decimal('250.00')),
        ]
        for desc, debit, credit, val in base_entries:
            LedgerEntry.objects.get_or_create(
                descricao=desc,
                debit_account=debit,
                credit_account=credit,
                valor=val,
                defaults={'usuario': user, 'debit_account_ref': Account.objects.filter(codigo=debit).first(), 'credit_account_ref': Account.objects.filter(codigo=credit).first(), 'cost_center': cc}
            )

        hoje = timezone.now().date()
        for i in range(20):
            ar, _ = Title.objects.get_or_create(tipo=Title.Tipo.AR, descricao=f'INIT recebível {i+1}', valor=Decimal('200.00') + Decimal(i*10), due_date=hoje)
            ap, _ = Title.objects.get_or_create(tipo=Title.Tipo.AP, descricao=f'INIT pagável {i+1}', valor=Decimal('150.00') + Decimal(i*8), due_date=hoje)
            TitleParcel.objects.get_or_create(title=ar, valor=ar.valor, due_date=hoje)
            TitleParcel.objects.get_or_create(title=ap, valor=ap.valor, due_date=hoje)

        for j in range(20):
            sup = suppliers[j % len(suppliers)]
            po, _ = PurchaseOrder.objects.get_or_create(
                fornecedor=sup,
                documento=f'INIT-PO-{j+1:03d}',
                defaults={'responsavel': user, 'cost_center': cc, 'deposito': dep, 'status': PurchaseOrder.Status.RECEBIDO}
            )
            total_po = Decimal('0.00')
            for k in range(3):
                prod = produtos[(j*3+k) % len(produtos)]
                custo = prod.custo or (prod.preco * Decimal('0.6'))
                item, _ = PurchaseItem.objects.get_or_create(order=po, produto=prod, quantidade=5 + (k % 2), defaults={'custo_unitario': custo})
                total_po += (Decimal(item.quantidade) * item.custo_unitario)
            if po.total != total_po:
                po.total = total_po
                po.save()
            rc, _ = StockReceipt.objects.get_or_create(
                fornecedor_ref=sup,
                documento=f'INIT-RC-{j+1:03d}',
                defaults={'responsavel': user, 'deposito': dep, 'compra': po, 'fornecedor': sup.nome, 'observacao': f'INIT recebimento {po.slug}'}
            )
            for pi in po.itens.all():
                StockReceiptItem.objects.get_or_create(recebimento=rc, produto=pi.produto, quantidade=pi.quantidade, defaults={'custo_unitario': pi.custo_unitario})
                StockMovement.objects.get_or_create(
                    produto=pi.produto,
                    tipo=StockMovement.Tipo.IN,
                    quantidade=pi.quantidade,
                    origem_slug=po.slug,
                    defaults={'responsavel': user, 'deposito': dep, 'observacao': f'INIT entrada compra {po.slug}'}
                )
            Title.objects.get_or_create(tipo=Title.Tipo.AP, descricao=f'INIT AP compra {po.slug}', valor=po.total, due_date=hoje)
            LedgerEntry.objects.get_or_create(
                descricao=f'INIT lançamento compra {po.slug}',
                debit_account=estoque_conta.codigo,
                credit_account='INIT-AP',
                valor=po.total,
                defaults={'usuario': user, 'debit_account_ref': estoque_conta, 'credit_account_ref': None, 'cost_center': cc}
            )

        for j in range(20):
            pv, _ = Pedido.objects.get_or_create(usuario=user, slug=None, defaults={'status': Pedido.Status.ENTREGUE, 'cost_center': cc})
            total_pv = Decimal('0.00')
            for k in range(2):
                prod = produtos[(j*2+k) % len(produtos)]
                item, created = ItemPedido.objects.get_or_create(pedido=pv, produto=prod, quantidade=1 + (k % 2), defaults={'preco_unitario': prod.preco})
                if created:
                    total_pv += (Decimal(item.quantidade) * item.preco_unitario)
                    StockMovement.objects.get_or_create(
                        produto=prod,
                        tipo=StockMovement.Tipo.OUT,
                        quantidade=item.quantidade,
                        origem_slug=pv.slug,
                        defaults={'responsavel': user, 'deposito': dep, 'pedido': pv, 'observacao': f'INIT saída venda {pv.slug}'}
                    )
            if total_pv > 0:
                pv.total = (pv.total or Decimal('0.00')) + total_pv
                pv.save()
                Title.objects.get_or_create(tipo=Title.Tipo.AR, descricao=f'INIT AR venda {pv.slug}', valor=total_pv, due_date=hoje)
                LedgerEntry.objects.get_or_create(
                    descricao=f'INIT lançamento venda {pv.slug}',
                    debit_account=caixa.codigo,
                    credit_account=receita.codigo,
                    valor=total_pv,
                    defaults={'usuario': user, 'debit_account_ref': caixa, 'credit_account_ref': receita, 'cost_center': cc}
                )

        self.stdout.write(self.style.SUCCESS('Seed init concluído'))
