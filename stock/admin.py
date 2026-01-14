"""
Django Admin para app Stock.
"""
from django.contrib import admin
from .models import Deposito, Saldo, Movimentacao


@admin.register(Deposito)
class DepositoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'is_padrao', 'is_active']
    list_filter = ['is_padrao', 'is_active']
    search_fields = ['nome', 'codigo']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Saldo)
class SaldoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'deposito', 'quantidade', 'custo_medio', 'updated_at']
    list_filter = ['deposito']
    search_fields = ['produto__nome', 'produto__sku']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Saldo é gerado automaticamente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar saldo diretamente
        return False


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'produto', 'deposito', 'quantidade', 'documento', 'created_at']
    list_filter = ['tipo', 'deposito', 'created_at']
    search_fields = ['produto__nome', 'documento', 'observacao']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def has_change_permission(self, request, obj=None):
        # Movimentações são imutáveis
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Movimentações são imutáveis
        return False
