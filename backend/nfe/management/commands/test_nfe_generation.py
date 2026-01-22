from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenant.models import Empresa
from partners.models import Cliente, TipoPessoa
from locations.models import Endereco, TipoEndereco, UF
from catalog.models import Produto, Categoria
from sales.models import Venda, ItemVenda, StatusVenda
from nfe.services import NFeService
from nfe.models import NotaFiscal
from decimal import Decimal
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa a geração de NFe a partir de uma Venda'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando teste de geração de NFe...")

        # 1. Setup Empresa e Usuário
        empresa, _ = Empresa.objects.get_or_create(
            razao_social="Empresa Teste NFe",
            defaults={
                'nome_fantasia': "Empresa Teste NFe",
                'cnpj': '33.000.167/0001-01', # CNPJ Válido (Petrobras)
                'inscricao_estadual': '123456789',
                'ambiente_nfe': '2', # Homologação
                'regime_tributario': '1', # Simples
                'numero_nfe_atual': 0
            }
        )
        
        user, _ = User.objects.get_or_create(
            username="tester_nfe",
            defaults={'email': 'tester@nfe.com', 'empresa': empresa}
        )

        # Garantir endereço da empresa
        if not Endereco.objects.filter(content_type__model='empresa', object_id=empresa.id).exists():
            Endereco.objects.create(
                empresa=empresa,
                content_object=empresa,
                tipo=TipoEndereco.COMERCIAL,
                cep='01310-100',
                logradouro='Av. Paulista',
                numero='1000',
                bairro='Bela Vista',
                cidade='São Paulo',
                uf=UF.SP,
                codigo_municipio_ibge='3550308'
            )

        # 2. Setup Cliente com Endereço
        cliente, _ = Cliente.objects.get_or_create(
            empresa=empresa,
            cpf_cnpj="710.675.780-21", # CPF Válido
            defaults={
                'nome': "Cliente Teste NFe",
                'tipo_pessoa': TipoPessoa.FISICA,
                'email': 'cliente@teste.com'
            }
        )
        
        # Garantir endereço
        if not cliente.enderecos.exists():
            Endereco.objects.create(
                empresa=empresa,
                content_object=cliente,
                tipo=TipoEndereco.FISICO,
                cep='01001-000',
                logradouro='Praça da Sé',
                numero='100',
                bairro='Sé',
                cidade='São Paulo',
                uf=UF.SP,
                codigo_municipio_ibge='3550308'
            )

        # 3. Setup Categoria e Produto
        categoria, _ = Categoria.objects.get_or_create(
            empresa=empresa,
            nome="Categoria NFe",
            defaults={'slug': 'categoria-nfe'}
        )

        produto, _ = Produto.objects.get_or_create(
            empresa=empresa,
            sku="PROD-NFE-01",
            defaults={
                'nome': "Produto Teste NFe",
                'categoria': categoria,
                'preco_venda': Decimal('100.00'),
                'ncm': '12345678',
                'cfop_padrao': '5102',
                'unidade_comercial': 'UN',
                'origem_mercadoria': '0'
            }
        )

        # 4. Criar Venda Finalizada
        venda = Venda.objects.create(
            empresa=empresa,
            cliente=cliente,
            vendedor=user,
            status=StatusVenda.FINALIZADA, # Simular venda já finalizada
            total_bruto=Decimal('200.00'),
            total_liquido=Decimal('200.00')
        )
        
        ItemVenda.objects.create(
            empresa=empresa,
            venda=venda,
            produto=produto,
            quantidade=Decimal('2.000'),
            preco_unitario=Decimal('100.00'),
            subtotal=Decimal('200.00')
        )
        
        self.stdout.write(f"Venda criada: {venda}")

        # 5. Gerar NFe
        try:
            self.stdout.write("Gerando NFe...")
            nota = NFeService.gerar_nfe_de_venda(empresa, venda.id, user)
            self.stdout.write(self.style.SUCCESS(f"NFe gerada com sucesso: {nota}"))
            self.stdout.write(f"Número: {nota.numero}")
            self.stdout.write(f"Chave (simulada): {nota.chave_acesso}")
            self.stdout.write(f"Itens: {nota.itens.count()}")
            
            # Verificar itens
            item = nota.itens.first()
            self.stdout.write(f"Item 1: {item.descricao_produto} - Qtd: {item.quantidade} - Valor: {item.valor_total}")
            
            # 6. Gerar XML
            self.stdout.write("Gerando XML...")
            xml = NFeService.gerar_xml(nota.id, empresa)
            self.stdout.write(self.style.SUCCESS("XML gerado com sucesso!"))
            self.stdout.write(f"Início do XML: {xml[:200]}...")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao gerar NFe: {e}"))
            import traceback
            traceback.print_exc()

