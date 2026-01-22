"""
Models de autenticação para Projeto Nix.
Usuários customizados com suporte a multi-tenancy.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class TipoCargo(models.TextChoices):
    """Tipos de cargo/função no sistema."""
    ADMIN = 'ADMIN', 'Administrador'
    GERENTE = 'GERENTE', 'Gerente'
    VENDEDOR = 'VENDEDOR', 'Vendedor'
    CAIXA = 'CAIXA', 'Operador de Caixa'
    ESTOQUISTA = 'ESTOQUISTA', 'Estoquista'
    FINANCEIRO = 'FINANCEIRO', 'Financeiro'


class CustomUser(AbstractUser):
    """
    Usuário customizado com suporte a multi-tenancy.
    
    Estende AbstractUser do Django adicionando:
    - Associação com Empresa (tenant)
    - Cargo/função no sistema
    - Configurações pessoais
    
    IMPORTANTE: Este é o model de usuário padrão do sistema.
    Configure em settings.py: AUTH_USER_MODEL = 'authentication.CustomUser'
    """
    
    # Associação com empresa (multi-tenancy)
    empresa = models.ForeignKey(
        'tenant.Empresa',
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Empresa',
        help_text='Empresa à qual o usuário pertence'
    )
    
    # Cargo/função
    cargo = models.CharField(
        max_length=20,
        choices=TipoCargo.choices,
        default=TipoCargo.VENDEDOR,
        verbose_name='Cargo',
        help_text='Função do usuário no sistema',
        db_index=True
    )
    
    # Informações adicionais
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
        help_text='Telefone de contato'
    )
    
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil',
        help_text='Avatar do usuário'
    )
    
    # Configurações de notificação
    receber_notificacoes_email = models.BooleanField(
        default=True,
        verbose_name='Receber Notificações por Email',
        help_text='Enviar notificações do sistema por email'
    )

    # Funções Operacionais (Colaborador)
    is_colaborador = models.BooleanField(
        default=False, 
        verbose_name="É Colaborador?",
        help_text="Indica se o usuário também é um colaborador (funcionário)"
    )
    role_atendente = models.BooleanField(
        default=False, 
        verbose_name="É Atendente/Garçom?",
        help_text="Pode ser selecionado como atendente em vendas"
    )
    role_caixa = models.BooleanField(
        default=False, 
        verbose_name="É Operador de Caixa?",
        help_text="Pode abrir e fechar caixas"
    )
    comissao_percentual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00, 
        verbose_name="Comissão (%)",
        help_text="Percentual de comissão sobre vendas"
    )
    
    # Campos herdados de AbstractUser:
    # - username
    # - first_name
    # - last_name
    # - email
    # - is_staff
    # - is_active
    # - is_superuser
    # - date_joined
    # - last_login
    # - groups
    # - user_permissions
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['empresa', 'username']
        indexes = [
            models.Index(fields=['empresa', 'is_active']),
            models.Index(fields=['cargo']),
        ]
    
    def __str__(self):
        """Representação amigável do usuário."""
        nome_completo = self.get_full_name()
        if nome_completo:
            return f"{nome_completo} (@{self.username})"
        return self.username
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Email é obrigatório
        if not self.email:
            raise ValidationError({'email': 'Email é obrigatório'})
    
    @property
    def nome_completo(self):
        """
        Retorna nome completo ou username.
        
        Returns:
            str: Nome completo ou username se nome não definido
        """
        return self.get_full_name() or self.username
    
    @property
    def is_admin(self):
        """Verifica se usuário é administrador."""
        return self.cargo == TipoCargo.ADMIN or self.is_superuser
    
    @property
    def is_gerente(self):
        """Verifica se usuário é gerente ou admin."""
        return self.cargo in [TipoCargo.ADMIN, TipoCargo.GERENTE] or self.is_superuser
    
    @property
    def is_vendedor(self):
        return self.cargo in [TipoCargo.VENDEDOR, TipoCargo.CAIXA, TipoCargo.GERENTE, TipoCargo.ADMIN] or self.is_superuser
    
    def pode_acessar_financeiro(self):
        """Verifica se usuário pode acessar módulo financeiro."""
        return self.cargo in [TipoCargo.ADMIN, TipoCargo.GERENTE, TipoCargo.FINANCEIRO]
    
    def pode_gerenciar_estoque(self):
        """Verifica se usuário pode gerenciar estoque."""
        return self.cargo in [TipoCargo.ADMIN, TipoCargo.GERENTE, TipoCargo.ESTOQUISTA]
    
    def pode_finalizar_vendas(self):
        """Verifica se usuário pode finalizar vendas."""
        return self.cargo in [TipoCargo.ADMIN, TipoCargo.GERENTE, TipoCargo.VENDEDOR, TipoCargo.CAIXA]
