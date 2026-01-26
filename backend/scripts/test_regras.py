import os
import django
import sys
from decimal import Decimal

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Produto, FichaTecnicaItem, TipoProduto, Categoria
from partners.models import Cliente
from sales.models import Venda, ItemVenda, StatusVenda
from sales.services import VendaService
from stock.models import Deposito, Saldo
from financial.models import ContaReceber, StatusConta, TipoPagamento

def testar_tudo():
    print("🧪 Iniciando Testes de Regras de Negócio...")
    
    # Busca empresa demo (criada no passo anterior)
    from tenant.models import Empresa
    empresa = Empresa.objects.first()
    if not empresa:
        print("❌ Erro: Empresa demo não encontrada. Rode o script de dados demo primeiro.")
        return

    # --- TESTE 1: Recálculo de Custos (BOM) ---
    print("\n1. Testando Recálculo de Custos (Ficha Técnica)...")
    pao = Produto.objects.get(nome='Pão de Hambúrguer', empresa=empresa)
    xburger = Produto.objects.get(nome='X-Burger Clássico', empresa=empresa)
    
    print(f"   Custo atual do Pão: R$ {pao.preco_custo}")
    print(f"   Custo atual do X-Burger: R$ {xburger.preco_custo}")
    
    # Altera custo do insumo
    pao.preco_custo = Decimal('5.00') # Dobrou o preço
    pao.save()
    
    xburger.refresh_from_db()
    print(f"   Novo custo do Pão: R$ {pao.preco_custo}")
    print(f"   >>> Novo custo do X-Burger (Automático): R$ {xburger.refresh_from_db() or xburger.preco_custo}")
    
    if xburger.preco_custo > Decimal('10.00'):
        print("   ✅ SUCESSO: Custo do produto composto atualizado via Signal.")
    else:
        print("   ❌ FALHA: O custo do pai não foi atualizado.")

    # --- TESTE 2: Limite de Crédito ---
    print("\n2. Testando Limite de Crédito...")
    cliente, _ = Cliente.objects.get_or_create(
        nome="João Teste",
        empresa=empresa,
        defaults={'cpf_cnpj': '111.111.111-11', 'limite_credito': Decimal('100.00')}
    )
    cliente.limite_credito = Decimal('100.00')
    cliente.saldo_devedor = Decimal('0.00')
    cliente.save()

    deposito = Deposito.objects.filter(empresa=empresa).first()
    
    # Cria uma venda de R$ 150 (Acima do limite de R$ 100)
    venda_cara = Venda.objects.create(empresa=empresa, cliente=cliente, total_liquido=Decimal('150.00'))
    ItemVenda.objects.create(venda=venda_cara, produto=xburger, quantidade=Decimal('5'), preco_unitario=Decimal('30.00'))

    print(f"   Tentando finalizar venda de R$ 150 para cliente com limite de R$ 100...")
    try:
        VendaService.finalizar_venda(venda_cara.id, deposito.id, usuario='admin', tipo_pagamento='CONTA_CLIENTE')
        print("   ❌ FALHA: O sistema permitiu uma venda acima do limite!")
    except Exception as e:
        print(f"   ✅ SUCESSO: Venda bloqueada. Erro: {str(e)[:50]}...")

    # --- TESTE 3: Atualização de Saldo Devedor ---
    print("\n3. Testando Saldo Devedor Financeiro...")
    venda_ok = Venda.objects.create(empresa=empresa, cliente=cliente, total_liquido=Decimal('50.00'))
    ItemVenda.objects.create(venda=venda_ok, produto=xburger, quantidade=Decimal('2'), preco_unitario=Decimal('25.00'))
    
    # Finaliza venda dentro do limite
    VendaService.finalizar_venda(venda_ok.id, deposito.id, usuario='admin', tipo_pagamento='CONTA_CLIENTE')
    
    cliente.refresh_from_db()
    print(f"   Venda de R$ 50 finalizada.")
    print(f"   >>> Saldo devedor do cliente (Automático): R$ {cliente.saldo_devedor}")
    
    if cliente.saldo_devedor == Decimal('50.00'):
        print("   ✅ SUCESSO: Saldo devedor atualizado via Financeiro.")
    else:
        print(f"   ❌ FALHA: Saldo devedor esperado 50.00, atual {cliente.saldo_devedor}.")

    print("\n🏁 Testes concluídos!")

if __name__ == '__main__':
    testar_tudo()
