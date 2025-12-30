"""Modelos de Cadastro: Address, Supplier e Customer."""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal


class Address(models.Model):
    """Endereço com campos básicos e referência opcional."""
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=50, blank=True)
    complemento = models.CharField(max_length=200, blank=True)
    bairro = models.CharField(max_length=120, blank=True)
    cidade = models.CharField(max_length=120)
    estado = models.CharField(max_length=50, blank=True)
    cep = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=100, default='Brasil')
    referencia = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.logradouro}, {self.numero or ''} - {self.cidade}"


class Supplier(models.Model):
    """Fornecedor com dados de contato e slug único."""
    nome = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=50, blank=True)
    documento = models.CharField(max_length=32, blank=True)
    enderecos = models.ManyToManyField(Address, blank=True, related_name='fornecedores')
    criado_em = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Gera slug único baseado no nome."""
        if not self.slug:
            base = slugify(self.nome)
            slug = base
            i = 1
            while Supplier.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Customer(models.Model):
    """Cliente com vínculo opcional a usuário do auth e slug único."""
    nome = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=50, blank=True)
    documento = models.CharField(max_length=32, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='clientes')
    enderecos = models.ManyToManyField(Address, blank=True, related_name='clientes')
    criado_em = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Gera slug único baseado no nome."""
        if not self.slug:
            base = slugify(self.nome)
            slug = base
            i = 1
            while Customer.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

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

    def save(self, *args, **kwargs):
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
    class Meta:
        db_table = "cadastro_produto"


class ProdutoImagem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    alt = models.CharField(max_length=160, blank=True)
    pos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pos', 'id']
        db_table = "cadastro_produtoimagem"


class ProdutoAtributo(models.Model):
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
    class Meta:
        db_table = "cadastro_produtoatributo"


class ProdutoAtributoValor(models.Model):
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
        if self.valor_texto:
            return self.valor_texto
        if self.valor_numero is not None:
            return self.valor_numero
        return bool(self.valor_bool)
    class Meta:
        unique_together = ('produto', 'atributo')
        db_table = "cadastro_produtoatributovalor"


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
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.produto.slug}:{self.sku}"
    class Meta:
        indexes = [
            models.Index(fields=['sku']),
        ]
        db_table = "cadastro_produtovariacao"
