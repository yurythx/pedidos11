"""
Comando Django para popular banco de dados com dados de demonstração.
Uso: python manage.py popular_dados_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta

from tenant.models import Empresa
from catalog.models import Produto, Categoria, TipoProduto, FichaTecnicaItem
from catalog.services import CatalogService
from stock.models import Deposito, Lote
from stock.services import StockService
from nfe.models import ProdutoFornecedor
from partners.models import Fornecedor

class Command(BaseCommand):
    help = 'Popula banco de dados com dados de demonstração'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando criação de dados de demonstração...\n'))
        
        User = get_user_model()

        with transaction.atomic():
            # Helper para garantir clean() e save()
            def create_clean(model, **kwargs):
                obj = model(**kwargs)
                obj.full_clean()
                obj.save()
                return obj

            # 1. Empresa Totalmente Nova (CNPJ: 45.997.418/0001-53)
            self.stdout.write('🏢 Configurando empresa...')
            empresa = Empresa.objects.filter(cnpj='45997418000153').first()
            if not empresa:
                empresa = create_clean(Empresa, 
                    cnpj='45997418000153',
                    nome_fantasia='Nix Global Demo',
                    razao_social='Nix Global Demo LTDA'
                )
            self.stdout.write(self.style.SUCCESS(f'   ✅ Empresa: {empresa.nome_fantasia}'))

            # 2. Usuário admin
            user = User.objects.filter(username='admin_demo').first()
            if not user:
                user = User.objects.create_user(
                    username='admin_demo', email='demo@nix.com',
                    password='admin_demo_123', empresa=empresa,
                    is_staff=True, is_active=True
                )
            else:
                user.empresa = empresa
                user.save()

            # 3. Categorias 
            Categoria.objects.filter(empresa=empresa).delete()
            cat_i = create_clean(Categoria, empresa=empresa, nome='Insumos')
            cat_f = create_clean(Categoria, empresa=empresa, nome='Finalizados')

            # 4. Depósito
            Deposito.objects.filter(empresa=empresa).delete()
            dep = create_clean(Deposito, empresa=empresa, nome='Almoxarifado Principal', is_padrao=True)

            # 5. Fornecedores
            Fornecedor.objects.filter(empresa=empresa).delete()
            f_abc = create_clean(Fornecedor, empresa=empresa, cpf_cnpj='06947283000160', razao_social='FORNECEDOR GOOGLE')
            f_xyz = create_clean(Fornecedor, empresa=empresa, cpf_cnpj='33000118000179', razao_social='FORNECEDOR VIVO')

            # 6. Produtos INSUMO (REMOVIDO 'unidade')
            Produto.objects.filter(empresa=empresa).delete()
            pao = create_clean(Produto, empresa=empresa, nome='Pao Australiano Demo', tipo=TipoProduto.INSUMO, categoria=cat_i, preco_custo=Decimal('3.00'), preco_venda=Decimal('0.00'), codigo_barras='7890001')
            carne = create_clean(Produto, empresa=empresa, nome='Carne Angus Demo', tipo=TipoProduto.INSUMO, categoria=cat_i, preco_custo=Decimal('12.00'), preco_venda=Decimal('0.00'), codigo_barras='7890002')

            # 7. Produto COMPOSTO
            burger = create_clean(Produto, empresa=empresa, nome='Nix Burger Supreme Demo', tipo=TipoProduto.COMPOSTO, categoria=cat_f, preco_venda=Decimal('45.00'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=burger, componente=pao, quantidade_liquida=Decimal('1'))
            FichaTecnicaItem.objects.create(empresa=empresa, produto_pai=burger, componente=carne, quantidade_liquida=Decimal('1'))
            CatalogService.recalcular_custo_produto(burger)

            # 8. Lote
            hoje = date.today()
            StockService.dar_entrada_com_lote(pao, dep, Decimal('100'), 'LOTE-PAO-INIT', hoje+timedelta(days=10), hoje, pao.preco_custo, 'INIT')
            StockService.dar_entrada_com_lote(carne, dep, Decimal('50'), 'LOTE-CARNE-INIT', hoje+timedelta(days=7), hoje, carne.preco_custo, 'INIT')

            # 9. Vínculo NFe
            ProdutoFornecedor.objects.create(
                empresa=empresa, produto=pao, cnpj_fornecedor=f_abc.documento_numerico, 
                nome_fornecedor=f_abc.razao_social, codigo_no_fornecedor='XML-101', fator_conversao=Decimal('12')
            )

        self.stdout.write(self.style.SUCCESS('\n✨ DADOS DE TESTE PRONTOS! ✨'))
        self.stdout.write('   👤 Admin: admin_demo / admin_demo_123\n')
