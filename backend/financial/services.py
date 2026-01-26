from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Caixa, SessaoCaixa, MovimentoCaixa, TipoMovimentoCaixa, StatusSessao,
    ContaReceber, StatusConta, TipoPagamento
)

class CaixaService:
    @staticmethod
    def get_sessao_aberta(usuario):
        """Retorna sessão aberta para o usuário, se houver."""
        return SessaoCaixa.objects.filter(
            operador=usuario,
            status=StatusSessao.ABERTA
        ).first()

    @staticmethod
    @transaction.atomic
    def abrir_caixa(caixa_id, usuario, saldo_inicial=Decimal('0.00')):
        """Abre uma nova sessão de caixa."""
        # Verifica se usuário já tem caixa aberto
        if CaixaService.get_sessao_aberta(usuario):
            raise ValidationError("Você já possui um caixa aberto.")
        
        # Verifica se caixa físico já está aberto por outro
        if SessaoCaixa.objects.filter(caixa_id=caixa_id, status=StatusSessao.ABERTA).exists():
            raise ValidationError("Este caixa já está aberto por outro operador.")
            
        # Valida se caixa pertence à empresa do usuário
        caixa = Caixa.objects.get(id=caixa_id)
        if caixa.empresa != usuario.empresa:
            raise ValidationError("Caixa não pertence à sua empresa.")

        sessao = SessaoCaixa.objects.create(
            empresa=usuario.empresa,
            caixa_id=caixa_id,
            operador=usuario,
            saldo_inicial=saldo_inicial,
            status=StatusSessao.ABERTA
        )
        return sessao

    @staticmethod
    @transaction.atomic
    def fechar_caixa(sessao_id, saldo_informado):
        """Fecha a sessão de caixa."""
        try:
            sessao = SessaoCaixa.objects.get(id=sessao_id)
        except SessaoCaixa.DoesNotExist:
            raise ValidationError("Sessão não encontrada.")
            
        if sessao.status != StatusSessao.ABERTA:
            raise ValidationError("Caixa já está fechado.")
            
        # Calcula totais
        movimentos = sessao.movimentos.all()
        total_suprimentos = sum(m.valor for m in movimentos if m.tipo == TipoMovimentoCaixa.SUPRIMENTO)
        total_sangrias = sum(m.valor for m in movimentos if m.tipo == TipoMovimentoCaixa.SANGRIA)
        total_vendas = sum(m.valor for m in movimentos if m.tipo == TipoMovimentoCaixa.VENDA)
        
        saldo_calculado = sessao.saldo_inicial + total_suprimentos + total_vendas - total_sangrias
        
        sessao.saldo_final_informado = saldo_informado
        sessao.saldo_final_calculado = saldo_calculado
        sessao.data_fechamento = timezone.now()
        sessao.status = StatusSessao.FECHADA
        sessao.save()
        
        return sessao

    @staticmethod
    def obter_resumo(sessao):
        """Retorna resumo detalhado da sessão para fechamento."""
        movimentos = sessao.movimentos.select_related('venda_origem').all()
        
        # Totais por tipo de movimento
        total_suprimentos = sum(m.valor for m in movimentos if m.tipo == TipoMovimentoCaixa.SUPRIMENTO)
        total_sangrias = sum(m.valor for m in movimentos if m.tipo == TipoMovimentoCaixa.SANGRIA)
        
        # Totais por forma de pagamento (Vendas)
        vendas = [m.venda_origem for m in movimentos if m.tipo == TipoMovimentoCaixa.VENDA and m.venda_origem]
        
        resumo_vendas = {
            'DINHEIRO': Decimal('0.00'),
            'PIX': Decimal('0.00'),
            'CARTAO_DEBITO': Decimal('0.00'),
            'CARTAO_CREDITO': Decimal('0.00'),
            'OUTROS': Decimal('0.00')
        }
        
        total_vendas_geral = Decimal('0.00')
        
        for v in vendas:
            valor = v.total_liquido
            total_vendas_geral += valor
            tipo = v.tipo_pagamento or 'OUTROS'
            if tipo in resumo_vendas:
                resumo_vendas[tipo] += valor
            else:
                resumo_vendas['OUTROS'] += valor
                
        # Saldo em Dinheiro (Gaveta)
        # = Inicial + Suprimentos + Vendas(Dinheiro) - Sangrias
        saldo_dinheiro = sessao.saldo_inicial + total_suprimentos + resumo_vendas['DINHEIRO'] - total_sangrias
        
        return {
            'saldo_inicial': sessao.saldo_inicial,
            'total_suprimentos': total_suprimentos,
            'total_sangrias': total_sangrias,
            'total_vendas': total_vendas_geral,
            'vendas_por_tipo': resumo_vendas,
            'saldo_final_dinheiro': saldo_dinheiro, # Esperado na gaveta
            'status': sessao.status
        }

    @staticmethod
    def registrar_movimento(sessao, tipo, valor, descricao, venda=None):
        """Registra movimentação manual (suprimento/sangria) ou venda."""
        if sessao.status != StatusSessao.ABERTA:
            raise ValidationError("Caixa fechado.")
            
        MovimentoCaixa.objects.create(
            empresa=sessao.empresa,
            sessao=sessao,
            tipo=tipo,
            valor=valor,
            descricao=descricao,
            venda_origem=venda
        )

class FinanceiroService:
    @staticmethod
    def gerar_conta_receber_venda(venda, parcelas=1, dias_vencimento=0):
        """Gera conta a receber para uma venda finalizada."""
        # Se já existe, não gera
        if ContaReceber.objects.filter(venda=venda).exists():
            return
            
        # Mapeia tipo de pagamento
        tipo_map = {
            'DINHEIRO': TipoPagamento.DINHEIRO,
            'PIX': TipoPagamento.PIX,
            'CARTAO_DEBITO': TipoPagamento.CARTAO_DEBITO,
            'CARTAO_CREDITO': TipoPagamento.CARTAO_CREDITO,
            'CONTA_CLIENTE': TipoPagamento.CONTA_CLIENTE,
        }
        
        # Vou atualizar o Enum de TipoPagamento no financial/models.py também para ter CONTA_CLIENTE
        tipo = tipo_map.get(venda.tipo_pagamento, TipoPagamento.DINHEIRO)
        
        # Define status inicial (paga se for dinheiro/pix/debito)
        pagos_imediato = [TipoPagamento.DINHEIRO, TipoPagamento.PIX, TipoPagamento.CARTAO_DEBITO]
        status_conta = StatusConta.PAGA if tipo in pagos_imediato and tipo != TipoPagamento.CONTA_CLIENTE else StatusConta.PENDENTE
        
        # Se dias_vencimento > 0, usa. Senão hoje.
        if dias_vencimento > 0:
            data_vencimento = timezone.now().date() + timezone.timedelta(days=dias_vencimento)
        else:
            data_vencimento = timezone.now().date()
            
        data_pagamento = timezone.now().date() if status_conta == StatusConta.PAGA else None
        
        ContaReceber.objects.create(
            empresa=venda.empresa,
            venda=venda,
            cliente=venda.cliente, # Pode ser None
            descricao=f"Venda #{venda.numero}",
            valor_original=venda.total_liquido,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            status=status_conta,
            tipo_pagamento=tipo
        )
