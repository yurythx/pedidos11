"""
Django Admin para NFe - Projeto Nix.
"""
from django.contrib import admin
from .models import ProdutoFornecedor


@admin.register(ProdutoFornecedor)
class ProdutoFornecedorAdmin(admin.ModelAdmin):
    """Admin para vínculos produto-fornecedor."""
    
    list_display = [
        'produto', 'codigo_no_fornecedor', 'nome_fornecedor',
        'fator_conversao', 'ultimo_preco', 'preco_convertido_display',
        'data_ultima_compra'
    ]
    list_filter = ['nome_fornecedor', 'data_ultima_compra']
    search_fields = [
        'produto__nome', 'codigo_no_fornecedor',
        'cnpj_fornecedor', 'nome_fornecedor'
    ]
    autocomplete_fields = ['produto']
    readonly_fields = ['data_ultima_compra', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Produto', {
            'fields': ('produto',)
        }),
        ('Fornecedor', {
            'fields': ('cnpj_fornecedor', 'nome_fornecedor', 'codigo_no_fornecedor')
        }),
        ('Conversão e Preço', {
            'fields': ('fator_conversao', 'ultimo_preco')
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('data_ultima_compra', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preco_convertido_display(self, obj):
        """Mostra preço unitário convertido."""
        preco = obj.preco_unitario_convertido
        if preco:
            return f'R$ {preco:.2f}/un'
        return '-'
    preco_convertido_display.short_description = 'Preço Unitário'
