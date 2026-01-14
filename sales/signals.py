"""
Signals para o módulo de vendas.
Automatiza cálculos e manutenção de dados derivados.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from decimal import Decimal

from .models import ItemVenda, Venda


@receiver(post_save, sender=ItemVenda)
@receiver(post_delete, sender=ItemVenda)
def recalcular_totais_venda(sender, instance, **kwargs):
    """
    Recalcula os totais da venda quando um item é salvo ou deletado.
    
    Atualiza:
    - total_bruto: Soma de (quantidade × preço unitário + complementos) de todos os itens
    - total_desconto: Soma de descontos de todos os itens
    - total_liquido: total_bruto - total_desconto
    
    IMPORTANTE: Este signal garante que os totais estejam sempre
    sincronizados com os itens, incluindo complementos.
    """
    venda = instance.venda
    
    # Calcula totais agregando os itens
    # Nota: subtotal do item já inclui complementos (calculado no signal abaixo)
    agregacao = venda.itens.aggregate(
        total_bruto=Sum(F('quantidade') * F('preco_unitario')),
        total_desconto=Sum('desconto'),
        total_subtotais=Sum('subtotal')  # Já inclui complementos
    )
    
    # Extrai valores (ou 0 se não houver itens)
    total_bruto_itens = agregacao['total_bruto'] or Decimal('0.00')
    total_desconto = agregacao['total_desconto'] or Decimal('0.00')
    
    # Soma complementos ao total bruto
    from sales.models import ItemVendaComplemento
    total_complementos = ItemVendaComplemento.objects.filter(
        item_pai__venda=venda
    ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    
    total_bruto = total_bruto_itens + total_complementos
    total_liquido = total_bruto - total_desconto
    
    # Atualiza venda (apenas se valores mudaram)
    if (venda.total_bruto != total_bruto or 
        venda.total_desconto != total_desconto or 
        venda.total_liquido != total_liquido):
        
        venda.total_bruto = total_bruto
        venda.total_desconto = total_desconto
        venda.total_liquido = total_liquido
        
        # Usa update_fields para evitar triggers desnecessários
        venda.save(update_fields=['total_bruto', 'total_desconto', 'total_liquido', 'updated_at'])


# Signal para recalcular subtotal do item quando complementos mudam
@receiver(post_save, sender='sales.ItemVendaComplemento')
@receiver(post_delete, sender='sales.ItemVendaComplemento')
def recalcular_subtotal_item(sender, instance, **kwargs):
    """
    Recalcula subtotal do item quando seus complementos mudam.
    
    Subtotal do item = (quantidade × preço) + total_complementos - desconto
    """
    item = instance.item_pai
    
    # Calcula total dos complementos
    total_complementos = item.total_complementos
    
    # Calcula novo subtotal
    base = item.quantidade * item.preco_unitario
    novo_subtotal = base + total_complementos - item.desconto
    
    # Atualiza apenas se mudou
    if item.subtotal != novo_subtotal:
        item.subtotal = novo_subtotal
        item.save(update_fields=['subtotal', 'updated_at'])

