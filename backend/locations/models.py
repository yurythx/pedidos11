"""
Models de localização geográfica para Projeto Nix.
Implementa endereços genéricos que podem ser associados a múltiplas entidades.
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator

from core.models import TenantModel


class TipoEndereco(models.TextChoices):
    """Tipos de endereço suportados pelo sistema."""
    COBRANCA = 'COBRANCA', 'Cobrança'
    ENTREGA = 'ENTREGA', 'Entrega'
    FISICO = 'FISICO', 'Físico'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    RESIDENCIAL = 'RESIDENCIAL', 'Residencial'


class UF(models.TextChoices):
    """
    Unidades Federativas do Brasil.
    Enum completo para validação e seleção.
    """
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'


class Endereco(TenantModel):
    """
    Modelo genérico de endereço utilizando GenericForeignKey.
    
    Permite associar endereços a múltiplas entidades (Cliente, Fornecedor, 
    Deposito, etc.) sem criar tabelas separadas para cada tipo.
    
    Características:
    - Suporta múltiplos tipos de endereço (Cobrança, Entrega, Físico)
    - Validação de CEP formato brasileiro
    - Campos completos para endereço brasileiro
    - Associação polimórfica via ContentTypes
    
    Exemplo de uso:
        >>> cliente = Cliente.objects.get(id=...)
        >>> endereco = Endereco.objects.create(
        ...     empresa=cliente.empresa,
        ...     content_object=cliente,
        ...     tipo=TipoEndereco.ENTREGA,
        ...     logradouro='Av. Paulista',
        ...     numero='1000',
        ...     cep='01310-100'
        ... )
    """
    
    # GenericForeignKey - permite associar a qualquer modelo
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de Conteúdo',
        help_text='Tipo da entidade associada (Cliente, Fornecedor, etc.)'
    )
    
    object_id = models.UUIDField(
        verbose_name='ID do Objeto',
        help_text='UUID da entidade associada'
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Tipo de endereço
    tipo = models.CharField(
        max_length=20,
        choices=TipoEndereco.choices,
        default=TipoEndereco.COMERCIAL,
        verbose_name='Tipo de Endereço',
        help_text='Finalidade do endereço',
        db_index=True
    )
    
    # Campos de endereço brasileiro
    cep_validator = RegexValidator(
        regex=r'^\d{5}-?\d{3}$',
        message='CEP deve estar no formato 00000-000 ou 00000000'
    )
    
    cep = models.CharField(
        max_length=9,
        validators=[cep_validator],
        verbose_name='CEP',
        help_text='Código de Endereçamento Postal (com ou sem hífen)'
    )
    
    logradouro = models.CharField(
        max_length=255,
        verbose_name='Logradouro',
        help_text='Rua, avenida, travessa, etc.'
    )
    
    numero = models.CharField(
        max_length=20,
        verbose_name='Número',
        help_text='Número do endereço (use "S/N" para sem número)'
    )
    
    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Complemento',
        help_text='Apartamento, sala, bloco, etc. (opcional)'
    )
    
    bairro = models.CharField(
        max_length=100,
        verbose_name='Bairro',
        help_text='Bairro ou distrito'
    )
    
    cidade = models.CharField(
        max_length=100,
        verbose_name='Cidade',
        help_text='Município'
    )
    
    uf = models.CharField(
        max_length=2,
        choices=UF.choices,
        verbose_name='UF',
        help_text='Unidade Federativa (Estado)'
    )
    
    # Campos opcionais para geolocalização futura
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Latitude',
        help_text='Coordenada geográfica (opcional)'
    )
    
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Longitude',
        help_text='Coordenada geográfica (opcional)'
    )
    
    # Referência ou observação
    referencia = models.TextField(
        blank=True,
        verbose_name='Ponto de Referência',
        help_text='Informações adicionais para localização (opcional)'
    )
    
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['empresa', 'tipo']),
            models.Index(fields=['cep']),
            models.Index(fields=['cidade', 'uf']),
        ]
    
    def __str__(self):
        """Representação amigável do endereço."""
        return (
            f"{self.logradouro}, {self.numero} - "
            f"{self.bairro}, {self.cidade}/{self.uf} - "
            f"CEP: {self.cep} ({self.get_tipo_display()})"
        )
    
    @property
    def endereco_completo(self):
        """
        Retorna o endereço formatado completo.
        
        Returns:
            str: Endereço formatado em múltiplas linhas
        """
        linhas = [
            f"{self.logradouro}, {self.numero}",
        ]
        
        if self.complemento:
            linhas.append(self.complemento)
        
        linhas.append(f"{self.bairro} - {self.cidade}/{self.uf}")
        linhas.append(f"CEP: {self.cep}")
        
        return '\n'.join(linhas)
    
    def clean(self):
        """
        Validação customizada.
        Normaliza CEP removendo caracteres especiais.
        """
        from django.core.exceptions import ValidationError
        
        # Normaliza CEP
        if self.cep:
            self.cep = self.cep.replace('-', '').strip()
            # Adiciona hífen no formato padrão
            if len(self.cep) == 8:
                self.cep = f"{self.cep[:5]}-{self.cep[5:]}"
        
        super().clean()
