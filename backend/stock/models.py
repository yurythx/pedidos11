"""
Models de gestão de estoque para Projeto Nix.
Implementa controle de inventário físico com rastreamento de movimentações.

SEPARAÇÃO DE RESPONSABILIDADES (DDD):
- catalog: Define O QUE é o produto (comercial)
- stock: Define ONDE e QUANTO temos (logística)
"""
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal

from core.models import TenantModel
from catalog.models import Produto


class TipoMovimentacao(models.TextChoices):
    """Tipos de movimentação de estoque."""
    ENTRADA = 'ENTRADA', 'Entrada'
    SAIDA = 'SAIDA', 'Saída'
    BALANCO = 'BALANCO', 'Balanço'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência'
    AJUSTE = 'AJUSTE', 'Ajuste'


class Deposito(TenantModel):
    """
    Depósito/Armazém para estoque de produtos.
    
    Representa locais físicos ou virtuais onde produtos são armazenados.
    Exemplos:
    - Loja Principal (físico)
    - Estoque Virtual (para reservas)
    - Almoxarifado Central (físico)
    - CD (Centro de Distribuição)
    
    Características:
    - Suporta endereço via GenericForeignKey do app locations
    - Flag de depósito padrão para automações
    - Slug para identificação amigável
    """
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome do depósito/armazém'
    )
    
    slug = models.SlugField(
        max_length=120,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    codigo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código',
        help_text='Código interno do depósito (opcional)'
    )
    
    is_padrao = models.BooleanField(
        default=False,
        verbose_name='Depósito Padrão',
        help_text='Usar como padrão em operações automáticas',
        db_index=True
    )
    
    is_virtual = models.BooleanField(
        default=False,
        verbose_name='Virtual',
        help_text='Depósito virtual (não físico) usado para reservas'
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição ou observações sobre o depósito'
    )
    
    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['-is_padrao', 'nome']
        unique_together = [['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'is_padrao']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        """Representação amigável do depósito."""
        if self.codigo:
            return f"[{self.codigo}] {self.nome}"
        return self.nome
    
    def save(self, *args, **kwargs):
        """
        Validações e automações no save.
        - Gera slug automaticamente
        - Garante apenas um depósito padrão por empresa
        """
        # Gera slug
        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while Deposito.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Garante apenas um depósito padrão por empresa
        if self.is_padrao:
            Deposito.objects.filter(
                empresa=self.empresa,
                is_padrao=True
            ).exclude(id=self.id).update(is_padrao=False)
        
        super().save(*args, **kwargs)


class Saldo(TenantModel):
    """
    Saldo atual de produtos por depósito.
    
    Tabela pivot que representa a quantidade disponível de cada produto
    em cada depósito. Esta é a "fonte da verdade" para consultas de estoque.
    
    Características:
    - Relacionamento único: Empresa × Produto × Depósito
    - Atualizado automaticamente pelas Movimentações
    - NÃO deve ser editado manualmente - use Movimentacao
    
    IMPORTANTE: Não crie ou edite Saldo diretamente.
    Sempre use o model Movimentacao que atualiza o Saldo automaticamente.
    """
    
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='saldos',
        verbose_name='Produto'
    )
    
    deposito = models.ForeignKey(
        Deposito,
        on_delete=models.PROTECT,
        related_name='saldos',
        verbose_name='Depósito'
    )
    
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name='Quantidade',
        help_text='Quantidade atual em estoque (atualizado automaticamente)'
    )
    
    # Campo de auditoria - última movimentação que afetou este saldo
    ultima_movimentacao = models.ForeignKey(
        'Movimentacao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Última Movimentação'
    )
    
    class Meta:
        verbose_name = 'Saldo de Estoque'
        verbose_name_plural = 'Saldos de Estoque'
        ordering = ['produto__nome', 'deposito__nome']
        unique_together = [['empresa', 'produto', 'deposito']]
        indexes = [
            models.Index(fields=['empresa', 'produto']),
            models.Index(fields=['empresa', 'deposito']),
            models.Index(fields=['quantidade']),
        ]
    
    def __str__(self):
        """Representação amigável do saldo."""
        return (
            f"{self.produto.nome} @ {self.deposito.nome}: "
            f"{self.quantidade} unidades"
        )
    
    @property
    def disponivel(self):
        """
        Alias para quantidade (pode ser expandido para reservas futuras).
        
        Returns:
            Decimal: Quantidade disponível
        """
        return self.quantidade
    
    def clean(self):
        """
        Validação customizada.
        Previne criação manual - deve ser criado via Movimentacao.
        """
        super().clean()
        
        # Validação: produto e depósito devem ser da mesma empresa
        if self.produto.empresa != self.empresa:
            raise ValidationError({
                'produto': 'Produto deve pertencer à mesma empresa'
            })
        
        if self.deposito.empresa != self.empresa:
            raise ValidationError({
                'deposito': 'Depósito deve pertencer à mesma empresa'
            })


class Movimentacao(TenantModel):
    """
    Movimentação de estoque (audit trail imutável).
    
    Registra TODAS as entradas, saídas e ajustes de estoque.
    Este model é APPEND-ONLY - movimentações não podem ser editadas
    após criação para manter integridade do histórico.
    
    REGRAS CRÍTICAS DE NEGÓCIO:
    1. Atualiza automaticamente o Saldo correspondente no save()
    2. Usa @transaction.atomic para garantir consistência
    3. Usa select_for_update() para prevenir race conditions
    4. Impede edição de movimentações existentes
    5. Cria Saldo automaticamente se for a primeira movimentação
    
    Tipos de Movimentação:
    - ENTRADA: Compra, devolução de cliente, produção
    - SAIDA: Venda, perda, uso interno
    - BALANCO: Ajuste de inventário
    - TRANSFERENCIA: Entre depósitos
    - AJUSTE: Correções gerais
    """
    
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='Produto'
    )
    
    deposito = models.ForeignKey(
        Deposito,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        verbose_name='Depósito',
        help_text='Depósito de origem (para saída) ou destino (para entrada)'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimentacao.choices,
        verbose_name='Tipo',
        help_text='Tipo de movimentação',
        db_index=True
    )
    
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade',
        help_text='Quantidade movimentada (sempre positivo - tipo define direção)'
    )
    
    # Snapshot do valor unitário no momento da movimentação (para custos)
    valor_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Unitário',
        help_text='Custo unitário no momento da movimentação (snapshot)'
    )
    
    # Valor total calculado
    @property
    def valor_total(self):
        """Calcula valor total da movimentação."""
        return self.quantidade * self.valor_unitario
    
    # Referências externas (opcional)
    documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Documento',
        help_text='Número da nota fiscal, pedido, etc. (opcional)'
    )
    
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação',
        help_text='Detalhes ou motivo da movimentação (opcional)'
    )
    
    # Auditoria adicional
    usuario = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Usuário',
        help_text='Usuário responsável pela movimentação'
    )
    
    # Controle de lotes (opcional para migração suave)
    lote = models.ForeignKey(
        'Lote',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimentacoes',
        verbose_name='Lote',
        help_text='Lote específico desta movimentação (opcional, para controle FIFO/FEFO)'
    )
    
    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['empresa', 'produto', 'deposito']),
            models.Index(fields=['empresa', 'tipo']),
            models.Index(fields=['created_at']),
            models.Index(fields=['documento']),
        ]
    
    def __str__(self):
        """Representação amigável da movimentação."""
        return (
            f"{self.get_tipo_display()}: {self.quantidade} × "
            f"{self.produto.nome} @ {self.deposito.nome}"
        )
    
    def clean(self):
        """
        Validações antes do save.
        """
        super().clean()
        
        # Validações de empresa
        if self.produto.empresa != self.empresa:
            raise ValidationError({
                'produto': 'Produto deve pertencer à mesma empresa'
            })
        
        if self.deposito.empresa != self.empresa:
            raise ValidationError({
                'deposito': 'Depósito deve pertencer à mesma empresa'
            })
        
        # Quantidade deve ser positiva
        if self.quantidade <= 0:
            raise ValidationError({
                'quantidade': 'Quantidade deve ser maior que zero'
            })
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Save com lógica crítica de negócio.
        
        IMPLEMENTAÇÃO DAS REGRAS CRÍTICAS:
        1. Impede modificação de movimentações existentes (append-only)
        2. Usa select_for_update() para lock de linha (previne race condition)
        3. Atualiza ou cria Saldo automaticamente
        4. Tudo dentro de uma transação atômica
        
        Raises:
            ValidationError: Se tentar editar movimentação existente
        """
        # REGRA 1: Movimentações são imutáveis (append-only)
        if not self._state.adding:
            raise ValidationError(
                "Movimentações não podem ser editadas após criação. "
                "Crie uma nova movimentação de ajuste se necessário."
            )
        
        # Executa validações
        self.full_clean()
        
        # Salva a movimentação primeiro
        super().save(*args, **kwargs)
        
        # REGRA 2 e 3: Atualiza Saldo com lock (select_for_update)
        try:
            # Tenta obter o saldo existente COM LOCK para prevenir race condition
            saldo = Saldo.objects.select_for_update().get(
                empresa=self.empresa,
                produto=self.produto,
                deposito=self.deposito
            )
        except Saldo.DoesNotExist:
            # REGRA 4: Cria saldo se for a primeira movimentação
            saldo = Saldo(
                empresa=self.empresa,
                produto=self.produto,
                deposito=self.deposito,
                quantidade=Decimal('0.000')
            )
        
        # Atualiza quantidade baseado no tipo de movimentação
        if self.tipo in [TipoMovimentacao.ENTRADA, TipoMovimentacao.BALANCO]:
            saldo.quantidade += self.quantidade
        elif self.tipo in [TipoMovimentacao.SAIDA, TipoMovimentacao.AJUSTE]:
            saldo.quantidade -= self.quantidade
        # TRANSFERENCIA será tratada criando duas movimentações
        
        # Previne saldo negativo (regra de negócio)
        if saldo.quantidade < 0:
            raise ValidationError(
                f"Operação resultaria em saldo negativo: {saldo.quantidade}. "
                f"Saldo atual: {saldo.quantidade + self.quantidade}, "
                f"Tentativa de saída: {self.quantidade}"
            )
        
        # Atualiza referência da última movimentação
        saldo.ultima_movimentacao = self
        saldo.save()
    
    @classmethod
    def criar_transferencia(cls, produto, deposito_origem, deposito_destino, 
                           quantidade, empresa, valor_unitario=None, **kwargs):
        """
        Método auxiliar para criar transferência entre depósitos.
        
        Cria duas movimentações atomicamente:
        1. SAIDA do depósito de origem
        2. ENTRADA no depósito de destino
        
        Args:
            produto: Produto a transferir
            deposito_origem: Depósito de onde sai
            deposito_destino: Depósito para onde vai
            quantidade: Quantidade a transferir
            empresa: Empresa (tenant)
            valor_unitario: Valor unitário (opcional)
            **kwargs: Campos adicionais (documento, observacao, usuario)
        
        Returns:
            tuple: (movimentacao_saida, movimentacao_entrada)
        """
        with transaction.atomic():
            # Saída do depósito de origem
            mov_saida = cls.objects.create(
                empresa=empresa,
                produto=produto,
                deposito=deposito_origem,
                tipo=TipoMovimentacao.TRANSFERENCIA,
                quantidade=quantidade,
                valor_unitario=valor_unitario or produto.preco_custo,
                observacao=f"Transferência para {deposito_destino.nome}. {kwargs.get('observacao', '')}",
                documento=kwargs.get('documento', ''),
                usuario=kwargs.get('usuario', '')
            )
            
            # Entrada no depósito de destino
            mov_entrada = cls.objects.create(
                empresa=empresa,
                produto=produto,
                deposito=deposito_destino,
                tipo=TipoMovimentacao.TRANSFERENCIA,
                quantidade=quantidade,
                valor_unitario=valor_unitario or produto.preco_custo,
                observacao=f"Transferência de {deposito_origem.nome}. {kwargs.get('observacao', '')}",
                documento=kwargs.get('documento', ''),
                usuario=kwargs.get('usuario', '')
            )
            
            return mov_saida, mov_entrada


class Lote(TenantModel):
    """
    Lote de produto com rastreamento de validade.
    
    Permite controle FIFO/FEFO (First Expired, First Out) e rastreabilidade
    completa para recall, fiscalização e redução de perdas por vencimento.
    
    Cada lote representa uma entrada específica de produto com:
    - Código único do lote (fornecedor ou interno)
    - Datas de fabricação e validade
    - Saldo atual específico deste lote
    
    Casos de uso:
    - Consumo automático do lote mais próximo ao vencimento
    - Alertas de produtos prestes a vencer
    - Rastreabilidade para recalls
    - Relatórios de perdas por vencimento
    """
    
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name='Produto',
        help_text='Produto deste lote'
    )
    
    deposito = models.ForeignKey(
        Deposito,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name='Depósito',
        help_text='Depósito onde o lote está armazenado'
    )
    
    codigo_lote = models.CharField(
        max_length=50,
        verbose_name='Código do Lote',
        help_text='Código fornecido pelo fabricante ou gerado internamente',
        db_index=True
    )
    
    data_fabricacao = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Fabricação',
        help_text='Data de fabricação do produto (opcional)'
    )
    
    data_validade = models.DateField(
        verbose_name='Data de Validade',
        help_text='Data de validade/vencimento do lote',
        db_index=True  # Índice crítico para ordenação FIFO/FEFO
    )
    
    quantidade_atual = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name='Saldo Atual',
        help_text='Saldo atual deste lote específico (atualizado automaticamente)'
    )
    
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação',
        help_text='Observações sobre o lote (opcional)'
    )
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['data_validade', 'data_fabricacao']  # Ordem padrão para FIFO/FEFO
        unique_together = [['empresa', 'produto', 'deposito', 'codigo_lote']]
        indexes = [
            models.Index(fields=['empresa', 'produto', 'deposito', 'data_validade']),
            models.Index(fields=['empresa', 'data_validade']),  # Para alertas globais
            models.Index(fields=['codigo_lote']),
        ]
    
    def __str__(self):
        """Representação amigável do lote."""
        return f"{self.codigo_lote} - {self.produto.nome} (Val: {self.data_validade})"
    
    @property
    def dias_ate_vencer(self):
        """
        Calcula dias restantes até o vencimento.
        
        Returns:
            int: Dias até vencer (negativo se já vencido)
        """
        from django.utils import timezone
        delta = self.data_validade - timezone.now().date()
        return delta.days
    
    @property
    def status_validade(self):
        """
        Determina o status do lote baseado na validade.
        
        Returns:
            str: 'VENCIDO', 'CRITICO', 'ATENCAO' ou 'OK'
        """
        dias = self.dias_ate_vencer
        
        if dias < 0:
            return 'VENCIDO'
        elif dias <= 7:
            return 'CRITICO'  # Menos de 1 semana
        elif dias <= 30:
            return 'ATENCAO'  # Menos de 1 mês
        else:
            return 'OK'
    
    @property
    def percentual_consumido(self):
        """
        Calcula percentual consumido do lote (para análises).
        
        Requer que haja movimentações de entrada associadas.
        
        Returns:
            Decimal: Percentual consumido (0-100)
        """
        # Soma todas as entradas deste lote
        entradas = self.movimentacoes.filter(
            tipo__in=[TipoMovimentacao.ENTRADA, TipoMovimentacao.BALANCO]
        ).aggregate(
            total=models.Sum('quantidade')
        )['total'] or Decimal('0')
        
        if entradas == 0:
            return Decimal('0.00')
        
        consumido = entradas - self.quantidade_atual
        percentual = (consumido / entradas) * 100
        return round(percentual, 2)
    
    def clean(self):
        """Validações de negócio."""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        super().clean()
        
        # Validação: data de validade não pode ser no passado (para novos lotes)
        if not self.pk and self.data_validade < timezone.now().date():
            raise ValidationError({
                'data_validade': 'Data de validade não pode estar no passado'
            })
        
        # Validação: data de fabricação deve ser anterior à validade
        if self.data_fabricacao and self.data_fabricacao > self.data_validade:
            raise ValidationError({
                'data_fabricacao': 'Data de fabricação deve ser anterior à data de validade'
            })
        
        # Validação: produto e depósito mesma empresa
        if self.produto.empresa != self.empresa:
            raise ValidationError({
                'produto': 'Produto deve pertencer à mesma empresa'
            })
        
        if self.deposito.empresa != self.empresa:
            raise ValidationError({
                'deposito': 'Depósito deve pertencer à mesma empresa'
            })

