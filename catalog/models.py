"""
Models de catálogo de produtos para ProjetoRavenna.
Define a estrutura comercial de produtos e categorias.

IMPORTANTE: Este módulo NÃO contém informações de estoque.
Quantidade de produtos está no módulo 'stock'.
"""
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

from core.models import TenantModel


class TipoProduto(models.TextChoices):
    """Tipos de produto suportados pelo sistema."""
    FISICO = 'FISICO', 'Físico'
    SERVICO = 'SERVICO', 'Serviço'
    DIGITAL = 'DIGITAL', 'Digital'


class Categoria(TenantModel):
    """
    Categoria hierárquica de produtos.
    
    Suporta estrutura de árvore (categorias e subcategorias) através
    do campo 'parent'. Permite organização flexível do catálogo.
    
    Exemplos:
        - Eletrônicos → Smartphones → iPhone
        - Alimentos → Bebidas → Refrigerantes
        - Serviços → Consultoria → TI
    
    Características:
    - Hierarquia ilimitada através de self-reference
    - Slug automático para URLs amigáveis
    - Isolamento por tenant (empresa)
    """
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome da categoria'
    )
    
    slug = models.SlugField(
        max_length=120,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name='Categoria Pai',
        help_text='Categoria superior na hierarquia (opcional)'
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada da categoria (opcional)'
    )
    
    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição (menor valor aparece primeiro)'
    )
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']
        unique_together = [['empresa', 'slug']]
        indexes = [
            models.Index(fields=['empresa', 'parent']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        """Retorna caminho completo da categoria."""
        if self.parent:
            return f"{self.parent} → {self.nome}"
        return self.nome
    
    def save(self, *args, **kwargs):
        """Gera slug automaticamente se não fornecido."""
        if not self.slug:
            base_slug = slugify(self.nome)
            # Garante unicidade do slug dentro da empresa
            slug = base_slug
            counter = 1
            while Categoria.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    @property
    def caminho_completo(self):
        """
        Retorna o caminho completo da categoria na hierarquia.
        
        Returns:
            list: Lista de categorias do topo até a atual
            
        Exemplo:
            >>> categoria.caminho_completo
            ['Eletrônicos', 'Smartphones', 'iPhone']
        """
        caminho = [self.nome]
        categoria_atual = self.parent
        
        while categoria_atual:
            caminho.insert(0, categoria_atual.nome)
            categoria_atual = categoria_atual.parent
        
        return caminho
    
    def get_todos_filhos(self):
        """
        Retorna todas as subcategorias recursivamente.
        
        Returns:
            QuerySet: Todas as subcategorias (filhos, netos, bisnetos, etc.)
        """
        from django.db.models import Q
        
        filhos = list(self.subcategorias.all())
        descendentes = filhos.copy()
        
        for filho in filhos:
            descendentes.extend(filho.get_todos_filhos())
        
        return descendentes


class Produto(TenantModel):
    """
    Produto do catálogo comercial.
    
    Define as características comerciais e comerciais do produto.
    NÃO contém informações de estoque - use o módulo 'stock' para isso.
    
    Responsabilidades:
    - Identificação (SKU, código de barras, nome)
    - Precificação (venda e custo como referência)
    - Categorização
    - Tipo de produto
    
    IMPORTANTE: A quantidade em estoque NÃO fica aqui.
    Use stock.Saldo para consultar disponibilidade.
    """
    
    # Identificação
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Nome comercial do produto'
    )
    
    slug = models.SlugField(
        max_length=220,
        verbose_name='Slug',
        help_text='Identificador único para URLs (gerado automaticamente)',
        blank=True
    )
    
    sku = models.CharField(
        max_length=50,
        verbose_name='SKU',
        help_text='Stock Keeping Unit - código interno do produto',
        blank=True
    )
    
    codigo_barras = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Código de Barras',
        help_text='EAN, UPC ou qualquer código de barras'
    )
    
    # Classificação
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='produtos',
        verbose_name='Categoria',
        help_text='Categoria do produto'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoProduto.choices,
        default=TipoProduto.FISICO,
        verbose_name='Tipo',
        help_text='Tipo do produto (Físico, Serviço ou Digital)'
    )
    
    # Precificação (valores de referência)
    preco_venda = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço de Venda',
        help_text='Preço de venda padrão (pode variar por lista de preço)'
    )
    
    preco_custo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name='Preço de Custo',
        help_text='Custo médio de aquisição (referência)'
    )
    
    # Informações complementares
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do produto (opcional)'
    )
    
    descricao_curta = models.CharField(
        max_length=250,
        blank=True,
        verbose_name='Descrição Curta',
        help_text='Resumo para listagens (opcional)'
    )
    
    # Controle
    permite_venda_sem_estoque = models.BooleanField(
        default=False,
        verbose_name='Permite Venda sem Estoque',
        help_text='Se True, permite vender mesmo com estoque zerado'
    )
    
    destaque = models.BooleanField(
        default=False,
        verbose_name='Produto em Destaque',
        help_text='Marcar para destacar em vitrines e promoções',
        db_index=True
    )
    
    # Food Service (Restaurante)
    setor_impressao = models.ForeignKey(
        'restaurant.SetorImpressao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name='Setor de Impressão',
        help_text='Setor onde o pedido deste produto será impresso (ex: Cozinha, Bar)'
    )
    
    imprimir_producao = models.BooleanField(
        default=True,
        verbose_name='Imprimir na Produção',
        help_text='Se True, item aparecerá na impressão da cozinha/bar'
    )
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']
        unique_together = [
            ['empresa', 'slug'],
            ['empresa', 'codigo_barras'],  # Código de barras único por empresa
        ]
        indexes = [
            models.Index(fields=['empresa', 'categoria']),
            models.Index(fields=['empresa', 'tipo']),
            models.Index(fields=['sku']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['destaque', 'is_active']),
        ]
    
    def __str__(self):
        """Representação amigável do produto."""
        if self.sku:
            return f"[{self.sku}] {self.nome}"
        return self.nome
    
    def save(self, *args, **kwargs):
        """
        Validações e automações no save.
        - Gera slug automaticamente
        - Gera SKU se não fornecido
        """
        # Gera slug
        if not self.slug:
            base_slug = slugify(self.nome)
            slug = base_slug
            counter = 1
            while Produto.objects.filter(
                empresa=self.empresa,
                slug=slug
            ).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Gera SKU se não fornecido
        if not self.sku:
            # Usa ID curto ou timestamp para gerar SKU
            import hashlib
            unique_str = f"{self.empresa_id}-{self.nome}-{self.created_at or ''}"
            hash_obj = hashlib.md5(unique_str.encode())
            self.sku = f"SKU-{hash_obj.hexdigest()[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    @property
    def margem_lucro(self):
        """
        Calcula a margem de lucro percentual.
        
        Returns:
            Decimal: Margem de lucro em percentual
            
        Exemplo:
            >>> produto.margem_lucro
            Decimal('25.50')  # 25.5% de margem
        """
        if self.preco_custo == 0:
            return Decimal('0.00')
        
        margem = ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return round(margem, 2)
    
    @property
    def lucro_unitario(self):
        """
        Retorna o lucro unitário (venda - custo).
        
        Returns:
            Decimal: Diferença entre preço de venda e custo
        """
        return self.preco_venda - self.preco_custo


class GrupoComplemento(TenantModel):
    """
    Agrupa opções de complementos para um produto.
    
    Exemplos:
    - "Escolha o Ponto da Carne" (obrigatório, min=1, max=1)
    - "Escolha a Borda" (opcional, min=0, max=1)
    - "Adicionais" (opcional, min=0, max=10)
    
    Responsabilidades:
    - Definir grupos de opções
    - Controlar obrigatoriedade
    - Limitar quantidade de escolhas
    - Vincular a produtos específicos
    """
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome do grupo (ex: "Escolha o Ponto", "Adicionais")'
    )
    
    obrigatorio = models.BooleanField(
        default=False,
        verbose_name='Obrigatório',
        help_text='Cliente deve escolher ao menos uma opção deste grupo'
    )
    
    min_qtd = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade Mínima',
        help_text='Mínimo de opções que devem ser selecionadas'
    )
    
    max_qtd = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Quantidade Máxima',
        help_text='Máximo de opções que podem ser selecionadas'
    )
    
    produtos_vinculados = models.ManyToManyField(
        Produto,
        related_name='grupos_complementos',
        verbose_name='Produtos',
        help_text='Produtos que possuem este grupo de complementos'
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição'
    )
    
    class Meta:
        verbose_name = 'Grupo de Complemento'
        verbose_name_plural = 'Grupos de Complementos'
        ordering = ['ordem', 'nome']
        indexes = [
            models.Index(fields=['empresa', 'is_active']),
        ]
    
    def __str__(self):
        obrig = '(Obrigatório)' if self.obrigatorio else '(Opcional)'
        return f"{self.nome} {obrig}"
    
    def clean(self):
        """Validações de negócio."""
        super().clean()
        
        # min_qtd não pode ser maior que max_qtd
        if self.min_qtd > self.max_qtd:
            raise ValidationError({
                'min_qtd': 'Quantidade mínima não pode ser maior que máxima'
            })
        
        # Se obrigatório, min_qtd deve ser pelo menos 1
        if self.obrigatorio and self.min_qtd < 1:
            self.min_qtd = 1


class Complemento(TenantModel):
    """
    Opção individual de complemento/adicional.
    
    Exemplos:
    - Ponto da Carne: "Mal Passado", "Ao Ponto", "Bem Passado"
    - Borda: "Catupiry", "Cheddar", "Chocolate"
    - Adicionais: "Bacon", "Ovo", "Queijo Extra"
    
    Responsabilidades:
    - Definir opções disponíveis
    - Precificar adicionais
    - Vincular a produtos para baixa de estoque (opcional)
    """
    
    grupo = models.ForeignKey(
        GrupoComplemento,
        on_delete=models.CASCADE,
        related_name='complementos',
        verbose_name='Grupo',
        help_text='Grupo ao qual este complemento pertence'
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome do complemento (ex: "Mal Passado", "Bacon")'
    )
    
    produto_referencia = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complementos_vinculados',
        verbose_name='Produto Referência',
        help_text='Se preenchido, baixa estoque deste produto ao adicionar (ex: Bacon, Ovo)'
    )
    
    preco_adicional = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Preço Adicional',
        help_text='Valor extra somado ao preço do produto principal'
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição'
    )
    
    class Meta:
        verbose_name = 'Complemento'
        verbose_name_plural = 'Complementos'
        ordering = ['grupo', 'ordem', 'nome']
        indexes = [
            models.Index(fields=['empresa', 'grupo']),
            models.Index(fields=['produto_referencia']),
        ]
    
    def __str__(self):
        if self.preco_adicional > 0:
            return f"{self.nome} (+R$ {self.preco_adicional})"
        return self.nome
    
    @property
    def possui_produto_vinculado(self):
        """Verifica se complemento baixa estoque de produto."""
        return self.produto_referencia is not None
