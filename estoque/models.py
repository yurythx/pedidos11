"""Modelos de Estoque.

Incluem depósito, motivo de ajuste, movimentos de estoque (IN/OUT/ADJUST) e
recebimentos com itens, vinculando pedidos, compras, usuários e fornecedores.
"""
from django.conf import settings
from django.db import models
from cadastro.models import Produto
from vendas.models import Pedido
from cadastro.models import Supplier
from django.utils import timezone


class Deposito(models.Model):
    """Local físico de armazenamento com slug único."""
    nome = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    endereco = models.ForeignKey('cadastro.Address', on_delete=models.SET_NULL, blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Gera slug único baseado no nome."""
        if not self.slug and self.nome:
            from django.utils.text import slugify
            base = slugify(self.nome)
            s = base
            i = 1
            while Deposito.objects.filter(slug=s).exists():
                s = f"{base}-{i}"
                i += 1
            self.slug = s
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class MotivoAjuste(models.Model):
    """Motivo categórico para ajustes de estoque."""
    codigo = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=120)
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class StockMovement(models.Model):
    """Movimento de estoque: entrada, saída ou ajuste."""
    class Tipo(models.TextChoices):
        IN = 'IN', 'Entrada'
        OUT = 'OUT', 'Saída'
        ADJUST = 'ADJUST', 'Ajuste'

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='movimentos_estoque')
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    quantidade = models.IntegerField()
    origem_slug = models.CharField(max_length=64, blank=True, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, blank=True, null=True, related_name='movimentos_estoque')
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    observacao = models.TextField(blank=True)
    deposito = models.ForeignKey(Deposito, on_delete=models.SET_NULL, blank=True, null=True)
    motivo_ajuste = models.ForeignKey(MotivoAjuste, on_delete=models.SET_NULL, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} {self.quantidade} {self.produto.slug}"


class StockReceipt(models.Model):
    """Recebimento de estoque, possivelmente vinculado a uma compra."""
    fornecedor = models.CharField(max_length=120, blank=True)
    fornecedor_ref = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='recebimentos', blank=True, null=True)
    documento = models.CharField(max_length=64, blank=True)
    observacao = models.TextField(blank=True)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    deposito = models.ForeignKey(Deposito, on_delete=models.SET_NULL, blank=True, null=True)
    compra = models.ForeignKey('compras.PurchaseOrder', on_delete=models.SET_NULL, blank=True, null=True, related_name='recebimentos')
    criado_em = models.DateTimeField(default=timezone.now)
    estornado_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.documento or 'recebimento'}"


class StockReceiptItem(models.Model):
    """Item de recebimento, com quantidade e custo unitário."""
    recebimento = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)
