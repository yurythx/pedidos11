"""
Models de parceiros (clientes e fornecedores) para ProjetoRavenna.
"""
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation

from core.models import TenantModel


def validar_cpf(value):
    """
    Valida CPF brasileiro.
    
    Args:
        value: CPF a validar (com ou sem formatação)
    
    Raises:
        ValidationError: Se CPF for inválido
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, value))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')
    
    # Verifica se não é sequência repetida
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido')
    
    # Cálculo dos dígitos verificadores
    def calcular_digito(cpf_parcial):
        soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Valida primeiro dígito
    if int(cpf[9]) != calcular_digito(cpf[:9]):
        raise ValidationError('CPF inválido (primeiro dígito verificador)')
    
    # Valida segundo dígito
    if int(cpf[10]) != calcular_digito(cpf[:10]):
        raise ValidationError('CPF inválido (segundo dígito verificador)')


def validar_cnpj(value):
    """
    Valida CNPJ brasileiro.
    Reutiliza validação do tenant.models.
    """
    from tenant.models import validar_cnpj as validar_cnpj_tenant
    validar_cnpj_tenant(value)


class TipoPessoa(models.TextChoices):
    """Tipos de pessoa fiscal."""
    FISICA = 'FISICA', 'Pessoa Física'
    JURIDICA = 'JURIDICA', 'Pessoa Jurídica'


class Cliente(TenantModel):
    """
    Cliente da empresa.
    
    Responsabilidades:
    - Cadastro de clientes (PF ou PJ)
    - Informações de contato
    - Relacionamento com endereços (via GenericRelation)
    - Controle de crédito e limites (futuro)
    """
    
    # Tipo de pessoa
    tipo_pessoa = models.CharField(
        max_length=10,
        choices=TipoPessoa.choices,
        default=TipoPessoa.FISICA,
        verbose_name='Tipo de Pessoa',
        help_text='Pessoa Física ou Jurídica'
    )
    
    # Identificação
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Nome completo (PF) ou Razão Social (PJ)'
    )
    
    slug = models.SlugField(
        max_length=220,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nome Fantasia',
        help_text='Nome comercial (apenas PJ)'
    )
    
    # Documento (CPF ou CNPJ)
    cpf_cnpj = models.CharField(
        max_length=18,
        verbose_name='CPF/CNPJ',
        help_text='CPF (11 dígitos) ou CNPJ (14 dígitos)',
        db_index=True
    )
    
    # RG/IE
    rg_ie = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='RG/IE',
        help_text='RG (PF) ou Inscrição Estadual (PJ)'
    )
    
    # Contato
    email = models.EmailField(
        blank=True,
        verbose_name='Email',
        help_text='Email principal'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
        help_text='Telefone principal'
    )
    
    celular = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Celular',
        help_text='Celular/WhatsApp'
    )
    
    # Relacionamento com endereços (via GenericRelation)
    enderecos = GenericRelation(
        'locations.Endereco',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='cliente'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas ou comentários sobre o cliente'
    )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        unique_together = [['empresa', 'cpf_cnpj'], ['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'tipo_pessoa']),
            models.Index(fields=['cpf_cnpj']),
            models.Index(fields=['nome']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        """Representação amigável do cliente."""
        if self.nome_fantasia:
            return f"{self.nome_fantasia} ({self.cpf_cnpj})"
        return f"{self.nome} ({self.cpf_cnpj})"
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Gera slug se não fornecido
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while Cliente.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Remove formatação do CPF/CNPJ
        if self.cpf_cnpj:
            self.cpf_cnpj = ''.join(filter(str.isdigit, self.cpf_cnpj))
            
            # Valida CPF ou CNPJ baseado no length
            if len(self.cpf_cnpj) == 11:
                validar_cpf(self.cpf_cnpj)
                # Formata CPF: 000.000.000-00
                self.cpf_cnpj = f"{self.cpf_cnpj[:3]}.{self.cpf_cnpj[3:6]}.{self.cpf_cnpj[6:9]}-{self.cpf_cnpj[9:]}"
                self.tipo_pessoa = TipoPessoa.FISICA
            elif len(self.cpf_cnpj) == 14:
                validar_cnpj(self.cpf_cnpj)
                # Formata CNPJ: 00.000.000/0000-00
                self.cpf_cnpj = f"{self.cpf_cnpj[:2]}.{self.cpf_cnpj[2:5]}.{self.cpf_cnpj[5:8]}/{self.cpf_cnpj[8:12]}-{self.cpf_cnpj[12:]}"
                self.tipo_pessoa = TipoPessoa.JURIDICA
            else:
                raise ValidationError({
                    'cpf_cnpj': 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'
                })
    
    @property
    def documento_numerico(self):
        """Retorna CPF/CNPJ apenas com números."""
        return ''.join(filter(str.isdigit, self.cpf_cnpj))
    
    @property
    def is_pessoa_fisica(self):
        """Verifica se é pessoa física."""
        return self.tipo_pessoa == TipoPessoa.FISICA
    
    @property
    def is_pessoa_juridica(self):
        """Verifica se é pessoa jurídica."""
        return self.tipo_pessoa == TipoPessoa.JURIDICA


class Fornecedor(TenantModel):
    """
    Fornecedor da empresa.
    
    Responsabilidades:
    - Cadastro de fornecedores (geralmente PJ)
    - Informações de contato
    - Condições comerciais (prazo, pagamento)
    - Relacionamento com endereços
    """
    
    # Tipo de pessoa (geralmente jurídica)
    tipo_pessoa = models.CharField(
        max_length=10,
        choices=TipoPessoa.choices,
        default=TipoPessoa.JURIDICA,
        verbose_name='Tipo de Pessoa',
        help_text='Pessoa Física ou Jurídica'
    )
    
    # Identificação
    razao_social = models.CharField(
        max_length=200,
        verbose_name='Razão Social',
        help_text='Razão social do fornecedor'
    )
    
    slug = models.SlugField(
        max_length=220,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nome Fantasia',
        help_text='Nome comercial'
    )
    
    # Documento
    cpf_cnpj = models.CharField(
        max_length=18,
        verbose_name='CPF/CNPJ',
        help_text='CPF ou CNPJ do fornecedor',
        db_index=True
    )
    
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Inscrição Estadual',
        help_text='IE do fornecedor'
    )
    
    # Contato
    email = models.EmailField(
        blank=True,
        verbose_name='Email',
        help_text='Email principal'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
        help_text='Telefone principal'
    )
    
    contato_nome = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nome do Contato',
        help_text='Pessoa de contato principal'
    )
    
    # Relacionamento com endereços
    enderecos = GenericRelation(
        'locations.Endereco',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='fornecedor'
    )
    
    # Condições comerciais
    prazo_entrega_dias = models.PositiveIntegerField(
        default=0,
        verbose_name='Prazo de Entrega (dias)',
        help_text='Prazo médio de entrega em dias'
    )
    
    condicao_pagamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Condição de Pagamento',
        help_text='Condições de pagamento (ex: 30/60/90 dias)'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Notas sobre o fornecedor'
    )
    
    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['razao_social']
        unique_together = [['empresa', 'cpf_cnpj'], ['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'tipo_pessoa']),
            models.Index(fields=['cpf_cnpj']),
            models.Index(fields=['razao_social']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        """Representação amigável do fornecedor."""
        if self.nome_fantasia:
            return f"{self.nome_fantasia} ({self.cpf_cnpj})"
        return f"{self.razao_social} ({self.cpf_cnpj})"
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Gera slug se não fornecido
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.razao_social)
            slug = base_slug
            counter = 1
            while Fornecedor.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Remove formatação e valida CPF/CNPJ
        if self.cpf_cnpj:
            self.cpf_cnpj = ''.join(filter(str.isdigit, self.cpf_cnpj))
            
            if len(self.cpf_cnpj) == 11:
                validar_cpf(self.cpf_cnpj)
                self.cpf_cnpj = f"{self.cpf_cnpj[:3]}.{self.cpf_cnpj[3:6]}.{self.cpf_cnpj[6:9]}-{self.cpf_cnpj[9:]}"
                self.tipo_pessoa = TipoPessoa.FISICA
            elif len(self.cpf_cnpj) == 14:
                validar_cnpj(self.cpf_cnpj)
                self.cpf_cnpj = f"{self.cpf_cnpj[:2]}.{self.cpf_cnpj[2:5]}.{self.cpf_cnpj[5:8]}/{self.cpf_cnpj[8:12]}-{self.cpf_cnpj[12:]}"
                self.tipo_pessoa = TipoPessoa.JURIDICA
            else:
                raise ValidationError({
                    'cpf_cnpj': 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'
                })
    
    @property
    def documento_numerico(self):
        """Retorna CPF/CNPJ apenas com números."""
        return ''.join(filter(str.isdigit, self.cpf_cnpj))
    
    @property
    def nome_exibicao(self):
        """Retorna nome fantasia ou razão social."""
        return self.nome_fantasia or self.razao_social
