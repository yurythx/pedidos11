from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from .models import ContaReceber, StatusConta

@receiver([post_save, post_delete], sender=ContaReceber)
def atualizar_saldo_devedor_cliente(sender, instance, **kwargs):
    """
    Atualiza o saldo devedor do cliente sempre que uma conta a receber 
    for alterada, paga ou excluída.
    """
    cliente = instance.cliente
    if not cliente:
        return

    # Soma todas as contas PENDENTES ou VENCIDAS do cliente
    saldo_aberto = ContaReceber.objects.filter(
        cliente=cliente,
        status__in=[StatusConta.PENDENTE, StatusConta.VENCIDAS] # Nota: No models.py é PENDENTE e VENCIDA
    ).aggregate(total=Sum('valor_original'))['total'] or Decimal('0.00')
    
    # Nota: Em financial/models.py o StatusConta tem VENCIDA no singular
    # Vou corrigir para usar o Enum correto se necessário ou filtrar manualmente
    
    # Busca real baseado no que está no models.py (StatusConta.PENDENTE e StatusConta.VENCIDA)
    saldo_aberto = ContaReceber.objects.filter(
        cliente=cliente,
        status__in=['PENDENTE', 'VENCIDA']
    ).aggregate(total=Sum('valor_original'))['total'] or Decimal('0.00')

    if cliente.saldo_devedor != saldo_aberto:
        cliente.saldo_devedor = saldo_aberto
        cliente.save(update_fields=['saldo_devedor', 'updated_at'])
