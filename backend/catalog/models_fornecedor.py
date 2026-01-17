"""
Models de catálogo de produtos para Projeto Nix.
Define a estrutura comercial de produtos e categorias.

IMPORTANTE: Este módulo NÃO contém informações de estoque.
Quantidade de produtos está no módulo 'stock'.
"""
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

from core.models import TenantModel


class ProdutoFornecedor(TenantModel):
    """
    Vínculo/Memória de produtos de fornecedores.
    
    Armazena o mapeamento entre produtos da empresa e códigos de fornecedores,
    facilitando importações futuras de NFe e mantendo histórico de conversões.
    
    Casos de Uso:
    - Importação de NFe: Sistema lembra qual produto corresponde a cada código XML
    - Conversão de Unidades: NFe vem em caixas (12un), sistema converte automaticamente
    - Histórico de Preços: Rastreia preço médio por fornecedor
    
    Exemplo:
        XML: "7891000100045" (Coca-Cola Cx 12un)
        Produto Interno: "Coca-Cola Lata 350ml" (unidade)
        Fator: 12 (1 caixa = 12 latas)
    """
    
    produto = models.ForeignKey(
        'catalog.Produto',
        on_delete=models.CASCADE,
        related_name='vinculos_fornecedor',
        verbose_name='Produto'
    )
    
    cnpj_fornecedor = models.CharField(
        max_length=14,
        verbose_name='CNPJ Fornecedor',
        help_text='CNPJ do fornecedor (apenas números)'
    )
    
    nome_fornecedor = models.CharField(
        max_length=200,
        verbose_name='Nome do Fornecedor',
        help_text='Razão social ou nome fantasia'
    )
    
    codigo_no_fornecedor = models.CharField(
        max_length=50,
        verbose_name='Código no Fornecedor',
        help_text='Código/SKU/EAN do produto no fornecedor'
    )
    
    fator_conversao = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Fator de Conversão',
        help_text='Quantas unidades do produto equivalem a 1 unidade do fornecedor (ex: 12 para caixas)'
    )
    
    ultimo_preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Último Preço',
        help_text='Último preço de compra (por unidade do fornecedor)'
    )
    
    data_ultima_compra = models.DateTimeField(
        auto_now=True,
        verbose_name='Data Última Compra',
        help_text='Atualizado automaticamente a cada importação'
    )
    
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação',
        help_text='Notas sobre este vínculo'
    )
    
    class Meta:
        db_table = 'catalog_produto_fornecedor'
        verbose_name = 'Vínculo Produto-Fornecedor'
        verbose_name_plural = 'Vínculos Produto-Fornecedor'
        ordering = ['-data_ultima_compra']
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'cnpj_fornecedor', 'codigo_no_fornecedor'],
                name='unique_vinculo_produto_fornecedor'
            )
        ]
        indexes = [
            models.Index(fields=['cnpj_fornecedor']),
            models.Index(fields=['codigo_no_fornecedor']),
        ]
    
    def __str__(self):
        return f'{self.produto.nome} ← {self.nome_fornecedor} ({self.codigo_no_fornecedor})'
    
    @property
    def preco_unitario_convertido(self):
        """Retorna o preço por unidade do produto interno."""
        if self.ultimo_preco and self.fator_conversao:
            return self.ultimo_preco / self.fator_conversao
        return None
