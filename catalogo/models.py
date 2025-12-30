"""Modelos do Catálogo (espelhando vendas.* e reutilizando as mesmas tabelas).

managed=False e db_table apontam para as tabelas existentes de vendas,
permitindo transição gradual sem migrações disruptivas.
"""
from django.db import models
from django.utils.text import slugify
from decimal import Decimal
import secrets


class Categoria(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        managed = False
        db_table = "vendas_categoria"
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def save(self, *args, **kwargs):
        if not self.slug and self.nome:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Produto(models.Model):
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

    class Meta:
        managed = False
        db_table = "vendas_produto"
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def save(self, *args, **kwargs):
        if not self.slug and self.nome:
            base_slug = slugify(self.nome)
            slug = base_slug
            idx = 1
            from vendas.models import Produto as VProduto  # evitar colisão
            while VProduto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{idx}"
                idx += 1
            self.slug = slug
        if not self.sku:
            base = slugify(self.nome)[:40]
            code = base or 'produto'
            i = 1
            from vendas.models import Produto as VProduto
            while VProduto.objects.filter(sku=code).exclude(pk=self.pk).exists():
                code = f"{base}-{i}"
                i += 1
            self.sku = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.slug})"


class ProdutoImagem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    alt = models.CharField(max_length=160, blank=True)
    pos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "vendas_produtoimagem"
        ordering = ['pos', 'id']


class ProdutoAtributo(models.Model):
    class Tipo(models.TextChoices):
        TEXTO = 'TEXT', 'Texto'
        NUMERO = 'NUMBER', 'Número'
        BOOLEANO = 'BOOL', 'Booleano'

    codigo = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.TEXTO)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "vendas_produtoatributo"


class ProdutoAtributoValor(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='atributos_valores')
    atributo = models.ForeignKey(ProdutoAtributo, on_delete=models.CASCADE, related_name='valores')
    valor_texto = models.CharField(max_length=160, blank=True)
    valor_numero = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    valor_bool = models.BooleanField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "vendas_produtoatributovalor"
        unique_together = ('produto', 'atributo')


class ProdutoVariacao(models.Model):
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
        managed = False
        db_table = "vendas_produtovariacao"
