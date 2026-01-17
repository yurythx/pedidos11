from django.test import TestCase
from decimal import Decimal
from datetime import date
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito, Movimentacao, TipoMovimentacao, Lote
from nfe.services import NFeService
from partners.models import Fornecedor, TipoPessoa

class NFeServiceImportacaoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia='Empresa NFe',
            razao_social='Empresa NFe LTDA',
            cnpj='11222333000181',
            email='nfe@empresa.test',
        )
        self.user = CustomUser.objects.create_user(
            username='nfe',
            email='nfe@empresa.test',
            password='123456',
            empresa=self.empresa,
            cargo=TipoCargo.GERENTE,
        )
        self.categoria = Categoria.objects.create(
            empresa=self.empresa,
            nome='Cat NFe',
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Insumo NFe',
            categoria=self.categoria,
            tipo=TipoProduto.INSUMO,
            preco_venda=Decimal('0.00'),
            preco_custo=Decimal('2.00'),
        )
        self.deposito = Deposito.objects.create(
            empresa=self.empresa,
            nome='Depósito NFe',
            is_padrao=True,
        )
        self.fornecedor = Fornecedor.objects.create(
            empresa=self.empresa,
            razao_social='Fornecedor XYZ',
            cpf_cnpj='73621701000129',
            tipo_pessoa=TipoPessoa.JURIDICA,
        )

    def test_efetivar_importacao_cria_lote_movimentacao_e_vinculo(self):
        payload = {
            'deposito_id': str(self.deposito.id),
            'numero_nfe': '12345',
            'serie_nfe': '1',
            'fornecedor': {'cnpj': '73621701000129', 'nome': 'Fornecedor XYZ'},
            'itens': [
                {
                    'codigo_xml': 'COD-XML-1',
                    'produto_id': str(self.produto.id),
                    'fator_conversao': 2,
                    'qtd_xml': 3,
                    'preco_custo': 4.50,
                    'lote': {
                        'codigo': 'LOTE-NFE-1',
                        'validade': str(date.today().replace(year=date.today().year + 1)),
                    },
                }
            ],
        }
        resultado = NFeService.efetivar_importacao_nfe(
            empresa=self.empresa,
            payload=payload,
            usuario=self.user.username,
        )
        self.assertEqual(resultado['documento'], 'NFE-1-12345')
        self.assertEqual(len(resultado['itens_processados']), 1)
        self.assertGreaterEqual(resultado['lotes_criados'], 1)
        self.assertGreaterEqual(resultado['vinculos_criados'], 1)
        movs = Movimentacao.objects.filter(
            empresa=self.empresa,
            deposito=self.deposito,
            tipo=TipoMovimentacao.ENTRADA,
            documento='NFE-1-12345',
        )
        self.assertTrue(movs.exists())
        lote = Lote.objects.get(
            empresa=self.empresa,
            produto=self.produto,
            deposito=self.deposito,
            codigo_lote='LOTE-NFE-1',
        )
        self.assertEqual(str(lote.data_validade), payload['itens'][0]['lote']['validade'])
