import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from tenant.models import Empresa
from stock.models import Deposito
from catalog.models import Categoria, Produto, TipoProduto
from restaurant.models import Mesa
from financial.models import Caixa
from locations.models import Endereco
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura ambiente de produção com dados iniciais'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Iniciando setup de produção...')

        # 1. Criar Empresa
        empresa, created = Empresa.objects.get_or_create(
            nome_fantasia='Nix Restaurante',
            defaults={
                'cnpj': '00000000000191',
                'razao_social': 'Nix Restaurante LTDA',
                'telefone': '11999999999'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Empresa criada: {empresa.nome_fantasia}'))
            
            # Criar endereço
            Endereco.objects.create(
                empresa=empresa,  # Campo obrigatório (TenantModel)
                content_type=ContentType.objects.get_for_model(Empresa),
                object_id=empresa.id,
                logradouro='Rua Principal',
                numero='100',
                bairro='Centro',
                cidade='São Paulo',
                uf='SP',
                cep='01001-000',
                tipo='PRINCIPAL'
            )
        else:
            self.stdout.write(f'Empresa já existe: {empresa.nome_fantasia}')

        # 2. Criar Usuário Suporte
        try:
            user = User.objects.get(username='suporte')
            self.stdout.write('Usuário suporte já existe.')
        except User.DoesNotExist:
            user = User.objects.create_superuser(
                username='suporte',
                email='suporte@nix.com',
                password='suporte123',
                empresa=empresa
            )
            self.stdout.write(self.style.SUCCESS('Usuário suporte criado (suporte/suporte123)'))
        
        # Atualizar permissões do usuário
        user.empresa = empresa
        user.role_caixa = True
        user.role_atendente = True
        user.is_colaborador = True
        user.cargo = 'ADMIN'
        user.save()
        self.stdout.write('Permissões de suporte atualizadas.')

        # 3. Criar Depósito Principal
        deposito, created = Deposito.objects.get_or_create(
            empresa=empresa,
            nome='Estoque Principal',
            defaults={'padrao': True}
        )
        if created:
             self.stdout.write(self.style.SUCCESS('Depósito Principal criado'))

        # 4. Criar Caixa
        caixa, created = Caixa.objects.get_or_create(
            empresa=empresa,
            nome='Caixa 01',
            defaults={'ativo': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Caixa 01 criado'))

        # 5. Criar Categorias e Produtos Básicos
        cat_bebidas, _ = Categoria.objects.get_or_create(empresa=empresa, nome='Bebidas')
        cat_lanches, _ = Categoria.objects.get_or_create(empresa=empresa, nome='Lanches')

        prod_coca, created = Produto.objects.get_or_create(
            empresa=empresa,
            nome='Coca Cola Lata',
            defaults={
                'categoria': cat_bebidas,
                'preco_venda': Decimal('6.00'),
                'preco_custo': Decimal('3.00'),
                'tipo': TipoProduto.PRODUTO_FINAL,
                'ncm': '22021000',
                'imprimir_producao': True
            }
        )
        
        prod_burger, created = Produto.objects.get_or_create(
            empresa=empresa,
            nome='X-Burger',
            defaults={
                'categoria': cat_lanches,
                'preco_venda': Decimal('25.00'),
                'preco_custo': Decimal('10.00'),
                'tipo': TipoProduto.PRODUTO_FINAL,
                'imprimir_producao': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Categorias e produtos básicos criados'))

        # 6. Criar Mesas (1 a 10)
        for i in range(1, 11):
            Mesa.objects.get_or_create(
                empresa=empresa,
                numero=i,
                defaults={'capacidade': 4}
            )
        self.stdout.write(self.style.SUCCESS('Mesas 1-10 criadas'))
        
        # 7. Criar Comandas (100 a 150)
        from restaurant.models import Comanda
        for i in range(100, 151):
            Comanda.objects.get_or_create(
                empresa=empresa,
                codigo=str(i),
                defaults={'status': 'LIVRE'}
            )
        self.stdout.write(self.style.SUCCESS('Comandas 100-150 criadas'))

        self.stdout.write(self.style.SUCCESS('Setup de produção concluído com sucesso!'))
