"""
Django Admin para NFe - Projeto Nix.
"""
from django.contrib import admin
from .models import ProdutoFornecedor, NotaFiscal, ItemNotaFiscal


class ItemNotaFiscalInline(admin.TabularInline):
    model = ItemNotaFiscal
    extra = 0
    readonly_fields = ['valor_total', 'base_icms', 'valor_icms']


@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'serie', 'modelo', 'status', 'valor_total_nota', 'data_emissao', 'chave_acesso']
    list_filter = ['status', 'modelo', 'ambiente', 'data_emissao']
    search_fields = ['numero', 'chave_acesso', 'cliente_nome']
    readonly_fields = ['chave_acesso', 'protocolo_autorizacao', 'xml_processado', 'data_emissao']
    inlines = [ItemNotaFiscalInline]
    date_hierarchy = 'data_emissao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('venda', 'modelo', 'serie', 'numero', 'chave_acesso')
        }),
        ('Status e Autorização', {
            'fields': ('status', 'ambiente', 'protocolo_autorizacao', 'data_emissao')
        }),
        ('Totais', {
            'fields': ('base_icms', 'valor_icms', 'valor_total_nota')
        }),
        ('XML e Documentos', {
            'fields': ('xml_processado',),
            'classes': ('collapse',)
        }),
    )


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
