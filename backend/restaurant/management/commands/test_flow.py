from django.core.management.base import BaseCommand
from decimal import Decimal
from restaurant.models import Mesa, StatusMesa
from catalog.models import Produto, Categoria
from stock.models import Deposito, Saldo as Estoque, Lote
from sales.models import Venda, StatusVenda
from financial.models import ContaReceber, Caixa
from restaurant.services import RestaurantService
from authentication.models import CustomUser
from datetime import date, timedelta
from tenant.models import Empresa
from financial.services import CaixaService

class Command(BaseCommand):
    help = 'Testa fluxo completo de venda'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INICIANDO TESTE DE FLUXO COMPLETO ---")
        
        # 1. Setup Inicial (Empresa, User, Deposito, Produto)
        user = CustomUser.objects.first() # Pega o primeiro user (admin)
        empresa = user.empresa
        
        self.stdout.write(f"Usuário: {user.username}, Empresa: {empresa.nome_fantasia}")
        
        # 1.1 CAIXA PDV: Abrir Caixa
        caixa, _ = Caixa.objects.get_or_create(
            empresa=empresa,
            nome="Caixa Teste Flow"
        )
        self.stdout.write(f"Caixa: {caixa.nome}")
        
        sessao = CaixaService.get_sessao_aberta(user)
        if not sessao:
            self.stdout.write("Abrindo caixa...")
            sessao = CaixaService.abrir_caixa(caixa.id, user, Decimal('100.00'))
        else:
            self.stdout.write(f"Caixa já aberto: Sessão #{sessao.id}")

        deposito, _ = Deposito.objects.get_or_create(
            empresa=empresa,
            nome="Deposito Teste",
            defaults={'is_padrao': True}
        )
        
        categoria, _ = Categoria.objects.get_or_create(
            empresa=empresa,
            nome="Categoria Teste"
        )
        
        produto, _ = Produto.objects.get_or_create(
            empresa=empresa,
            nome="Produto Teste Flow",
            defaults={
                'codigo_barras': 'EAN-TEST-FLOW-999',
                'preco_venda': Decimal('50.00'),
            'preco_custo': Decimal('20.00'),
            'categoria': categoria,
            'permite_venda_sem_estoque': False
        }
        )
        
        # Ajusta estoque (Saldo Geral)
        estoque, _ = Estoque.objects.get_or_create(
            empresa=empresa,
            produto=produto,
            deposito=deposito,
            defaults={'quantidade': Decimal('0')}
        )
        estoque.quantidade = Decimal('100')
        estoque.save()
        
        # Lotes desativados no settings.py, não precisamos criar Lote.
        # O sistema deve usar apenas o Saldo.
            
        self.stdout.write(f"Produto: {produto.nome}, Estoque: {estoque.quantidade}")
        
        # 2. Mesa
        mesa, _ = Mesa.objects.get_or_create(
            empresa=empresa,
            numero=999,
            defaults={'capacidade': 4}
        )
        
        # Garante mesa livre
        if mesa.status != StatusMesa.LIVRE:
            self.stdout.write(f"Mesa {mesa.numero} estava {mesa.status}. Liberando...")
            if mesa.venda_atual:
                mesa.venda_atual.status = StatusVenda.CANCELADA
                mesa.venda_atual.save()
            mesa.liberar()
        
        self.stdout.write(f"Mesa {mesa.numero} Status: {mesa.status}")
        
        # 3. Abrir Mesa
        self.stdout.write(">>> Abrindo Mesa...")
        venda = RestaurantService.abrir_mesa(mesa.id, user)
        self.stdout.write(f"Venda Criada: #{venda.numero}, Status: {venda.status}")
        
        # 4. Adicionar Item
        self.stdout.write(">>> Adicionando Item...")
        item = RestaurantService.adicionar_item_mesa(
            mesa_id=mesa.id,
            produto_id=produto.id,
            quantidade=2
        )
        self.stdout.write(f"Item Adicionado: {item.produto.nome} x {item.quantidade} = {item.subtotal}")
        
        # Recarrega venda
        venda.refresh_from_db()
        self.stdout.write(f"Total Venda: {venda.total_liquido}")
        
        # 5. Fechar Mesa
        self.stdout.write(">>> Fechando Mesa...")
        try:
            venda_finalizada = RestaurantService.fechar_mesa(
                mesa_id=mesa.id,
                deposito_id=deposito.id,
                tipo_pagamento='DINHEIRO',
                usuario=user
            )
            self.stdout.write(self.style.SUCCESS(f"Venda Finalizada! Status: {venda_finalizada.status}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO AO FECHAR: {e}"))
            import traceback
            traceback.print_exc()
            return

        # 6. Verificar Estoque
        estoque.refresh_from_db()
        self.stdout.write(f"Estoque Final: {estoque.quantidade} (Esperado: 98)")
        if estoque.quantidade == 98:
            self.stdout.write(self.style.SUCCESS("OK: Estoque baixado corretamente."))
        else:
            self.stdout.write(self.style.ERROR("FALHA: Estoque incorreto."))
            
        # 7. Verificar Financeiro
        contas = ContaReceber.objects.filter(venda=venda_finalizada)
        self.stdout.write(f"Contas a Receber geradas: {contas.count()}")
        if contas.exists():
            self.stdout.write(f"Conta: {contas.first().valor_total} - {contas.first().status}")
            self.stdout.write(self.style.SUCCESS("OK: Financeiro gerado."))
        else:
            self.stdout.write(self.style.ERROR("FALHA: Nenhuma conta a receber gerada."))

        self.stdout.write("--- TESTE CONCLUÍDO ---")