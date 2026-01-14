"""
Django Admin para app Catalog.
"""
from django.contrib import admin
from .models import Categoria, Produto, GrupoComplemento, Complemento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'parent', 'slug', 'ordem', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['nome', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    ordering = ['ordem', 'nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sku', 'categoria', 'preco_venda', 'tipo', 'destaque', 'is_active']
    list_filter = ['tipo', 'categoria', 'destaque', 'is_active', 'imprimir_producao']
    search_fields = ['nome', 'sku', 'codigo_barras']
    readonly_fields = ['id', 'slug', 'margem_lucro', 'lucro_unitario', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'categoria', 'tipo')
        }),
        ('Códigos', {
            'fields': ('sku', 'codigo_barras')
        }),
        ('Preços', {
            'fields': ('preco_venda', 'preco_custo', 'margem_lucro', 'lucro_unitario')
        }),
        ('Descrição', {
            'fields': ('descricao_curta', 'descricao')
        }),
        ('Food Service', {
            'fields': ('setor_impressao', 'imprimir_producao'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('permite_venda_sem_estoque', 'destaque', 'is_active')
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrupoComplemento)
class GrupoComplementoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'obrigatorio', 'min_qtd', 'max_qtd', 'ordem', 'is_active']
    list_filter = ['obrigatorio', 'is_active']
    search_fields = ['nome']
    filter_horizontal = ['produtos_vinculados']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Complemento)
class ComplementoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'grupo', 'preco_adicional', 'produto_referencia', 'is_active']
    list_filter = ['grupo', 'is_active']
    search_fields = ['nome']
    readonly_fields = ['id', 'possui_produto_vinculado', 'created_at', 'updated_at']
