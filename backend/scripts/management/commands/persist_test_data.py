from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
from tenant.models import Empresa
from authentication.models import CustomUser, TipoCargo
from catalog.models import Categoria, Produto, TipoProduto
from stock.models import Deposito
from sales.models import Venda, ItemVenda
from sales.services import VendaService
from stock.services import StockService
from financial.services import FinanceiroService
from nfe.services import NFeService
from partners.models import Fornecedor, TipoPessoa

class Command(BaseCommand):
    help = "Persiste dados equivalentes aos cenários de testes no banco atual"

    @transaction.atomic
    def handle(self, *args, **options):
        empresa, _ = Empresa.objects.get_or_create(
            cnpj="11.222.333/0001-81",
            defaults={
                "nome_fantasia": "Empresa Teste",
                "razao_social": "Empresa Teste LTDA",
                "email": "contato@empresa.test",
            },
        )
        def usuario(username, email, cargo):
            u, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "empresa": empresa,
                    "cargo": cargo,
                },
            )
            if created:
                u.set_password("123456")
                u.save()
            return u
        tester = usuario("tester", "tester@empresa.test", TipoCargo.GERENTE)
        tester2 = usuario("tester2", "tester2@empresa.test", TipoCargo.GERENTE)
        fefo = usuario("fefo", "fefo@empresa.test", TipoCargo.GERENTE)
        saldo = usuario("saldo", "saldo@empresa.test", TipoCargo.ESTOQUISTA)
        nfe_user = usuario("nfe", "nfe@empresa.test", TipoCargo.GERENTE)
        def categoria(nome):
            return Categoria.objects.get_or_create(empresa=empresa, nome=nome)[0]
        cat_teste = categoria("Categoria Teste")
        cat_fefo = categoria("Cat FEFO")
        cat_saldo = categoria("Cat Saldo")
        cat_nfe = categoria("Cat NFe")
        def deposito(nome):
            return Deposito.objects.get_or_create(empresa=empresa, nome=nome, defaults={"is_padrao": True})[0]
        dep_teste = deposito("Depósito Teste")
        dep_teste2 = deposito("Depósito Teste 2")
        dep_fefo = deposito("Depósito FEFO")
        dep_saldo = deposito("Depósito Saldo")
        dep_nfe = deposito("Depósito NFe")
        prod_final, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Produto Final",
            defaults={
                "categoria": cat_teste,
                "tipo": TipoProduto.FINAL,
                "preco_venda": Decimal("50.00"),
                "preco_custo": Decimal("30.00"),
                "codigo_barras": "BAR-FINAL-1",
            },
        )
        prod_final2, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Produto Final 2",
            defaults={
                "categoria": cat_teste,
                "tipo": TipoProduto.FINAL,
                "preco_venda": Decimal("40.00"),
                "preco_custo": Decimal("20.00"),
                "codigo_barras": "BAR-FINAL-2",
            },
        )
        prod_fefo, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Produto FEFO",
            defaults={
                "categoria": cat_fefo,
                "tipo": TipoProduto.FINAL,
                "preco_venda": Decimal("10.00"),
                "preco_custo": Decimal("5.00"),
                "codigo_barras": "BAR-FEFO-1",
            },
        )
        prod_saldo, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Produto Saldo",
            defaults={
                "categoria": cat_saldo,
                "tipo": TipoProduto.FINAL,
                "preco_venda": Decimal("10.00"),
                "preco_custo": Decimal("5.00"),
                "codigo_barras": "BAR-SALDO-1",
            },
        )
        insumo_nfe, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Insumo NFe",
            defaults={
                "categoria": cat_nfe,
                "tipo": TipoProduto.INSUMO,
                "preco_venda": Decimal("0.00"),
                "preco_custo": Decimal("2.00"),
                "codigo_barras": "BAR-INSUMO-NFE-1",
            },
        )
        def entrada(produto, deposito, quantidade, codigo, dias):
            try:
                StockService.dar_entrada_com_lote(
                    produto=produto,
                    deposito=deposito,
                    quantidade=quantidade,
                    codigo_lote=codigo,
                    data_validade=date.today() + timedelta(days=dias),
                )
            except Exception:
                pass
        entrada(prod_final, dep_teste, Decimal("10.000"), "LOTE-TST", 365)
        entrada(prod_final2, dep_teste2, Decimal("10.000"), "LOTE-CANC", 365)
        entrada(prod_fefo, dep_fefo, Decimal("5.000"), "LOTE-A", 30)
        entrada(prod_fefo, dep_fefo, Decimal("5.000"), "LOTE-B", 120)
        entrada(prod_saldo, dep_saldo, Decimal("2.000"), "LOTE-SALDO", 90)
        venda1, _ = Venda.objects.get_or_create(
            empresa=empresa,
            vendedor=tester,
            observacoes="Teste integração serviços",
            defaults={"tipo_pagamento": "DINHEIRO"},
        )
        if not venda1.itens.exists():
            ItemVenda.objects.create(
                empresa=empresa,
                venda=venda1,
                produto=prod_final,
                quantidade=Decimal("2.000"),
                preco_unitario=prod_final.preco_venda,
                desconto=Decimal("0.00"),
            )
        try:
            VendaService.finalizar_venda(
                venda_id=venda1.id,
                deposito_id=dep_teste.id,
                usuario=tester.username,
                usar_lotes=True,
                gerar_conta_receber=True,
            )
            contas = list(venda1.contas_receber.all())
            if contas:
                FinanceiroService.baixar_conta_receber(contas[0].id, tipo_pagamento="DINHEIRO")
        except Exception:
            pass
        venda2, _ = Venda.objects.get_or_create(
            empresa=empresa,
            vendedor=tester2,
            defaults={"tipo_pagamento": "DINHEIRO"},
        )
        if not venda2.itens.exists():
            ItemVenda.objects.create(
                empresa=empresa,
                venda=venda2,
                produto=prod_final2,
                quantidade=Decimal("3.000"),
                preco_unitario=prod_final2.preco_venda,
                desconto=Decimal("0.00"),
            )
        try:
            VendaService.finalizar_venda(
                venda_id=venda2.id,
                deposito_id=dep_teste2.id,
                usuario=tester2.username,
                usar_lotes=True,
                gerar_conta_receber=False,
            )
            VendaService.cancelar_venda(
                venda_id=venda2.id,
                motivo="Teste cancelamento",
                usuario=tester2.username,
            )
        except Exception:
            pass
        venda3, _ = Venda.objects.get_or_create(
            empresa=empresa,
            vendedor=fefo,
            defaults={"tipo_pagamento": "DINHEIRO"},
        )
        if not venda3.itens.exists():
            ItemVenda.objects.create(
                empresa=empresa,
                venda=venda3,
                produto=prod_fefo,
                quantidade=Decimal("7.000"),
                preco_unitario=prod_fefo.preco_venda,
                desconto=Decimal("0.00"),
            )
        try:
            VendaService.finalizar_venda(
                venda_id=venda3.id,
                deposito_id=dep_fefo.id,
                usuario=fefo.username,
                usar_lotes=True,
                gerar_conta_receber=False,
            )
        except Exception:
            pass
        fornecedor, _ = Fornecedor.objects.get_or_create(
            empresa=empresa,
            cpf_cnpj="73.621.701/0001-29",
            defaults={
                "razao_social": "Fornecedor XYZ",
                "tipo_pessoa": TipoPessoa.JURIDICA,
            },
        )
        try:
            NFeService.efetivar_importacao_nfe(
                empresa=empresa,
                payload={
                    "deposito_id": str(dep_nfe.id),
                    "numero_nfe": "12345",
                    "serie_nfe": "1",
                    "fornecedor": {"cnpj": fornecedor.documento_numerico, "nome": fornecedor.nome_exibicao},
                    "itens": [
                        {
                            "codigo_xml": "COD-XML-1",
                            "produto_id": str(insumo_nfe.id),
                            "fator_conversao": 2,
                            "qtd_xml": 3,
                            "preco_custo": 4.50,
                            "lote": {
                                "codigo": "LOTE-NFE-1",
                                "validade": str(date.today().replace(year=date.today().year + 1)),
                            },
                        }
                    ],
                },
                usuario=nfe_user.username,
            )
        except Exception:
            pass

        # Criação do Superusuário 'suporte'
        suporte_user, created_suporte = CustomUser.objects.get_or_create(
            username='suporte',
            empresa=empresa,
            defaults={
                'email': 'suporte@empresa.test',
                'first_name': 'Suporte',
                'last_name': 'Sistema',
                'cargo': TipoCargo.ADMIN,
                'is_superuser': True,
                'is_staff': True
            }
        )
        # Garante que a senha seja sempre 'suporte123', mesmo se o usuário já existir
        suporte_user.set_password('suporte123')
        suporte_user.save()
        
        if created_suporte:
            self.stdout.write(self.style.SUCCESS("Superusuário 'suporte' criado com senha 'suporte123'"))
        else:
            self.stdout.write(self.style.SUCCESS("Superusuário 'suporte' atualizado com senha 'suporte123'"))

        self.stdout.write(self.style.SUCCESS("Dados de cenários de teste persistidos"))
