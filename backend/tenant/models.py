"""
Models de empresas (tenants) para Projeto Nix.
Define a estrutura de multi-tenancy do sistema.
"""
import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validar_cnpj(value):
    """
    Valida CNPJ brasileiro.
    
    Args:
        value: CNPJ a validar (com ou sem formatação)
    
    Raises:
        ValidationError: Se CNPJ for inválido
    """
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, value))
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        raise ValidationError('CNPJ deve ter 14 dígitos')
    
    # Verifica se não é sequência repetida
    if cnpj == cnpj[0] * 14:
        raise ValidationError('CNPJ inválido')
    
    # Cálculo dos dígitos verificadores
    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(cnpj_parcial[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj[:12], pesos1)
    
    if int(cnpj[12]) != digito1:
        raise ValidationError('CNPJ inválido (primeiro dígito verificador)')
    
    # Segundo dígito
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj[:13], pesos2)
    
    if int(cnpj[13]) != digito2:
        raise ValidationError('CNPJ inválido (segundo dígito verificador)')


class Empresa(models.Model):
    """
    Empresa/Tenant no sistema multi-tenant.
    
    Cada empresa tem dados isolados através do TenantModel.
    Esta é a entidade raiz da hierarquia multi-tenant.
    
    Responsabilidades:
    - Identificar empresa no sistema
    - Armazenar dados fiscais e cadastrais
    - Configurações gerais da empresa
    - Controle de ativação/desativação
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    # Dados cadastrais
    nome_fantasia = models.CharField(
        max_length=200,
        verbose_name='Nome Fantasia',
        help_text='Nome comercial da empresa'
    )
    
    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    razao_social = models.CharField(
        max_length=200,
        verbose_name='Razão Social',
        help_text='Razão social completa da empresa'
    )
    
    cnpj_validator = RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$',
        message='CNPJ deve estar no formato 00.000.000/0000-00 ou 00000000000000'
    )
    
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        validators=[cnpj_validator, validar_cnpj],
        verbose_name='CNPJ',
        help_text='Cadastro Nacional de Pessoa Jurídica'
    )
    
    # Contato
    email = models.EmailField(
        blank=True,
        verbose_name='Email',
        help_text='Email principal da empresa'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
        help_text='Telefone principal'
    )
    
    website = models.URLField(
        blank=True,
        verbose_name='Website',
        help_text='Site da empresa (opcional)'
    )
    
    # Configurações
    logo = models.ImageField(
        upload_to='empresas/logos/',
        blank=True,
        null=True,
        verbose_name='Logo',
        help_text='Logotipo da empresa'
    )
    
    cor_primaria = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name='Cor Primária',
        help_text='Cor principal do tema (hex: #RRGGBB)'
    )
    
    cor_secundaria = models.CharField(
        max_length=7,
        default='#10B981',
        verbose_name='Cor Secundária',
        help_text='Cor secundária do tema (hex: #RRGGBB)'
    )
    
    # Preferências do sistema
    moeda = models.CharField(
        max_length=3,
        default='BRL',
        verbose_name='Moeda',
        help_text='Código ISO da moeda (BRL, USD, EUR)'
    )
    
    fuso_horario = models.CharField(
        max_length=50,
        default='America/Sao_Paulo',
        verbose_name='Fuso Horário',
        help_text='Fuso horário da empresa (ex: America/Sao_Paulo)'
    )
    
    # Controle
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa',
        help_text='Indica se a empresa está ativa no sistema',
        db_index=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em'
    )
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome_fantasia']
    
    def __str__(self):
        """Representação amigável da empresa."""
        return f"{self.nome_fantasia} ({self.cnpj})"
    
    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Normaliza CNPJ (remove formatação)
        if self.cnpj:
            cnpj_limpo = ''.join(filter(str.isdigit, self.cnpj))
            # Formata CNPJ: 00.000.000/0000-00
            if len(cnpj_limpo) == 14:
                self.cnpj = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    
    def save(self, *args, **kwargs):
        """Save com validações e geração de slug."""
        # Gera slug automaticamente se não fornecido
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.nome_fantasia)
            slug = base_slug
            counter = 1
            while Empresa.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def cnpj_numerico(self):
        """
        Retorna CNPJ apenas com números.
        
        Returns:
            str: CNPJ sem formatação (14 dígitos)
        """
        return ''.join(filter(str.isdigit, self.cnpj))
