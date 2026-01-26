"""
Script para popular dados avançados de demonstração.
Cria produtos com ficha técnica, lotes com validades variadas e demonstra funcionalidades.

Uso:
    python manage.py shell < scripts/populate_advanced_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from tenant.models import Empresa
from catalog.models import Categoria, Produto, TipoProduto, FichaTecnicaItem
from stock.models import Deposito, Lote
from stock.services import StockService
from catalog.services import CatalogService


def criar_dados_demonstracao():
    """Cria dados completos para demonstração do sistema."""
    
    print("🚀 Iniciando população de dados avançados...")
    print("=" * 60)
    
    # 1. Buscar ou criar empresa
    empresa, created = Empresa.objects.get_or_create(
        nome_fantasia="Restaurante Demo",
        defaults={
            'razao_social': 'Restaurante Demo LTDA',
            'cnpj': '00000000000191',
            'is_active': True
        }
    )
    if created:
        print(f"✅ Empresa criada: {empresa.nome_fantasia}")
    else:
        print(f"📌 Usando empresa existente: {empresa.nome_fantasia}")
    
    # 2. Criar categorias
    print("\n📁 Criando categorias...")
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
    
    print(f"   • {cat_insumos.nome}")
    print(f"   • {cat_lanches.nome}")
    print(f"   • {cat_bebidas.nome}")
    
    # 3. Criar depósito
    print("\n🏢 Criando depósito...")
    deposito, _ = Deposito.objects.get_or_create(
        empresa=empresa,
        nome="Depósito Principal",
        defaults={
            'codigo': 'DEP-01',
            'is_padrao': True,
            'descricao': 'Depósito principal do restaurante'
        }
    )
    print(f"   • {deposito.nome} (Código: {deposito.codigo})")
    
    # 4. Criar INSUMOS (matérias-primas)
    print("\n🥬 Criando insumos (matérias-primas)...")
    
    pao_hamburguer = Produto.objects.create(
        empresa=empresa,
        nome="Pão de Hambúrguer",
        sku="INS-001",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('2.50'),
        preco_venda=Decimal('0.00'),  # Insumos não são vendidos diretamente
        is_active=True
    )
    
    carne_hamburguer = Produto.objects.create(
        empresa=empresa,
        nome="Carne de Hambúrguer (180g)",
        sku="INS-002",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('8.00'),
        preco_venda=Decimal('0.00'),
        is_active=True
    )
    
    queijo_cheddar = Produto.objects.create(
        empresa=empresa,
        nome="Queijo Cheddar (fatia)",
        sku="INS-003",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('1.50'),
        preco_venda=Decimal('0.00'),
        is_active=True
    )
    
    alface = Produto.objects.create(
        empresa=empresa,
        nome="Alface (folha)",
        sku="INS-004",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('0.30'),
        preco_venda=Decimal('0.00'),
        is_active=True
    )
    
    tomate = Produto.objects.create(
        empresa=empresa,
        nome="Tomate (rodela)",
        sku="INS-005",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('0.50'),
        preco_venda=Decimal('0.00'),
        is_active=True
    )
    
    bacon = Produto.objects.create(
        empresa=empresa,
        nome="Bacon (tira)",
        sku="INS-006",
        categoria=cat_insumos,
        tipo=TipoProduto.INSUMO,
        preco_custo=Decimal('2.00'),
        preco_venda=Decimal('0.00'),
        is_active=True
    )
    
    print(f"   • {pao_hamburguer.nome} - R$ {pao_hamburguer.preco_custo}")
    print(f"   • {carne_hamburguer.nome} - R$ {carne_hamburguer.preco_custo}")
    print(f"   • {queijo_cheddar.nome} - R$ {queijo_cheddar.preco_custo}")
    print(f"   • {alface.nome} - R$ {alface.preco_custo}")
    print(f"   • {tomate.nome} - R$ {tomate.preco_custo}")
    print(f"   • {bacon.nome} - R$ {bacon.preco_custo}")
    
    # 5. Criar PRODUTO FINAL (produto de revenda direto)
    print("\n🥤 Criando produto final (revenda)...")
    
    coca_cola = Produto.objects.create(
        empresa=empresa,
        nome="Coca-Cola Lata 350ml",
        sku="FIN-001",
        categoria=cat_bebidas,
        tipo=TipoProduto.FINAL,
        preco_custo=Decimal('3.50'),
        preco_venda=Decimal('7.00'),
        is_active=True
    )
    print(f"   • {coca_cola.nome} - Custo: R$ {coca_cola.preco_custo} | Venda: R$ {coca_cola.preco_venda}")
    
    # 6. Criar PRODUTOS COMPOSTOS (com ficha técnica)
    print("\n🍔 Criando produtos compostos (com ficha técnica)...")
    
    # X-Burger
    x_burger = Produto.objects.create(
        empresa=empresa,
        nome="X-Burger",
        sku="COMP-001",
        categoria=cat_lanches,
        tipo=TipoProduto.COMPOSTO,
        preco_custo=Decimal('0.00'),  # Será calculado automaticamente
        preco_venda=Decimal('25.00'),
        is_active=True,
        descricao="Hambúrguer clássico com queijo"
    )
    
    # Ficha técnica do X-Burger
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_burger,
        componente=pao_hamburguer,
        quantidade_liquida=Decimal('1.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_burger,
        componente=carne_hamburguer,
        quantidade_liquida=Decimal('1.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_burger,
        componente=queijo_cheddar,
        quantidade_liquida=Decimal('2.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_burger,
        componente=alface,
        quantidade_liquida=Decimal('2.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_burger,
        componente=tomate,
        quantidade_liquida=Decimal('2.000')
    )
    
    # Recalcula custo automaticamente
    custo_x_burger = CatalogService.recalcular_custo_produto(x_burger)
    x_burger.refresh_from_db()
    
    print(f"   • {x_burger.nome}")
    print(f"      - Custo calculado: R$ {x_burger.preco_custo}")
    print(f"      - Preço venda: R$ {x_burger.preco_venda}")
    print(f"      - Margem: {x_burger.margem_lucro:.1f}%")
    
    # X-Bacon
    x_bacon = Produto.objects.create(
        empresa=empresa,
        nome="X-Bacon",
        sku="COMP-002",
        categoria=cat_lanches,
        tipo=TipoProduto.COMPOSTO,
        preco_custo=Decimal('0.00'),
        preco_venda=Decimal('30.00'),
        is_active=True,
        descricao="Hambúrguer com queijo e bacon"
    )
    
    # Ficha técnica do X-Bacon
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=pao_hamburguer,
        quantidade_liquida=Decimal('1.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=carne_hamburguer,
        quantidade_liquida=Decimal('1.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=queijo_cheddar,
        quantidade_liquida=Decimal('2.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=bacon,
        quantidade_liquida=Decimal('3.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=alface,
        quantidade_liquida=Decimal('2.000')
    )
    FichaTecnicaItem.objects.create(
        empresa=empresa,
        produto_pai=x_bacon,
        componente=tomate,
        quantidade_liquida=Decimal('2.000')
    )
    
    custo_x_bacon = CatalogService.recalcular_custo_produto(x_bacon)
    x_bacon.refresh_from_db()
    
    print(f"   • {x_bacon.nome}")
    print(f"      - Custo calculado: R$ {x_bacon.preco_custo}")
    print(f"      - Preço venda: R$ {x_bacon.preco_venda}")
    print(f"      - Margem: {x_bacon.margem_lucro:.1f}%")
    
    # 7. Criar LOTES com datas de validade variadas
    print("\n📦 Criando lotes com datas de validade...")
    
    hoje = date.today()
    
    # Lotes de Pão
    lote_pao_1, _ = StockService.dar_entrada_com_lote(
        produto=pao_hamburguer,
        deposito=deposito,
        quantidade=Decimal('50.000'),
        codigo_lote='PAO-2026-001',
        data_validade=hoje + timedelta(days=5),  # Vence em 5 dias (CRÍTICO)
        data_fabricacao=hoje - timedelta(days=2),
        valor_unitario=pao_hamburguer.preco_custo,
        documento='NF-12345',
        observacao='Lote de demonstração - vence em breve'
    )
    
    lote_pao_2, _ = StockService.dar_entrada_com_lote(
        produto=pao_hamburguer,
        deposito=deposito,
        quantidade=Decimal('100.000'),
        codigo_lote='PAO-2026-002',
        data_validade=hoje + timedelta(days=15),  # Vence em 15 dias (ATENÇÃO)
        data_fabricacao=hoje - timedelta(days=1),
        valor_unitario=pao_hamburguer.preco_custo,
        documento='NF-12346'
    )
    
    lote_pao_3, _ = StockService.dar_entrada_com_lote(
        produto=pao_hamburguer,
        deposito=deposito,
        quantidade=Decimal('150.000'),
        codigo_lote='PAO-2026-003',
        data_validade=hoje + timedelta(days=45),  # Vence em 45 dias (OK)
        data_fabricacao=hoje,
        valor_unitario=pao_hamburguer.preco_custo,
        documento='NF-12347'
    )
    
    print(f"   • Pão: 3 lotes criados")
    print(f"      - {lote_pao_1.codigo_lote}: {lote_pao_1.quantidade_atual} un. (Vence: {lote_pao_1.data_validade}) [{lote_pao_1.status_validade}]")
    print(f"      - {lote_pao_2.codigo_lote}: {lote_pao_2.quantidade_atual} un. (Vence: {lote_pao_2.data_validade}) [{lote_pao_2.status_validade}]")
    print(f"      - {lote_pao_3.codigo_lote}: {lote_pao_3.quantidade_atual} un. (Vence: {lote_pao_3.data_validade}) [{lote_pao_3.status_validade}]")
    
    # Lotes de Carne
    lote_carne, _ = StockService.dar_entrada_com_lote(
        produto=carne_hamburguer,
        deposito=deposito,
        quantidade=Decimal('200.000'),
        codigo_lote='CARNE-2026-001',
        data_validade=hoje + timedelta(days=20),
        data_fabricacao=hoje - timedelta(days=1),
        valor_unitario=carne_hamburguer.preco_custo,
        documento='NF-12348'
    )
    print(f"   • Carne: {lote_carne.quantidade_atual} un. (Lote: {lote_carne.codigo_lote})")
    
    # Lotes de Queijo
    lote_queijo, _ = StockService.dar_entrada_com_lote(
        produto=queijo_cheddar,
        deposito=deposito,
        quantidade=Decimal('500.000'),
        codigo_lote='QUEIJO-2026-001',
        data_validade=hoje + timedelta(days=30),
        data_fabricacao=hoje - timedelta(days=2),
        valor_unitario=queijo_cheddar.preco_custo,
        documento='NF-12349'
    )
    print(f"   • Queijo: {lote_queijo.quantidade_atual} un. (Lote: {lote_queijo.codigo_lote})")
    
    # Lotes de Bacon
    lote_bacon, _ = StockService.dar_entrada_com_lote(
        produto=bacon,
        deposito=deposito,
        quantidade=Decimal('300.000'),
        codigo_lote='BACON-2026-001',
        data_validade=hoje + timedelta(days=25),
        data_fabricacao=hoje - timedelta(days=3),
        valor_unitario=bacon.preco_custo,
        documento='NF-12350'
    )
    print(f"   • Bacon: {lote_bacon.quantidade_atual} un. (Lote: {lote_bacon.codigo_lote})")
    
    # Lotes de Alface e Tomate
    lote_alface, _ = StockService.dar_entrada_com_lote(
        produto=alface,
        deposito=deposito,
        quantidade=Decimal('1000.000'),
        codigo_lote='ALFACE-2026-001',
        data_validade=hoje + timedelta(days=7),
        data_fabricacao=hoje,
        valor_unitario=alface.preco_custo,
        documento='NF-12351'
    )
    
    lote_tomate, _ = StockService.dar_entrada_com_lote(
        produto=tomate,
        deposito=deposito,
        quantidade=Decimal('1000.000'),
        codigo_lote='TOMATE-2026-001',
        data_validade=hoje + timedelta(days=8),
        data_fabricacao=hoje,
        valor_unitario=tomate.preco_custo,
        documento='NF-12352'
    )
    print(f"   • Alface: {lote_alface.quantidade_atual} un.")
    print(f"   • Tomate: {lote_tomate.quantidade_atual} un.")
    
    # Lote de Coca-Cola (produto final)
    lote_coca, _ = StockService.dar_entrada_com_lote(
        produto=coca_cola,
        deposito=deposito,
        quantidade=Decimal('500.000'),
        codigo_lote='COCA-2026-001',
        data_validade=hoje + timedelta(days=180),  # 6 meses
        data_fabricacao=hoje - timedelta(days=10),
        valor_unitario=coca_cola.preco_custo,
        documento='NF-12353'
    )
    print(f"   • Coca-Cola: {lote_coca.quantidade_atual} un.")
    
    # 8. Resumo final
    print("\n" + "=" * 60)
    print("✅ POPULAÇÃO DE DADOS CONCLUÍDA!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"   • Categorias: 3")
    print(f"   • Insumos: 6 produtos")
    print(f"   • Produtos Finais: 1 produto")
    print(f"   • Produtos Compostos: 2 produtos (com ficha técnica)")
    print(f"   • Lotes: 10 lotes com validades variadas")
    print(f"   • Depósito: {deposito.nome}")
    print(f"\n🎯 Produtos Compostos Criados:")
    print(f"   • {x_burger.nome}: R$ {x_burger.preco_custo} (custo) | R$ {x_burger.preco_venda} (venda)")
    print(f"   • {x_bacon.nome}: R$ {x_bacon.preco_custo} (custo) | R$ {x_bacon.preco_venda} (venda)")
    print(f"\n⚠️  Lotes com Alerta:")
    print(f"   • {lote_pao_1.codigo_lote}: Vence em {lote_pao_1.dias_ate_vencer} dias - Status: {lote_pao_1.status_validade}")
    print(f"\n🧪 Teste Sugerido:")
    print(f"   1. Acesse /admin/ e veja os produtos criados")
    print(f"   2. Teste endpoint: GET /api/lotes/vencendo/?dias=7")
    print(f"   3. Teste venda de X-Burger para ver explosão de BOM + FIFO")
    print(f"\n📝 Comandos úteis:")
    print(f"   • python manage.py shell")
    print(f"   • >>> from stock.models import Lote")
    print(f"   • >>> Lote.objects.filter(status_validade='CRITICO')")
    print("=" * 60)


if __name__ == '__main__':
    criar_dados_demonstracao()
