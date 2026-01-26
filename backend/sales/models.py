"""
Models de vendas para Projeto Nix.
Gerencia vendas, itens e integração com estoque.
"""
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Max, Sum, F
from decimal import Decimal

from core.models import TenantModel
from catalog.models import Produto, Complemento


class StatusVenda(models.TextChoices):
    """Status possíveis de uma venda."""
    ORCAMENTO = 'ORCAMENTO', 'Orçamento'
    PENDENTE = 'PENDENTE', 'Pendente'
    FINALIZADA = 'FINALIZADA', 'Finalizada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class TipoPagamento(models.TextChoices):
    """Tipos de pagamento aceitos."""
    DINHEIRO = 'DINHEIRO', 'Dinheiro'
    PIX = 'PIX', 'PIX'
    CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
    BOLETO = 'BOLETO', 'Boleto'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência Bancária'
    CONTA_CLIENTE = 'CONTA_CLIENTE', 'Conta Cliente (A Prazo)'


class StatusProducao(models.TextChoices):
    """Status de produção do item (KDS - Kitchen Display System)."""
    PENDENTE = 'PENDENTE', 'Pendente'
    EM_PREPARO = 'EM_PREPARO', 'Em Preparo'
    PRONTO = 'PRONTO', 'Pronto'
    ENTREGUE = 'ENTREGUE', 'Entregue'


class Venda(TenantModel):
    """
    Venda realizada no sistema.
    
    Responsabilidades:
    - Registrar informações da venda (cliente, vendedor, totais)
    - Controlar status do ciclo de vida (orçamento → finalizada/cancelada)
    - Gerar número sequencial amigável por empresa
    
    IMPORTANTE:
    - Use VendaService para finalizar/cancelar vendas (não altere status diretamente)
    - Totais são calculados automaticamente via signals
    - Integração com estoque ocorre apenas no status FINALIZADA
    """
    
    # Número sequencial amigável (ex: 1001, 1002, 1003)
    numero = models.PositiveIntegerField(
        editable=False,
        verbose_name='Número',
        help_text='Número sequencial da venda (gerado automaticamente)',
        db_index=True
    )
    
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    # Relacionamentos
    cliente = models.ForeignKey(
        'partners.Cliente',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vendas',
        verbose_name='Cliente',
        help_text='Cliente da venda (nullable para venda balcão/sem cadastro)'
    )
    
    vendedor = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.PROTECT,
        related_name='vendas_realizadas',
        verbose_name='Vendedor',
        help_text='Usuário responsável pela venda'
    )
    
    colaborador = models.ForeignKey(
        'partners.Colaborador',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendas_comissionadas',
        verbose_name='Colaborador/Garçom (Legacy)',
        help_text='(Depreciado) Use o campo atendente'
    )

    atendente = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendas_atendidas',
        verbose_name='Atendente/Garçom',
        help_text='Usuário atendente que receberá comissão'
    )
    
    comissao_valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Comissão',
        help_text='Valor calculado da comissão'
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=StatusVenda.choices,
        default=StatusVenda.ORCAMENTO,
        verbose_name='Status',
        help_text='Status atual da venda',
        db_index=True
    )
    
    # Valores (atualizados automaticamente por signals)
    total_bruto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total Bruto',
        help_text='Soma de todos os subtotais dos itens'
    )
    
    total_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total Desconto',
        help_text='Soma de todos os descontos aplicados'
    )
    
    total_liquido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total Líquido',
        help_text='Total bruto - total desconto (valor final)'
    )
    
    # Pagamento
    tipo_pagamento = models.CharField(
        max_length=20,
        choices=TipoPagamento.choices,
        default=TipoPagamento.DINHEIRO,
        verbose_name='Tipo de Pagamento',
        help_text='Forma de pagamento utilizada'
    )
    
    # Datas
    data_emissao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Emissão',
        help_text='Data e hora de criação da venda'
    )
    
    data_finalizacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Finalização',
        help_text='Data e hora em que a venda foi finalizada'
    )
    
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Cancelamento',
        help_text='Data e hora em que a venda foi cancelada'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas ou comentários sobre a venda (opcional)'
    )
    
    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_emissao']
        unique_together = [['empresa', 'numero'], ['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'numero']),
            models.Index(fields=['vendedor', 'data_emissao']),
            models.Index(fields=['cliente', 'data_emissao']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        """Representação amigável da venda."""
        cliente_info = f" - {self.cliente.nome}" if self.cliente else " - Balcão"
        return f"Venda #{self.numero}{cliente_info} ({self.get_status_display()})"
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Save com geração de número sequencial.
        
        IMPORTANTE: Usa select_for_update() para prevenir race conditions
        na geração do número sequencial.
        """
        # Gera número sequencial se é uma nova venda
        if not self.numero:
            # Lock para prevenir race condition
            ultimo_numero = Venda.objects.select_for_update().filter(
                empresa=self.empresa
            ).aggregate(Max('numero'))['numero__max']
            
            # Começa em 1001 se for a primeira venda
            self.numero = (ultimo_numero or 1000) + 1
        
        # Gera slug baseado no número
        if not self.slug:
            self.slug = f"venda-{self.numero}"
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Validação: vendedor deve ser da mesma empresa
        if self.vendedor and self.vendedor.empresa != self.empresa:
            raise ValidationError({
                'vendedor': 'Vendedor deve pertencer à mesma empresa'
            })
        
        # Validação: cliente deve ser da mesma empresa (se informado)
        if self.cliente and self.cliente.empresa != self.empresa:
            raise ValidationError({
                'cliente': 'Cliente deve pertencer à mesma empresa'
            })
    
    @property
    def pode_ser_finalizada(self):
        """
        Verifica se a venda pode ser finalizada.
        
        Returns:
            bool: True se status permite finalização
        """
        return self.status in [StatusVenda.ORCAMENTO, StatusVenda.PENDENTE]
    
    @property
    def pode_ser_cancelada(self):
        """
        Verifica se a venda pode ser cancelada.
        
        Returns:
            bool: True se status permite cancelamento
        """
        return self.status == StatusVenda.FINALIZADA
    
    @property
    def quantidade_itens(self):
        """
        Retorna quantidade total de itens na venda.
        
        Returns:
            Decimal: Soma das quantidades de todos os itens
        """
        return self.itens.aggregate(
            total=Sum('quantidade')
        )['total'] or Decimal('0.000')


class ItemVenda(TenantModel):
    """
    Item individual de uma venda.
    
    Responsabilidades:
    - Associar produto à venda
    - Registrar quantidade vendida
    - Fazer snapshot do preço no momento da venda (imutabilidade)
    - Calcular subtotal com desconto
    
    IMPORTANTE:
    - preco_unitario é uma CÓPIA do preço do produto no momento da venda
    - Não altere o preço depois de criado (para manter histórico consistente)
    - Subtotal é calculado automaticamente via property e signal
    """
    
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Venda',
        help_text='Venda à qual este item pertence'
    )
    
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_venda',
        verbose_name='Produto',
        help_text='Produto vendido'
    )
    
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade',
        help_text='Quantidade vendida'
    )
    
    # SNAPSHOT do preço no momento da venda (imutável)
    preco_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço Unitário',
        help_text='Preço do produto no momento da venda (snapshot)'
    )

    # SNAPSHOT do custo no momento da venda (imutável)
    custo_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo Unitário',
        help_text='Custo do produto no momento da venda (snapshot)'
    )
    
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto',
        help_text='Valor de desconto aplicado neste item'
    )
    
    # Subtotal denormalizado (atualizado por signal)
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal',
        help_text='(quantidade × preço) + complementos - desconto'
    )
    
    # Food Service: observações do item
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Observações específicas deste item (ex: sem cebola, ponto da carne)'
    )
    
    # KDS (Kitchen Display System)
    status_producao = models.CharField(
        max_length=20,
        choices=StatusProducao.choices,
        default=StatusProducao.PENDENTE,
        verbose_name='Status de Produção',
        help_text='Status atual na cozinha/bar',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['venda', 'produto']),
            models.Index(fields=['empresa', 'produto']),
        ]
    
    def __str__(self):
        """Representação amigável do item."""
        return (
            f"{self.quantidade} × {self.produto.nome} "
            f"(Venda #{self.venda.numero})"
        )
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Validação: venda e produto devem ser da mesma empresa
        if self.venda.empresa != self.empresa:
            raise ValidationError({
                'venda': 'Venda deve pertencer à mesma empresa'
            })
        
        if self.produto.empresa != self.empresa:
            raise ValidationError({
                'produto': 'Produto deve pertencer à mesma empresa'
            })
        
        # Validação: quantidade deve ser positiva
        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'Quantidade deve ser maior que zero'
            })
        
        # Validação: desconto não pode ser maior que o total
        total_sem_desconto = self.quantidade * self.preco_unitario
        if self.desconto > total_sem_desconto:
            raise ValidationError({
                'desconto': f'Desconto ({self.desconto}) não pode ser maior que o total sem desconto ({total_sem_desconto})'
            })
        
        # Validação: não pode adicionar itens a venda finalizada ou cancelada
        if self.venda.status in [StatusVenda.FINALIZADA, StatusVenda.CANCELADA]:
            raise ValidationError(
                f"Não é possível adicionar itens a uma venda {self.venda.get_status_display()}"
            )
    
    def save(self, *args, **kwargs):
        """
        Save com cálculo automático do subtotal.
        
        IMPORTANTE: Se preco_unitario ou custo_unitario não forem fornecidos, 
        usa os valores atuais do produto (snapshot).
        """
        # Faz snapshot do preço e custo se não foram fornecidos
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco_venda
        
        if not self.custo_unitario:
            self.custo_unitario = self.produto.preco_custo
        
        # Calcula subtotal (será recalculado pelo signal incluindo complementos)
        self.subtotal = (self.quantidade * self.preco_unitario) - self.desconto
        
        super().save(*args, **kwargs)
    
    @property
    def total_sem_desconto(self):
        """
        Calcula total sem desconto.
        
        Returns:
            Decimal: quantidade × preço unitário
        """
        return self.quantidade * self.preco_unitario
    
    @property
    def percentual_desconto(self):
        """
        Calcula percentual de desconto aplicado.
        
        Returns:
            Decimal: Percentual de desconto (0-100)
        """
        if self.total_sem_desconto == 0:
            return Decimal('0.00')
        
        percentual = (self.desconto / self.total_sem_desconto) * 100
        return round(percentual, 2)
    
    @property
    def total_complementos(self):
        """
        Calcula valor total dos complementos deste item.
        
        Returns:
            Decimal: Soma de todos os complementos
        """
        return self.complementos.aggregate(
            total=Sum('subtotal')
        )['total'] or Decimal('0.00')


class ItemVendaComplemento(TenantModel):
    """
    Complemento/adicional escolhido para um item de venda.
    
    Responsabilidades:
    - Registrar escolhas do cliente (ex: Borda Catupiry, Ponto Mal Passado)
    - Fazer snapshot do preço do complemento
    - Calcular subtotal do complemento
    - Vincular complemento ao item pai
    
    Exemplos de uso:
    - Pizza: Borda Catupiry (+R$ 5,00)
    - Hambúrguer: Bacon (+R$ 3,00), Ovo (+R$ 2,00)
    - Carne: Ponto Mal Passado (sem custo adicional)
    
    IMPORTANTE:
    - preco_unitario é SNAPSHOT do complemento no momento
    - Se complemento tem produto_referencia, deve baixar estoque
    """
    
    item_pai = models.ForeignKey(
        ItemVenda,
        on_delete=models.CASCADE,
        related_name='complementos',
        verbose_name='Item Pai',
        help_text='Item de venda ao qual este complemento pertence'
    )
    
    complemento = models.ForeignKey(
        Complemento,
        on_delete=models.PROTECT,
        related_name='itens_vendidos',
        verbose_name='Complemento',
        help_text='Complemento escolhido pelo cliente'
    )
    
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade',
        help_text='Quantidade deste complemento'
    )
    
    # SNAPSHOT do preço do complemento no momento
    preco_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço Unitário',
        help_text='Preço adicional do complemento (snapshot)'
    )
    
    # Subtotal calculado
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal',
        help_text='quantidade × preço unitário'
    )
    
    class Meta:
        verbose_name = 'Complemento do Item'
        verbose_name_plural = 'Complementos dos Itens'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['item_pai', 'complemento']),
            models.Index(fields=['empresa', 'complemento']),
        ]
    
    def __str__(self):
        """Representação amigável."""
        return f"{self.complemento.nome} (Item #{self.item_pai.id})"
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Validação: item_pai e complemento devem ser da mesma empresa
        if self.item_pai.empresa != self.empresa:
            raise ValidationError({
                'item_pai': 'Item deve pertencer à mesma empresa'
            })
        
        if self.complemento.empresa != self.empresa:
            raise ValidationError({
                'complemento': 'Complemento deve pertencer à mesma empresa'
            })
        
        # Validação: quantidade deve ser positiva
        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'Quantidade deve ser maior que zero'
            })
    
    def save(self, *args, **kwargs):
        """Save com snapshot de preço e cálculo de subtotal."""
        # Faz snapshot do preço se não fornecido
        if not self.preco_unitario:
            self.preco_unitario = self.complemento.preco_adicional
        
        # Calcula subtotal
        self.subtotal = self.quantidade * self.preco_unitario
        
        super().save(*args, **kwargs)
    
    @property
    def possui_produto_vinculado(self):
        """Verifica se complemento baixa estoque."""
        return self.complemento.possui_produto_vinculado
