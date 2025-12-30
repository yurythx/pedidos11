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


from cadastro.models import Produto


from cadastro.models import ProdutoImagem


from cadastro.models import ProdutoAtributo


from cadastro.models import ProdutoAtributoValor


from cadastro.models import ProdutoVariacao


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
    produto = models.ForeignKey('cadastro.Produto', on_delete=models.PROTECT, related_name='itens_pedido')
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self) -> Decimal:
        """Subtotal = quantidade * preço."""
        return Decimal(self.quantidade) * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido {self.pedido_id})"
