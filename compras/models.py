"""Modelos de Compras (PurchaseOrder e itens).

Gerenciam ordens de compra, itens, custos e vínculos com fornecedor,
centro de custo e depósito, além de campos auxiliares para pagamentos/recebimentos.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from cadastro.models import Supplier
from catalogo.models import Produto
import secrets


class PurchaseOrder(models.Model):
    """Ordem de compra com status, totais e vínculos operacionais."""
    class Status(models.TextChoices):
        PENDENTE = 'Pendente', 'Pendente'
        RECEBIDO = 'Recebido', 'Recebido'
        CANCELADO = 'Cancelado', 'Cancelado'
        QUITADO = 'Quitado', 'Quitado'

    slug = models.SlugField(max_length=32, unique=True, blank=True)
    fornecedor = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='compras')
    documento = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    cost_center = models.ForeignKey('financeiro.CostCenter', on_delete=models.SET_NULL, blank=True, null=True, related_name='compras')
    deposito = models.ForeignKey('estoque.Deposito', on_delete=models.SET_NULL, blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)
    recebido_em = models.DateTimeField(blank=True, null=True)
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago_em = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Gera slug único hexadecimal na criação."""
        if not self.slug:
            code = secrets.token_hex(6)
            while PurchaseOrder.objects.filter(slug=code).exists():
                code = secrets.token_hex(6)
            self.slug = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO-{self.slug}"


class PurchaseItem(models.Model):
    """Item de compra vinculado à ordem, com quantidade e custo unitário."""
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(default=timezone.now)

    def subtotal(self):
        """Subtotal = quantidade * custo_unitário."""
        from decimal import Decimal
        return Decimal(self.quantidade) * self.custo_unitario
