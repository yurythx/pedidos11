from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from catalog.models import FichaTecnicaItem, Produto, TipoProduto

@receiver([post_save, post_delete], sender=FichaTecnicaItem)
def atualizar_custo_produto_composto(sender, instance, **kwargs):
    """
    Atualiza o preço de custo do produto pai (COMPOSTO) 
    sempre que um item da sua ficha técnica for alterado ou removido.
    """
    produto_pai = instance.produto_pai
    
    # Calcula a soma dos custos de todos os componentes
    # custo_calculado é uma property, então precisamos somar manualmente ou via extra/annotate
    itens = FichaTecnicaItem.objects.filter(produto_pai=produto_pai)
    
    novo_custo = Decimal('0.00')
    for item in itens:
        novo_custo += item.custo_calculado
        
    # Atualiza o produto pai
    if produto_pai.preco_custo != novo_custo:
        produto_pai.preco_custo = novo_custo
        produto_pai.save(update_fields=['preco_custo', 'updated_at'])

@receiver(post_save, sender=Produto)
def replicar_custo_para_compostos(sender, instance, **kwargs):
    """
    Se o preço de custo de um INSUMO ou FINAL mudar, 
    precisamos atualizar todos os produtos COMPOSTOS que o utilizam.
    """
    # Evita recursão infinita e processamento desnecessário
    if hasattr(instance, '_updating_custo'):
        return

    # Busca todas as fichas técnicas onde este produto é componente
    fichas = FichaTecnicaItem.objects.filter(componente=instance)
    
    produtos_afetados = set()
    for ficha in fichas:
        produtos_afetados.add(ficha.produto_pai)
        
    for pai in produtos_afetados:
        # Força o recálculo do custo do pai
        novo_custo = Decimal('0.00')
        for item in pai.ficha_tecnica.all():
            novo_custo += item.custo_calculado
        
        if pai.preco_custo != novo_custo:
            pai._updating_custo = True
            pai.preco_custo = novo_custo
            pai.save(update_fields=['preco_custo', 'updated_at'])
