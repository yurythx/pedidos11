"""Modelos de Vendas.

Incluem categorias, produtos (com variações e atributos), pedidos e itens,
com geração de slugs/SKU e utilitários de subtotal.
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from decimal import Decimal
import secrets


class Categoria(models.Model):
    """Categoria de produto, com slug derivado do nome."""
    nome = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.nome:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Produto base com metadados fiscais e de catálogo."""
    nome = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    sku = models.CharField(max_length=64, unique=True, blank=True)
    ean = models.CharField(max_length=14, blank=True, db_index=True)
    UNIDADES = (
        ('UN', 'Unidade'),
        ('CX', 'Caixa'),
        ('KG', 'Kilograma'),
        ('LT', 'Litro'),
    )
    unidade = models.CharField(max_length=4, choices=UNIDADES, default='UN')
    marca = models.CharField(max_length=120, blank=True)
    ncm = models.CharField(max_length=8, blank=True)
    cfop = models.CharField(max_length=4, blank=True)
    atributos = models.JSONField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='produtos')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    disponivel = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """Gera slug único e SKU único derivado do nome."""
        if not self.slug and self.nome:
            base_slug = slugify(self.nome)
            slug = base_slug
            idx = 1
            while Produto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{idx}"
                idx += 1
            self.slug = slug
        if not self.sku:
            base = slugify(self.nome)[:40]
            code = base or 'produto'
            i = 1
            while Produto.objects.filter(sku=code).exclude(pk=self.pk).exists():
                code = f"{base}-{i}"
                i += 1
            self.sku = code
        super().save(*args, **kwargs)


class ProdutoImagem(models.Model):
    """Imagem associada ao produto, com ordenação."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    alt = models.CharField(max_length=160, blank=True)
    pos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pos', 'id']


class ProdutoAtributo(models.Model):
    """Definição de atributo de produto (texto/número/booleano)."""
    class Tipo(models.TextChoices):
        TEXTO = 'TEXT', 'Texto'
        NUMERO = 'NUMBER', 'Número'
        BOOLEANO = 'BOOL', 'Booleano'

    codigo = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.TEXTO)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class ProdutoAtributoValor(models.Model):
    """Valor de atributo aplicado a um produto."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='atributos_valores')
    atributo = models.ForeignKey(ProdutoAtributo, on_delete=models.CASCADE, related_name='valores')
    valor_texto = models.CharField(max_length=160, blank=True)
    valor_numero = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    valor_bool = models.BooleanField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produto', 'atributo')

    def __str__(self):
        return f"{self.produto.slug}:{self.atributo.codigo}"

    @property
    def valor(self):
        """Retorna o valor coerente conforme tipo."""
        if self.valor_texto:
            return self.valor_texto
        if self.valor_numero is not None:
            return self.valor_numero
        return bool(self.valor_bool)


class ProdutoVariacao(models.Model):
    """Variação (SKU) de um produto com preço/custo e atributos."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variacoes')
    sku = models.CharField(max_length=64, unique=True)
    nome = models.CharField(max_length=150, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    disponivel = models.BooleanField(default=True)
    atributos = models.JSONField(blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/variacoes/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.produto.slug}:{self.sku}"


class Pedido(models.Model):
    """Pedido de venda com usuário, status, total e centro de custo."""
    class Status(models.TextChoices):
        PENDENTE = 'Pendente', 'Pendente'
        PREPARANDO = 'Preparando', 'Preparando'
        ENVIADO = 'Enviado', 'Enviado'
        ENTREGUE = 'Entregue', 'Entregue'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    slug = models.SlugField(max_length=32, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_criacao = models.DateTimeField(auto_now_add=True)
    cost_center = models.ForeignKey('financeiro.CostCenter', on_delete=models.SET_NULL, blank=True, null=True, related_name='pedidos')

    def __str__(self):
        return f"Pedido {self.slug or self.pk} - {self.usuario} - {self.status}"

    def save(self, *args, **kwargs):
        """Gera slug único hexadecimal na criação."""
        if not self.slug:
            code = secrets.token_hex(6)
            while Pedido.objects.filter(slug=code).exists():
                code = secrets.token_hex(6)
            self.slug = code
        super().save(*args, **kwargs)


class ItemPedido(models.Model):
    """Item do pedido com quantidade e preço unitário."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self) -> Decimal:
        """Subtotal = quantidade * preço."""
        return Decimal(self.quantidade) * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido_id})"
