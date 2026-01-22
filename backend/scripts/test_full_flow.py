import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, r'C:\Users\yuri.menezes\Desktop\Projetos\pedidos11\backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from restaurant.models import Mesa, StatusMesa
from catalog.models import Produto, Deposito, Estoque, Categoria
from sales.models import Venda, StatusVenda
from finance.models import ContaReceber
from restaurant.services import RestaurantService
from sales.services import VendaService
from core.models import Empresa, CustomUser

def run():
    print("--- INICIANDO TESTE DE FLUXO COMPLETO ---")
    
    # 1. Setup Inicial (Empresa, User, Deposito, Produto)
    user = CustomUser.objects.first() # Pega o primeiro user (admin)
    empresa = user.empresa
    
    print(f"Usuário: {user.username}, Empresa: {empresa.nome}")
    
    deposito, _ = Deposito.objects.get_or_create(
        empresa=empresa,
        nome="Deposito Teste",
        defaults={'padrao': True}
    )
    
    categoria, _ = Categoria.objects.get_or_create(
        empresa=empresa,
        nome="Categoria Teste"
    )
    
    produto, _ = Produto.objects.get_or_create(
        empresa=empresa,
        nome="Produto Teste Flow",
        defaults={
            'preco_venda': Decimal('50.00'),
            'preco_custo': Decimal('20.00'),
            'categoria': categoria,
            'controlar_estoque': True
        }
    )
    
    # Ajusta estoque
    estoque, _ = Estoque.objects.get_or_create(
        produto=produto,
        deposito=deposito,
        defaults={'quantidade': Decimal('0')}
    )
    estoque.quantidade = Decimal('100')
    estoque.save()
    
    print(f"Produto: {produto.nome}, Estoque: {estoque.quantidade}")
    
    # 2. Mesa
    mesa, _ = Mesa.objects.get_or_create(
        empresa=empresa,
        numero=999,
        defaults={'capacidade': 4}
    )
    
    # Garante mesa livre
    if mesa.status != StatusMesa.LIVRE:
        print(f"Mesa {mesa.numero} estava {mesa.status}. Liberando...")
        if mesa.venda_atual:
            mesa.venda_atual.status = StatusVenda.CANCELADA
            mesa.venda_atual.save()
        mesa.liberar()
    
    print(f"Mesa {mesa.numero} Status: {mesa.status}")
    
    # 3. Abrir Mesa
    print(">>> Abrindo Mesa...")
    venda = RestaurantService.abrir_mesa(mesa.id, user)
    print(f"Venda Criada: #{venda.numero}, Status: {venda.status}")
    
    # 4. Adicionar Item
    print(">>> Adicionando Item...")
    item = RestaurantService.adicionar_item_mesa(
        mesa_id=mesa.id,
        produto_id=produto.id,
        quantidade=2
    )
    print(f"Item Adicionado: {item.produto.nome} x {item.quantidade} = {item.subtotal}")
    
    # Recarrega venda
    venda.refresh_from_db()
    print(f"Total Venda: {venda.total_liquido}")
    
    # 5. Fechar Mesa
    print(">>> Fechando Mesa...")
    try:
        venda_finalizada = RestaurantService.fechar_mesa(
            mesa_id=mesa.id,
            deposito_id=deposito.id,
            tipo_pagamento='DINHEIRO'
        )
        print(f"Venda Finalizada! Status: {venda_finalizada.status}")
    except Exception as e:
        print(f"ERRO AO FECHAR: {e}")
        return

    # 6. Verificar Estoque
    estoque.refresh_from_db()
    print(f"Estoque Final: {estoque.quantidade} (Esperado: 98)")
    if estoque.quantidade == 98:
        print("OK: Estoque baixado corretamente.")
    else:
        print("FALHA: Estoque incorreto.")
        
    # 7. Verificar Financeiro
    contas = ContaReceber.objects.filter(venda=venda_finalizada)
    print(f"Contas a Receber geradas: {contas.count()}")
    if contas.exists():
        print(f"Conta: {contas.first().valor} - {contas.first().status}")
        print("OK: Financeiro gerado.")
    else:
        print("FALHA: Nenhuma conta a receber gerada.")

    print("--- TESTE CONCLUÍDO ---")

if __name__ == "__main__":
    run()