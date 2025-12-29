from decimal import Decimal
from django.db import models
from django.conf import settings


class Account(models.Model):
    class Tipo(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        PASSIVO = 'PASSIVO', 'Passivo'
        RECEITA = 'RECEITA', 'Receita'
        DESPESA = 'DESPESA', 'Despesa'
        PATRIMONIO = 'PATRIMONIO', 'Patrimônio'

    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)

    def __str__(self):
        return f"{self.codigo} {self.nome}"


class CostCenter(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.codigo} {self.nome}"


class UserDefaultCostCenter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='default_cost_center')
    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, related_name='users_default')
    class Meta:
        unique_together = ('user', 'cost_center')


class LedgerEntry(models.Model):
    pedido = models.ForeignKey('vendas.Pedido', on_delete=models.SET_NULL, blank=True, null=True, related_name='lancamentos_financeiros')
    descricao = models.CharField(max_length=200)
    debit_account = models.CharField(max_length=60)
    credit_account = models.CharField(max_length=60)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    debit_account_ref = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name='debitos')
    credit_account_ref = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name='creditos')
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, blank=True, null=True, related_name='lancamentos')

    def __str__(self):
        return f"{self.descricao} {self.valor}"
