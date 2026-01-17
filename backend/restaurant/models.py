"""
Models para o app Restaurant (Food Service).
Gerencia mesas, comandas e setores de produção.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from core.models import TenantModel


class SetorImpressao(TenantModel):
    """
    Define onde o pedido será impresso (ex: Cozinha, Bar, Copa).
    
    Responsabilidades:
    - Organizar produção por setores
    - Rotear impressão de pedidos
    - Agrupar produtos por local de preparo
    """
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome do setor (ex: Cozinha, Bar, Copa)'
    )
    
    slug = models.SlugField(
        max_length=120,
        verbose_name='Slug',
        help_text='Identificador único para URLs',
        blank=True
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição'
    )
    
    cor = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name='Cor',
        help_text='Cor de identificação (hex: #RRGGBB)'
    )
    
    class Meta:
        verbose_name = 'Setor de Impressão'
        verbose_name_plural = 'Setores de Impressão'
        ordering = ['ordem', 'nome']
        unique_together = [['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.nome}"
    
    def clean(self):
        """Validações e geração de slug."""
        super().clean()
        
        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while SetorImpressao.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug


class StatusMesa(models.TextChoices):
    """Status de uma mesa."""
    LIVRE = 'LIVRE', 'Livre'
    OCUPADA = 'OCUPADA', 'Ocupada'
    RESERVADA = 'RESERVADA', 'Reservada'
    SUJA = 'SUJA', 'Suja'


class Mesa(TenantModel):
    """
    Representa uma mesa física do restaurante.
    
    Responsabilidades:
    - Controlar ocupação de mesas
    - Vincular mesa à venda aberta
    - Gerenciar capacidade e reservas
    """
    
    numero = models.PositiveIntegerField(
        verbose_name='Número',
        help_text='Número da mesa (ex: 10)'
    )
    
    capacidade = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name='Capacidade',
        help_text='Quantidade de pessoas'
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusMesa.choices,
        default=StatusMesa.LIVRE,
        verbose_name='Status',
        help_text='Status atual da mesa',
        db_index=True
    )
    
    venda_atual = models.OneToOneField(
        'sales.Venda',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mesa',
        verbose_name='Venda Atual',
        help_text='Venda aberta vinculada a esta mesa'
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas sobre a mesa'
    )
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero']
        unique_together = [['empresa', 'numero']]
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['numero']),
        ]
    
    def __str__(self):
        return f"Mesa {self.numero} ({self.get_status_display()})"
    
    def clean(self):
        """Validações de negócio."""
        super().clean()
        
        # Se mesa está ocupada, deve ter venda vinculada
        if self.status == StatusMesa.OCUPADA and not self.venda_atual:
            raise ValidationError({
                'venda_atual': 'Mesa ocupada deve ter uma venda vinculada'
            })
        
        # Se mesa não está ocupada, não pode ter venda
        if self.status != StatusMesa.OCUPADA and self.venda_atual:
            self.venda_atual = None
    
    @property
    def esta_livre(self):
        """Verifica se mesa está livre."""
        return self.status == StatusMesa.LIVRE
    
    @property
    def esta_ocupada(self):
        """Verifica se mesa está ocupada."""
        return self.status == StatusMesa.OCUPADA
    
    def ocupar(self, venda):
        """
        Ocupa a mesa com uma venda.
        
        Args:
            venda: Instância de sales.Venda
        """
        if not self.esta_livre:
            raise ValidationError(f"Mesa {self.numero} não está livre")
        
        self.status = StatusMesa.OCUPADA
        self.venda_atual = venda
        self.save()
    
    def liberar(self):
        """Libera a mesa."""
        self.status = StatusMesa.LIVRE
        self.venda_atual = None
        self.save()


class StatusComanda(models.TextChoices):
    """Status de uma comanda."""
    LIVRE = 'LIVRE', 'Livre'
    EM_USO = 'EM_USO', 'Em Uso'
    BLOQUEADA = 'BLOQUEADA', 'Bloqueada'


class Comanda(TenantModel):
    """
    Comanda/Cartão individual para consumo.
    
    Responsabilidades:
    - Identificar consumo individual
    - Vincular comanda à venda
    - Controlar comandas perdidas/bloqueadas
    
    Casos de uso:
    - Bares (cartões individuais)
    - Eventos (consumo em pé)
    - Self-service (controle individual)
    """
    
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código',
        help_text='Número do cartão/ficha (ex: A01, 0042)',
        db_index=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusComanda.choices,
        default=StatusComanda.LIVRE,
        verbose_name='Status',
        db_index=True
    )
    
    venda_atual = models.OneToOneField(
        'sales.Venda',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comanda',
        verbose_name='Venda Atual',
        help_text='Venda aberta vinculada a esta comanda'
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas (ex: motivo do bloqueio)'
    )
    
    class Meta:
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'
        ordering = ['codigo']
        unique_together = [['empresa', 'codigo']]
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"Comanda {self.codigo} ({self.get_status_display()})"
    
    def clean(self):
        """Validações de negócio."""
        super().clean()
        
        # Se comanda está em uso, deve ter venda vinculada
        if self.status == StatusComanda.EM_USO and not self.venda_atual:
            raise ValidationError({
                'venda_atual': 'Comanda em uso deve ter uma venda vinculada'
            })
        
        # Se comanda não está em uso, não pode ter venda
        if self.status != StatusComanda.EM_USO and self.venda_atual:
            self.venda_atual = None
    
    @property
    def esta_livre(self):
        """Verifica se comanda está livre."""
        return self.status == StatusComanda.LIVRE
    
    @property
    def esta_em_uso(self):
        """Verifica se comanda está em uso."""
        return self.status == StatusComanda.EM_USO
    
    def usar(self, venda):
        """
        Coloca comanda em uso com uma venda.
        
        Args:
            venda: Instância de sales.Venda
        """
        if not self.esta_livre:
            raise ValidationError(f"Comanda {self.codigo} não está livre")
        
        self.status = StatusComanda.EM_USO
        self.venda_atual = venda
        self.save()
    
    def liberar(self):
        """Libera a comanda."""
        self.status = StatusComanda.LIVRE
        self.venda_atual = None
        self.save()
    
    def bloquear(self, motivo=''):
        """
        Bloqueia a comanda.
        
        Args:
            motivo: Motivo do bloqueio
        """
        self.status = StatusComanda.BLOQUEADA
        self.venda_atual = None
        if motivo:
            self.observacoes = f"Bloqueada: {motivo}"
        self.save()
