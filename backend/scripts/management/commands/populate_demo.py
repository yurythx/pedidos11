"""
Management command para popular dados avançados de demonstração.
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import date, timedelta

from tenant.models import Empresa
from catalog.models import Categoria, Produto, TipoProduto, FichaTecnicaItem
from stock.models import Deposito
from stock.services import StockService
from catalog.services import CatalogService


class Command(BaseCommand):
    help = 'Popula dados avançados: produtos compostos, fichas técnicas e lotes'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando população de dados avançados...")
        self.stdout.write("=" * 60)
        
        # 1. Buscar ou criar empresa
        empresa, created = Empresa.objects.get_or_create(
            nome_fantasia="Restaurante Demo",
            defaults={
                'razao_social': 'Restaurante Demo LTDA',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Empresa criada: {empresa.nome_fantasia}"))
        else:
            self.stdout.write(f"📌 Usando empresa existente: {empresa.nome_fantasia}")
        
        # 2. Criar categorias
        self.stdout.write("\n📁 Criando categorias...")
        cat_insumos, _ = Categoria.objects.get_or_create(
            empresa=empresa,
            nome="Insumos",
            defaults={'descricao': 'Matérias-primas e ingredientes'}
        )
        
        cat_lanches, _ = Categoria.objects.get_or_create(
            empresa=empresa,
            nome="Lanches",
            defaults={'descricao': 'Lanches e hambúrgueres'}
        )
        
        cat_bebidas, _ = Categoria.objects.get_or_create(
            empresa=empresa,
            nome="Bebidas",
            defaults={'descricao': 'Bebidas e sucos'}
        )
        
        self.stdout.write(f"   • {cat_insumos.nome}, {cat_lanches.nome}, {cat_bebidas.nome}")
        
        # 3. Criar depósito
        self.stdout.write("\n🏢 Criando depósito...")
        deposito, _ = Deposito.objects.get_or_create(
            empresa=empresa,
            nome="Depósito Principal",
            defaults={
                'codigo': 'DEP-01',
                'is_padrao': True
            }
        )
        self.stdout.write(f"   • {deposito.nome}")
        
        # 4. Criar INSUMOS
        self.stdout.write("\n🥬 Criando insumos...")
        pao, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-001",
            defaults={
                'nome': "Pão de Hambúrguer",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('2.50'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        carne, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-002",
            defaults={
                'nome': "Carne de Hambúrguer (180g)",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('8.00'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        queijo, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-003",
            defaults={
                'nome': "Queijo Cheddar (fatia)",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('1.50'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        alface, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-004",
            defaults={
                'nome': "Alface (folha)",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('0.30'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        tomate, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-005",
            defaults={
                'nome': "Tomate (rodela)",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('0.50'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        bacon, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="INS-006",
            defaults={
                'nome': "Bacon (tira)",
                'categoria': cat_insumos,
                'tipo': TipoProduto.INSUMO,
                'preco_custo': Decimal('2.00'),
                'preco_venda': Decimal('0.00')
            }
        )
        
        self.stdout.write(f"   • 6 insumos criados")
        
        # 5. Criar PRODUTO COMPOSTO: X-Burger
        self.stdout.write("\n🍔 Criando produtos compostos...")
        x_burger, created = Produto.objects.get_or_create(
            empresa=empresa,
            sku="COMP-001",
            defaults={
                'nome': "X-Burger",
                'categoria': cat_lanches,
                'tipo': TipoProduto.COMPOSTO,
                'preco_custo': Decimal('0.00'),
                'preco_venda': Decimal('25.00'),
                'descricao': "Hambúrguer clássico com queijo"
            }
        )
        
        if created:
            # Criar ficha técnica
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=x_burger, componente=pao, quantidade_liquida=Decimal('1'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=x_burger, componente=carne, quantidade_liquida=Decimal('1'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=x_burger, componente=queijo, quantidade_liquida=Decimal('2'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=x_burger, componente=alface, quantidade_liquida=Decimal('2'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=x_burger, componente=tomate, quantidade_liquida=Decimal('2'))
            
            CatalogService.recalcular_custo_produto(x_burger)
            x_burger.refresh_from_db()
        
        self.stdout.write(f"   • {x_burger.nome} - Custo: R$ {x_burger.preco_custo} | Venda: R$ {x_burger.preco_venda}")
        
        # 6. Criar LOTES
        self.stdout.write("\n📦 Criando lotes...")
        hoje = date.today()
        
        # Lotes de Pão
        lote_pao_1, _ = StockService.dar_entrada_com_lote(
            produto=pao,
            deposito=deposito,
            quantidade=Decimal('50'),
            codigo_lote='PAO-2026-001',
            data_validade=hoje + timedelta(days=5),
            valor_unitario=pao.preco_custo,
            documento='NF-DEMO'
        )
        
        lote_pao_2, _ = StockService.dar_entrada_com_lote(
            produto=pao,
            deposito=deposito,
            quantidade=Decimal('100'),
            codigo_lote='PAO-2026-002',
            data_validade=hoje + timedelta(days=15),
            valor_unitario=pao.preco_custo,
            documento='NF-DEMO'
        )
        
        # Lotes outros insumos
        StockService.dar_entrada_com_lote(produto=carne, deposito=deposito, quantidade=Decimal('200'), codigo_lote='CARNE-001', data_validade=hoje + timedelta(days=20), valor_unitario=carne.preco_custo, documento='NF-DEMO')
        StockService.dar_entrada_com_lote(produto=queijo, deposito=deposito, quantidade=Decimal('500'), codigo_lote='QUEIJO-001', data_validade=hoje + timedelta(days=30), valor_unitario=queijo.preco_custo, documento='NF-DEMO')
        StockService.dar_entrada_com_lote(produto=bacon, deposito=deposito, quantidade=Decimal('300'), codigo_lote='BACON-001', data_validade=hoje + timedelta(days=25), valor_unitario=bacon.preco_custo, documento='NF-DEMO')
        StockService.dar_entrada_com_lote(produto=alface, deposito=deposito, quantidade=Decimal('1000'), codigo_lote='ALFACE-001', data_validade=hoje + timedelta(days=7), valor_unitario=alface.preco_custo, documento='NF-DEMO')
        StockService.dar_entrada_com_lote(produto=tomate, deposito=deposito, quantidade=Decimal('1000'), codigo_lote='TOMATE-001', data_validade=hoje + timedelta(days=8), valor_unitario=tomate.preco_custo, documento='NF-DEMO')
        
        self.stdout.write(f"   • {lote_pao_1.codigo_lote}: {lote_pao_1.quantidade_atual} un. - Status: {lote_pao_1.status_validade}")
        self.stdout.write(f"   • {lote_pao_2.codigo_lote}: {lote_pao_2.quantidade_atual} un. - Status: {lote_pao_2.status_validade}")
        self.stdout.write(f"   • + 5 lotes adicionais")
        
        # 7. Resumo
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ POPULAÇÃO CONCLUÍDA!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\n📊 Dados criados:")
        self.stdout.write(f"   • 6 Insumos")
        self.stdout.write(f"   • 1 Produto Composto (X-Burger) com ficha técnica")
        self.stdout.write(f"   • 7 Lotes com validades variadas")
        self.stdout.write(f"\n🧪 Testes sugeridos:")
        self.stdout.write(f"   • python manage.py runserver")
        self.stdout.write(f"   • Acesse: /admin/")
        self.stdout.write(f"   • API: GET /api/lotes/vencendo/?dias=7")
        self.stdout.write("=" * 60)
