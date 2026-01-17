"""
Service Layer para o módulo financeiro.
Orquestra regras de negócio e integrações.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from .models import ContaReceber, ContaPagar, StatusConta


class FinanceiroService:
    """
    Service responsável por operações financeiras.
    
    Responsabilidades:
    - Gerar contas a receber a partir de vendas
    - Baixar pagamentos
    - Calcular juros e multas
    - Gerar parcelas
    """
    
    @staticmethod
    @transaction.atomic
    def gerar_conta_receber_venda(venda, parcelas=1, dias_vencimento=30):
        """
        Gera contas a receber a partir de uma venda finalizada.
        
        Args:
            venda: Instância de sales.Venda
            parcelas: Número de parcelas (default: 1 - à vista)
            dias_vencimento: Dias até vencimento (default: 30)
        
        Returns:
            list: Lista de ContaReceber criadas
        
        Raises:
            ValidationError: Se venda não estiver finalizada
        """
        from sales.models import StatusVenda
        
        # Valida status da venda
        if venda.status != StatusVenda.FINALIZADA:
            raise ValidationError(
                f"Venda #{venda.numero} deve estar FINALIZADA para gerar contas a receber"
            )
        
        # Verifica se já existem contas para esta venda
        if venda.contas_receber.exists():
            return list(venda.contas_receber.all())
        
        # Calcula valor de cada parcela
        valor_parcela = venda.total_liquido / parcelas
        valor_parcela = valor_parcela.quantize(Decimal('0.01'))
        
        # Ajusta última parcela para compensar arredondamento
        valor_total_parcelas = valor_parcela * (parcelas - 1)
        valor_ultima_parcela = venda.total_liquido - valor_total_parcelas
        
        # Cria contas
        contas_criadas = []
        data_base = venda.data_finalizacao.date()
        
        for i in range(parcelas):
            # Calcula vencimento (parcelas mensais)
            dias_adicionar = dias_vencimento + (i * 30)  # 30, 60, 90 dias...
            data_vencimento = data_base + timedelta(days=dias_adicionar)
            
            # Valor desta parcela
            valor = valor_ultima_parcela if i == parcelas - 1 else valor_parcela
            
            # Descrição
            if parcelas == 1:
                descricao = f"Venda #{venda.numero} - À vista"
            else:
                descricao = f"Venda #{venda.numero} - Parcela {i+1}/{parcelas}"
            
            # Cria conta
            conta = ContaReceber.objects.create(
                empresa=venda.empresa,
                venda=venda,
                cliente=venda.cliente,
                descricao=descricao,
                valor_original=valor,
                data_emissao=data_base,
                data_vencimento=data_vencimento,
                status=StatusConta.PENDENTE
            )
            
            contas_criadas.append(conta)
        
        return contas_criadas
    
    @staticmethod
    @transaction.atomic
    def baixar_conta_receber(conta_id, data_pagamento=None, tipo_pagamento=None,
                            valor_juros=None, valor_multa=None, valor_desconto=None):
        """
        Baixa (marca como paga) uma conta a receber.
        
        Args:
            conta_id: UUID da conta
            data_pagamento: Data do pagamento (None = hoje)
            tipo_pagamento: Forma de pagamento
            valor_juros: Juros cobrados (None = calcular automaticamente)
            valor_multa: Multa cobrada (None = calcular automaticamente)
            valor_desconto: Desconto concedido
        
        Returns:
            ContaReceber: Conta atualizada
        """
        try:
            conta = ContaReceber.objects.select_for_update().get(id=conta_id)
        except ContaReceber.DoesNotExist:
            raise ValidationError(f"Conta a receber com ID {conta_id} não encontrada")
        
        # Valida status
        if conta.status == StatusConta.PAGA:
            raise ValidationError(f"Conta #{conta.id} já está paga")
        
        if conta.status == StatusConta.CANCELADA:
            raise ValidationError(f"Conta #{conta.id} está cancelada")
        
        # Data de pagamento
        if data_pagamento is None:
            data_pagamento = timezone.now().date()
        
        # Calcula juros/multas automaticamente se não fornecidos
        if conta.esta_vencida:
            dias_atraso = conta.dias_atraso
            
            # Juros: 0.033% ao dia (1% ao mês)
            if valor_juros is None:
                valor_juros = conta.valor_original * Decimal('0.00033') * dias_atraso
                valor_juros = valor_juros.quantize(Decimal('0.01'))
            
            # Multa: 2% sobre valor original
            if valor_multa is None:
                valor_multa = conta.valor_original * Decimal('0.02')
                valor_multa = valor_multa.quantize(Decimal('0.01'))
        else:
            valor_juros = valor_juros or Decimal('0.00')
            valor_multa = valor_multa or Decimal('0.00')
        
        # Desconto
        valor_desconto = valor_desconto or Decimal('0.00')
        
        # Atualiza conta
        conta.data_pagamento = data_pagamento
        conta.tipo_pagamento = tipo_pagamento
        conta.valor_juros = valor_juros
        conta.valor_multa = valor_multa
        conta.valor_desconto = valor_desconto
        conta.status = StatusConta.PAGA
        conta.save()
        
        return conta
    
    @staticmethod
    @transaction.atomic
    def baixar_conta_pagar(conta_id, data_pagamento=None, tipo_pagamento=None,
                          valor_juros=None, valor_multa=None, valor_desconto=None):
        """
        Baixa (marca como paga) uma conta a pagar.
        
        Mesma lógica de baixar_conta_receber adaptada para despesas.
        """
        try:
            conta = ContaPagar.objects.select_for_update().get(id=conta_id)
        except ContaPagar.DoesNotExist:
            raise ValidationError(f"Conta a pagar com ID {conta_id} não encontrada")
        
        if conta.status == StatusConta.PAGA:
            raise ValidationError(f"Conta #{conta.id} já está paga")
        
        if conta.status == StatusConta.CANCELADA:
            raise ValidationError(f"Conta #{conta.id} está cancelada")
        
        if data_pagamento is None:
            data_pagamento = timezone.now().date()
        
        # Calcula juros/multas se vencida
        if conta.esta_vencida:
            dias_atraso = conta.dias_atraso
            
            if valor_juros is None:
                valor_juros = conta.valor_original * Decimal('0.00033') * dias_atraso
                valor_juros = valor_juros.quantize(Decimal('0.01'))
            
            if valor_multa is None:
                valor_multa = conta.valor_original * Decimal('0.02')
                valor_multa = valor_multa.quantize(Decimal('0.01'))
        else:
            valor_juros = valor_juros or Decimal('0.00')
            valor_multa = valor_multa or Decimal('0.00')
        
        valor_desconto = valor_desconto or Decimal('0.00')
        
        # Atualiza conta
        conta.data_pagamento = data_pagamento
        conta.tipo_pagamento = tipo_pagamento
        conta.valor_juros = valor_juros
        conta.valor_multa = valor_multa
        conta.valor_desconto = valor_desconto
        conta.status = StatusConta.PAGA
        conta.save()
        
        return conta
    
    @staticmethod
    def atualizar_status_vencidas():
        """
        Atualiza status de contas pendentes que venceram.
        
        Deve ser executado periodicamente (ex: task agendada, cron).
        
        Returns:
            dict: {'contas_receber': int, 'contas_pagar': int}
        """
        hoje = timezone.now().date()
        
        # Atualiza contas a receber
        cr_atualizadas = ContaReceber.objects.filter(
            status=StatusConta.PENDENTE,
            data_vencimento__lt=hoje
        ).update(status=StatusConta.VENCIDA)
        
        # Atualiza contas a pagar
        cp_atualizadas = ContaPagar.objects.filter(
            status=StatusConta.PENDENTE,
            data_vencimento__lt=hoje
        ).update(status=StatusConta.VENCIDA)
        
        return {
            'contas_receber': cr_atualizadas,
            'contas_pagar': cp_atualizadas
        }
