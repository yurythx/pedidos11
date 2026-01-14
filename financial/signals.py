"""
Signals para o módulo financeiro.
Automatiza geração de contas a receber quando vendas são finalizadas.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from sales.models import StatusVenda, Venda
from .services import FinanceiroService



@receiver(post_save, sender=Venda)
def gerar_conta_receber_apos_venda(sender, instance, created, **kwargs):
    """
    Gera conta a receber automaticamente quando uma venda é finalizada.
    
    Gatilho: Venda.status muda para FINALIZADA
    Ação: Cria ContaReceber à vista (1 parcela, 30 dias)
    
    NOTA: Para vendas parceladas, use FinanceiroService.gerar_conta_receber_venda
    com número de parcelas customizado.
    """
    # Só age se status mudou para FINALIZADA
    if instance.status != StatusVenda.FINALIZADA:
        return
    
    # Evita duplicação (se já tem contas, não cria novamente)
    if instance.contas_receber.exists():
        return
    
    # Gera conta a receber à vista
    try:
        FinanceiroService.gerar_conta_receber_venda(
            venda=instance,
            parcelas=1,
            dias_vencimento=30
        )
    except Exception as e:
        # Log do erro (não deve quebrar o fluxo de finalização da venda)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Erro ao gerar conta a receber para venda #{instance.numero}: {str(e)}"
        )
