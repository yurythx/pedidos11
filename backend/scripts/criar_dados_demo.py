"""
Script para criar dados de demonstração - Projeto Nix
Popula sistema com exemplos funcionais de BOM, Lotes e NFe
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from tenant.models import Empresa
from catalog.models import Produto, Categoria, TipoProduto, FichaTecnicaItem
from stock.models import Deposito, Lote
from stock.services import StockService
from nfe.models import ProdutoFornecedor

User = get_user_model()


def criar_dados_demo():
    """Cria dados de demonstração completos."""
    
    print("🚀 Iniciando criação de dados de demonstração...\n")
    
    # 1. Empresa e Usuário
    print("1️⃣ Criando empresa e usuário...")
    empresa, _ = Empresa.objects.get_or_create(
        nome_fantasia='Restaurante Demo',
        defaults={
            'razao_social': 'Restaurante Demo LTDA',
            'cnpj': '12345678000199'
        }
    )
    print(f"   ✅ Empresa: {empresa.nome_fantasia}")
    
    # Usuário admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@demo.com',
            password='admin123',
            empresa=empresa
        )
        print("   ✅ Usuário admin criado (senha: admin123)")
    
    # 2. Categoria
    print("\n2️⃣ Criando categorias...")
    cat_insumos, _ = Categoria.objects.get_or_create(
        empresa=empresa,
        nome='Insumos',
        defaults={'descricao': 'Matérias-primas'}
    )
    cat_produtos, _ = Categoria.objects.get_or_create(
        empresa=empresa,
        nome='Produtos Finais',
        defaults={'descricao': 'Produtos para venda'}
    )
    print("   ✅ Categorias criadas")
    
    # 3. Depósito
    print("\n3️⃣ Criando depósito...")
    deposito, _ = Deposito.objects.get_or_create(
        empresa=empresa,
        nome='Estoque Principal',
        defaults={'is_padrao': True}
    )
    print(f"   ✅ Depósito: {deposito.nome}")
    
    # 4. Produtos INSUMO
    print("\n4️⃣ Criando produtos INSUMO...")
    
    pao, _ = Produto.objects.get_or_create(
        empresa=empresa,
        nome='Pão de Hambúrguer',
        defaults={
            'tipo': TipoProduto.INSUMO,
            'categoria': cat_insumos,
            'preco_custo': Decimal('2.50'),
            'unidade': 'UN',
            'is_active': True,
            'codigo_barras': '7891000000001'
        }
    )
    
    carne, _ = Produto.objects.get_or_create(
        empresa=empresa,
        nome='Hambúrguer Bovino 180g',
        defaults={
            'tipo': TipoProduto.INSUMO,
            'categoria': cat_insumos,
            'preco_custo': Decimal('8.00'),
            'unidade': 'UN',
            'is_active': True,
            'codigo_barras': '7891000000002'
        }
    )
    
    queijo, _ = Produto.objects.get_or_create(
        empresa=empresa,
        nome='Queijo Cheddar Fatia',
        defaults={
            'tipo': TipoProduto.INSUMO,
            'categoria': cat_insumos,
            'preco_custo': Decimal('1.50'),
            'unidade': 'UN',
            'is_active': True,
            'codigo_barras': '7891000000003'
        }
    )
    
    alface, _ = Produto.objects.get_or_create(
        empresa=empresa,
        nome='Alface',
        defaults={
            'tipo': TipoProduto.INSUMO,
            'categoria': cat_insumos,
            'preco_custo': Decimal('0.50'),
            'unidade': 'UN',
            'is_active': True,
            'codigo_barras': '7891000000004'
        }
    )
    
    print(f"   ✅ Insumos: Pão, Carne, Queijo, Alface")
    
    # 5. Produto COMPOSTO (X-Burger)
    print("\n5️⃣ Criando produto COMPOSTO...")
    
    xburger, created = Produto.objects.get_or_create(
        empresa=empresa,
        nome='X-Burger Clássico',
        defaults={
            'tipo': TipoProduto.COMPOSTO,
            'categoria': cat_produtos,
            'preco_venda': Decimal('25.00'),
            'unidade': 'UN',
            'is_active': True
        }
    )
    
    if created:
        # Criar ficha técnica
        FichaTecnicaItem.objects.create(
            empresa=empresa,
            produto_pai=xburger,
            componente=pao,
            quantidade_liquida=Decimal('1')
        )
        FichaTecnicaItem.objects.create(
            empresa=empresa,
            produto_pai=xburger,
            componente=carne,
            quantidade_liquida=Decimal('1')
        )
        FichaTecnicaItem.objects.create(
            empresa=empresa,
            produto_pai=xburger,
            componente=queijo,
            quantidade_liquida=Decimal('2')
        )
        FichaTecnicaItem.objects.create(
            empresa=empresa,
            produto_pai=xburger,
            componente=alface,
            quantidade_liquida=Decimal('2')
        )
        
        # Recalcular custo
        from catalog.services import CatalogService
        CatalogService.recalcular_custo_produto(xburger)
        xburger.refresh_from_db()
        
        print(f"   ✅ X-Burger criado!")
        print(f"      Custo: R$ {xburger.preco_custo}")
        print(f"      Venda: R$ {xburger.preco_venda}")
        print(f"      Margem: {xburger.margem_lucro}%")
    
    # 6. Lotes com datas variadas
    print("\n6️⃣ Criando lotes...")
    
    hoje = date.today()
    
    lotes_criados = 0
    for produto, qtd, dias_validade in [
        (pao, 100, 5),      # Vence em 5 dias - CRÍTICO
        (pao, 150, 15),     # Vence em 15 dias - ATENÇÃO
        (pao, 200, 45),     # Vence em 45 dias - OK
        (carne, 50, 10),    # Vence em 10 dias
        (carne, 80, 30),    # Vence em 30 dias
        (queijo, 120, 20),  # Vence em 20 dias
        (alface, 50, 3),    # Vence em 3 dias - VENCENDO!
    ]:
        lote, mov = StockService.dar_entrada_com_lote(
            produto=produto,
            deposito=deposito,
            quantidade=Decimal(str(qtd)),
            codigo_lote=f'LOTE-{produto.nome[:3].upper()}-{dias_validade}D',
            data_validade=hoje + timedelta(days=dias_validade),
            data_fabricacao=hoje - timedelta(days=2),
            valor_unitario=produto.preco_custo,
            documento='ESTOQUE-INICIAL',
            observacao='Dados de demonstração'
        )
        lotes_criados += 1
    
    print(f"   ✅ {lotes_criados} lotes criados")
    print(f"      🔴 1 Vencendo (Alface - 3 dias)")
    print(f"      🟠 1 Crítico (Pão - 5 dias)")
    print(f"      🟡 2 Atenção (Pão - 15 dias, Queijo - 20 dias)")
    print(f"      🟢 3 OK (Pão - 45 dias, Carne - 10/30 dias)")
    
    # 7. Vínculos com fornecedor
    print("\n7️⃣ Criando vínculos fornecedor...")
    
    vinculos = [
        (pao, '12345678000199', 'Fornecedor ABC', 'PAO-123', 12),  # Caixa 12un
        (carne, '12345678000199', 'Fornecedor ABC', 'CAR-456', 10),  # Pacote 10un
        (queijo, '98765432000188', 'Fornecedor XYZ', 'QUE-789', 20), # Pacote 20un
    ]
    
    for produto, cnpj, nome, codigo, fator in vinculos:
        ProdutoFornecedor.objects.get_or_create(
            empresa=empresa,
            produto=produto,
            cnpj_fornecedor=cnpj,
            codigo_no_fornecedor=codigo,
            defaults={
                'nome_fornecedor': nome,
                'fator_conversao': Decimal(str(fator)),
                'ultimo_preco': produto.preco_custo
            }
        )
    
    print(f"   ✅ 3 vínculos criados")
    print(f"      (Para matching automático de NFe)")
    
    # 8. Resumo final
    print("\n" + "="*60)
    print("🎉 DADOS DE DEMONSTRAÇÃO CRIADOS COM SUCESSO!")
    print("="*60)
    print(f"""
📊 Resumo:
   • Empresa: {empresa.nome_fantasia}
   • Depósito: {deposito.nome}
   • Categorias: 2
   • Produtos INSUMO: 4
   • Produtos COMPOSTO: 1 (X-Burger)
   • Lotes: {lotes_criados}
   • Vínculos: 3

🔐 Login:
   Usuário: admin
   Senha: admin123

🌐 Acesse:
    IP Local: http://192.168.1.121:8002/admin/
    Domínio (se DNS ok): http://api.projetohavoc.shop:8002/admin/

✅ O que testar:
   1. Catalog → Produtos → X-Burger
      → Ver ficha técnica e custo calculado
   
   2. Stock → Lotes
      → Ver badges de status (🔴🟠🟢)
      → Filtrar por "Status de Validade"
   
   3. NFe → Vínculos
      → Ver produtos vinculados a fornecedores
   
   4. API → POST /api/nfe/importacao/upload-xml/
      → Testar upload de XML

🚀 Sistema pronto para uso!
    """)


if __name__ == '__main__':
    try:
        criar_dados_demo()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
