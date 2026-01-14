"""
Django Admin para app Restaurant.
"""
from django.contrib import admin
from .models import SetorImpressao, Mesa, Comanda


@admin.register(SetorImpressao)
class SetorImpressaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'cor', 'ordem', 'is_active']
    list_filter = ['is_active']
    search_fields = ['nome', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    ordering = ['ordem', 'nome']


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'capacidade', 'status', 'venda_atual', 'esta_livre', 'esta_ocupada']
    list_filter = ['status', 'capacidade']
    search_fields = ['numero']
    readonly_fields = ['id', 'esta_livre', 'esta_ocupada', 'created_at', 'updated_at']
    ordering = ['numero']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'capacidade', 'status')
        }),
        ('Venda Atual', {
            'fields': ('venda_atual', 'esta_livre', 'esta_ocupada')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'status', 'venda_atual', 'esta_livre', 'esta_em_uso']
    list_filter = ['status']
    search_fields = ['codigo']
    readonly_fields = ['id', 'esta_livre', 'esta_em_uso', 'created_at', 'updated_at']
    ordering = ['codigo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'status')
        }),
        ('Venda Atual', {
            'fields': ('venda_atual', 'esta_livre', 'esta_em_uso')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
