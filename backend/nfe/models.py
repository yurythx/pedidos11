"""
Models para importação de NFe - Projeto Nix.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

from core.models import TenantModel
from tenant.models import AmbienteNFe


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
        db_table = 'nfe_produto_fornecedor'
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


class StatusNFe(models.TextChoices):
    DIGITACAO = 'DIGITACAO', 'Em Digitação'
    VALIDADA = 'VALIDADA', 'Validada'
    ASSINADA = 'ASSINADA', 'Assinada'
    TRANSMITIDA = 'TRANSMITIDA', 'Transmitida'
    AUTORIZADA = 'AUTORIZADA', 'Autorizada'
    REJEITADA = 'REJEITADA', 'Rejeitada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    DENEGADA = 'DENEGADA', 'Denegada'


class TipoEmissao(models.TextChoices):
    NORMAL = '1', 'Normal'
    CONTINGENCIA_FSIA = '2', 'Contingência FS-IA'
    CONTINGENCIA_SCAN = '3', 'Contingência SCAN'
    CONTINGENCIA_EPEC = '4', 'Contingência EPEC'
    CONTINGENCIA_FSDA = '5', 'Contingência FS-DA'
    CONTINGENCIA_SVCAN = '6', 'Contingência SVC-AN'
    CONTINGENCIA_SVCRS = '7', 'Contingência SVC-RS'
    CONTINGENCIA_OFFLINE = '9', 'Contingência Offline'


class FinalidadeNFe(models.TextChoices):
    NORMAL = '1', 'NFe Normal'
    COMPLEMENTAR = '2', 'NFe Complementar'
    AJUSTE = '3', 'NFe de Ajuste'
    DEVOLUCAO = '4', 'Devolução de Mercadoria'


class NotaFiscal(TenantModel):
    """
    Nota Fiscal Eletrônica (NFe/NFCe) de Saída.
    """
    
    # Origem
    venda = models.ForeignKey(
        'sales.Venda',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notas_fiscais',
        verbose_name='Venda de Origem'
    )
    
    cliente = models.ForeignKey(
        'partners.Cliente',
        on_delete=models.PROTECT,
        verbose_name='Destinatário'
    )
    
    # Identificação
    numero = models.PositiveIntegerField(
        verbose_name='Número'
    )
    
    serie = models.PositiveIntegerField(
        verbose_name='Série'
    )
    
    modelo = models.CharField(
        max_length=2,
        default='55',
        verbose_name='Modelo',
        help_text='55=NFe, 65=NFCe'
    )
    
    tipo_emissao = models.CharField(
        max_length=1,
        choices=TipoEmissao.choices,
        default=TipoEmissao.NORMAL,
        verbose_name='Tipo de Emissão'
    )

    finalidade = models.CharField(
        max_length=1,
        choices=FinalidadeNFe.choices,
        default=FinalidadeNFe.NORMAL,
        verbose_name='Finalidade'
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusNFe.choices,
        default=StatusNFe.DIGITACAO,
        verbose_name='Status'
    )
    
    natureza_operacao = models.CharField(
        max_length=60,
        default='VENDA',
        verbose_name='Natureza da Operação'
    )
    
    ambiente = models.CharField(
        max_length=1,
        choices=AmbienteNFe.choices,
        default=AmbienteNFe.HOMOLOGACAO,
        verbose_name='Ambiente'
    )
    
    data_emissao = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Emissão'
    )
    
    data_saida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Saída'
    )
    
    # Chaves e Protocolos
    chave_acesso = models.CharField(
        max_length=44,
        blank=True,
        verbose_name='Chave de Acesso'
    )
    
    protocolo_autorizacao = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Protocolo'
    )
    
    # XMLs
    xml_envio = models.TextField(
        blank=True,
        verbose_name='XML Envio'
    )
    
    xml_retorno = models.TextField(
        blank=True,
        verbose_name='XML Retorno'
    )
    
    xml_processado = models.TextField(
        blank=True,
        verbose_name='XML Processado (ProcNFe)'
    )
    
    # Totais (Snapshot para histórico)
    valor_total_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Produtos'
    )
    
    valor_frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor Frete'
    )
    
    valor_seguro = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor Seguro'
    )
    
    valor_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor Desconto'
    )
    
    valor_outras_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Outras Despesas'
    )
    
    valor_total_nota = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor Total da Nota'
    )
    
    # Totais Impostos (Simplificado para MVP)
    valor_icms = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    valor_ipi = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    valor_pis = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    valor_cofins = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    
    class Meta:
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        ordering = ['-data_emissao']
        constraints = [
            models.UniqueConstraint(
                fields=['empresa', 'modelo', 'serie', 'numero'],
                name='unique_nfe_numero'
            )
        ]
        indexes = [
            models.Index(fields=['chave_acesso']),
            models.Index(fields=['status']),
            models.Index(fields=['data_emissao']),
        ]
        
    def __str__(self):
        return f"NFe {self.numero} - {self.cliente.nome}"


class ItemNotaFiscal(TenantModel):
    """
    Item da Nota Fiscal.
    """
    
    nota = models.ForeignKey(
        NotaFiscal,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Nota Fiscal'
    )
    
    produto = models.ForeignKey(
        'catalog.Produto',
        on_delete=models.PROTECT,
        verbose_name='Produto'
    )
    
    numero_item = models.PositiveIntegerField(
        verbose_name='Nº Item'
    )
    
    # Snapshot dos dados do produto
    codigo_produto = models.CharField(max_length=60, verbose_name='Código')
    descricao_produto = models.CharField(max_length=120, verbose_name='Descrição')
    ncm = models.CharField(max_length=8, verbose_name='NCM')
    cest = models.CharField(max_length=7, blank=True, verbose_name='CEST')
    cfop = models.CharField(max_length=4, verbose_name='CFOP')
    unidade_comercial = models.CharField(max_length=6, verbose_name='Unidade')
    
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Quantidade'
    )
    
    valor_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=10, # Mais precisão para unitário
        verbose_name='Valor Unitário'
    )
    
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total'
    )
    
    valor_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Desconto'
    )
    
    valor_frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Frete'
    )
    
    valor_seguro = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Seguro'
    )
    
    valor_outras_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Outras Despesas'
    )
    
    # Impostos (Simplificado)
    origem = models.CharField(max_length=1, default='0', verbose_name='Origem')
    csosn = models.CharField(max_length=4, blank=True, verbose_name='CSOSN')
    cst_pis = models.CharField(max_length=2, blank=True, verbose_name='CST PIS')
    cst_cofins = models.CharField(max_length=2, blank=True, verbose_name='CST COFINS')
    cst_ipi = models.CharField(max_length=2, blank=True, verbose_name='CST IPI')
    
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    aliquota_icms = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    base_icms = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        verbose_name = 'Item da Nota Fiscal'
        verbose_name_plural = 'Itens da Nota Fiscal'
        ordering = ['numero_item']
        constraints = [
            models.UniqueConstraint(
                fields=['nota', 'numero_item'],
                name='unique_item_nfe'
            )
        ]
        
    def __str__(self):
        return f"Item {self.numero_item} - {self.codigo_produto}"
