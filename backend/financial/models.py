"""
Models financeiros para Projeto Nix.
Gestão de contas a pagar e receber.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from core.models import TenantModel


class StatusConta(models.TextChoices):
    """Status de uma conta a pagar/receber."""
    PENDENTE = 'PENDENTE', 'Pendente'
    PAGA = 'PAGA', 'Paga'
    CANCELADA = 'CANCELADA', 'Cancelada'
    VENCIDA = 'VENCIDA', 'Vencida'


class TipoPagamento(models.TextChoices):
    """Tipos de pagamento."""
    DINHEIRO = 'DINHEIRO', 'Dinheiro'
    PIX = 'PIX', 'PIX'
    CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
    BOLETO = 'BOLETO', 'Boleto'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência Bancária'
    CHEQUE = 'CHEQUE', 'Cheque'


class ContaReceber(TenantModel):
    """
    Conta a receber (receitas).
    
    Representa valores a receber de clientes, geralmente originados
    de vendas realizadas.
    
    Responsabilidades:
    - Registrar valores a receber
    - Controlar vencimentos
    - Registrar pagamentos
    - Calcular juros/multas por atraso
    """
    
    # Origem (geralmente uma venda)
    venda = models.ForeignKey(
        'sales.Venda',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='contas_receber',
        verbose_name='Venda',
        help_text='Venda que originou esta conta (opcional)'
    )
    
    cliente = models.ForeignKey(
        'partners.Cliente',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='contas_receber',
        verbose_name='Cliente',
        help_text='Cliente responsável pelo pagamento'
    )
    
    # Descrição
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição',
        help_text='Descrição da conta a receber'
    )
    
    # Valores
    valor_original = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Original',
        help_text='Valor original da conta'
    )
    
    valor_juros = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Juros',
        help_text='Valor de juros aplicados'
    )
    
    valor_multa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Multa',
        help_text='Valor de multa aplicada'
    )
    
    valor_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto',
        help_text='Valor de desconto concedido'
    )
    
    # Datas
    data_emissao = models.DateField(
        default=timezone.now,
        verbose_name='Data de Emissão',
        help_text='Data de emissão da conta'
    )
    
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento',
        help_text='Data de vencimento da conta',
        db_index=True
    )
    
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Pagamento',
        help_text='Data em que foi paga (null se não paga)'
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusConta.choices,
        default=StatusConta.PENDENTE,
        verbose_name='Status',
        help_text='Status atual da conta',
        db_index=True
    )
    
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TipoPagamento.choices,
        null=True,
        blank=True,
        verbose_name='Tipo de Pagamento',
        help_text='Forma de pagamento utilizada'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas sobre a conta'
    )
    
    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['data_vencimento', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'data_vencimento']),
            models.Index(fields=['cliente', 'status']),
            models.Index(fields=['venda']),
        ]
    
    def __str__(self):
        """Representação amigável da conta."""
        cliente_info = f" - {self.cliente.nome}" if self.cliente else ""
        return f"CR #{self.id}{cliente_info} - R$ {self.valor_total} (Venc: {self.data_vencimento})"
    
    @property
    def valor_total(self):
        """
        Calcula valor total da conta.
        
        Returns:
            Decimal: valor_original + juros + multa - desconto
        """
        return (
            self.valor_original + 
            self.valor_juros + 
            self.valor_multa - 
            self.valor_desconto
        )
    
    @property
    def esta_vencida(self):
        """
        Verifica se a conta está vencida.
        
        Returns:
            bool: True se vencida e não paga
        """
        if self.status == StatusConta.PAGA:
            return False
        return timezone.now().date() > self.data_vencimento
    
    @property
    def dias_atraso(self):
        """
        Calcula dias de atraso.
        
        Returns:
            int: Número de dias de atraso (0 se não vencida)
        """
        if not self.esta_vencida:
            return 0
        return (timezone.now().date() - self.data_vencimento).days
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Data vencimento não pode ser menor que emissão
        if self.data_vencimento < self.data_emissao:
            raise ValidationError({
                'data_vencimento': 'Data de vencimento não pode ser anterior à emissão'
            })
        
        # Se paga, data_pagamento é obrigatória
        if self.status == StatusConta.PAGA and not self.data_pagamento:
            raise ValidationError({
                'data_pagamento': 'Data de pagamento é obrigatória para contas pagas'
            })


class ContaPagar(TenantModel):
    """
    Conta a pagar (despesas).
    
    Representa valores a pagar a fornecedores, geralmente originados
    de compras realizadas ou outras despesas.
    
    Responsabilidades:
    - Registrar valores a pagar
    - Controlar vencimentos
    - Registrar pagamentos
    - Calcular juros/multas por atraso
    """
    
    # Origem
    fornecedor = models.ForeignKey(
        'partners.Fornecedor',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name='Fornecedor',
        help_text='Fornecedor a ser pago'
    )
    
    # Descrição
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição',
        help_text='Descrição da conta a pagar'
    )
    
    categoria = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Categoria',
        help_text='Categoria da despesa (ex: Fornecedores, Aluguel, Salários)'
    )
    
    # Valores
    valor_original = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Original',
        help_text='Valor original da conta'
    )
    
    valor_juros = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Juros',
        help_text='Valor de juros aplicados'
    )
    
    valor_multa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Multa',
        help_text='Valor de multa aplicada'
    )
    
    valor_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto',
        help_text='Valor de desconto obtido'
    )
    
    # Datas
    data_emissao = models.DateField(
        default=timezone.now,
        verbose_name='Data de Emissão'
    )
    
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento',
        db_index=True
    )
    
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Pagamento'
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusConta.choices,
        default=StatusConta.PENDENTE,
        verbose_name='Status',
        db_index=True
    )
    
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TipoPagamento.choices,
        null=True,
        blank=True,
        verbose_name='Tipo de Pagamento'
    )
    
    # Documento fiscal
    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número do Documento',
        help_text='Número da nota fiscal, recibo, etc.'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    
    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['data_vencimento', '-created_at']
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'data_vencimento']),
            models.Index(fields=['fornecedor', 'status']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        """Representação amigável da conta."""
        fornecedor_info = f" - {self.fornecedor.nome_exibicao}" if self.fornecedor else ""
        return f"CP #{self.id}{fornecedor_info} - R$ {self.valor_total} (Venc: {self.data_vencimento})"
    
    @property
    def valor_total(self):
        """Calcula valor total da conta."""
        return (
            self.valor_original + 
            self.valor_juros + 
            self.valor_multa - 
            self.valor_desconto
        )
    
    @property
    def esta_vencida(self):
        """Verifica se a conta está vencida."""
        if self.status == StatusConta.PAGA:
            return False
        return timezone.now().date() > self.data_vencimento
    
    @property
    def dias_atraso(self):
        """Calcula dias de atraso."""
        if not self.esta_vencida:
            return 0
        return (timezone.now().date() - self.data_vencimento).days
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        if self.data_vencimento < self.data_emissao:
            raise ValidationError({
                'data_vencimento': 'Data de vencimento não pode ser anterior à emissão'
            })
        
        if self.status == StatusConta.PAGA and not self.data_pagamento:
            raise ValidationError({
                'data_pagamento': 'Data de pagamento é obrigatória para contas pagas'
            })


# === CAIXA PDV ===

class Caixa(TenantModel):
    """
    Ponto de venda físico ou lógico.
    Ex: Caixa 01, Caixa Bar, Caixa Delivery.
    """
    nome = models.CharField(
        max_length=50,
        verbose_name="Nome do Caixa",
        help_text="Identificação do caixa (ex: Caixa 01)"
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Serial/ID",
        help_text="Identificador único ou serial do equipamento (opcional)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se o caixa está disponível para uso"
    )

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
        unique_together = [['empresa', 'nome']]

    def __str__(self):
        return self.nome


class StatusSessao(models.TextChoices):
    """Status da sessão de caixa."""
    ABERTA = 'ABERTA', 'Aberta'
    FECHADA = 'FECHADA', 'Fechada'


class SessaoCaixa(TenantModel):
    """
    Sessão de trabalho de um operador no caixa (Turno).
    Registra abertura, fechamento e totais.
    """
    caixa = models.ForeignKey(
        Caixa,
        on_delete=models.PROTECT,
        related_name='sessoes',
        verbose_name="Caixa"
    )
    operador = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.PROTECT,
        related_name='sessoes_caixa',
        verbose_name="Operador"
    )
    
    data_abertura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Abertura"
    )
    data_fechamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Fechamento"
    )
    
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Inicial (Fundo de Troco)"
    )
    
    saldo_final_informado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saldo Final Informado",
        help_text="Valor contado fisicamente pelo operador no fechamento"
    )
    
    saldo_final_calculado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saldo Final Calculado",
        help_text="Valor esperado pelo sistema (Inicial + Vendas - Sangrias + Suprimentos)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusSessao.choices,
        default=StatusSessao.ABERTA,
        verbose_name="Status"
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )

    class Meta:
        verbose_name = "Sessão de Caixa"
        verbose_name_plural = "Sessões de Caixa"
        ordering = ['-data_abertura']
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'operador']),
            models.Index(fields=['empresa', 'data_abertura']),
        ]

    def __str__(self):
        return f"Sessão #{self.id} - {self.operador} ({self.status})"
        
    @property
    def diferenca_caixa(self):
        """Calcula diferença (sobra/falta)."""
        if self.saldo_final_informado is None or self.saldo_final_calculado is None:
            return None
        return self.saldo_final_informado - self.saldo_final_calculado


class TipoMovimentoCaixa(models.TextChoices):
    """Tipos de movimentação manual de caixa."""
    SUPRIMENTO = 'SUPRIMENTO', 'Suprimento (Entrada)'
    SANGRIA = 'SANGRIA', 'Sangria (Saída)'
    VENDA = 'VENDA', 'Venda (Recebimento)' # Opcional se vincular ContaReceber


class MovimentoCaixa(TenantModel):
    """
    Movimentação financeira dentro de uma sessão de caixa.
    Registra Suprimentos (Reforço), Sangrias (Retirada) e Vendas (Recebimentos em Dinheiro).
    """
    sessao = models.ForeignKey(
        SessaoCaixa,
        on_delete=models.CASCADE,
        related_name='movimentos',
        verbose_name="Sessão"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimentoCaixa.choices,
        verbose_name="Tipo"
    )
    
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor"
    )
    
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora"
    )
    
    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição/Motivo"
    )
    
    # Vínculo opcional com venda (para rastreabilidade)
    venda_origem = models.ForeignKey(
        'sales.Venda',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentos_caixa',
        verbose_name="Venda de Origem"
    )

    class Meta:
        verbose_name = "Movimento de Caixa"
        verbose_name_plural = "Movimentos de Caixa"
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.get_tipo_display()}: R$ {self.valor}"
