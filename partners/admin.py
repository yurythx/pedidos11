"""
Django Admin para app Partners.
"""
from django.contrib import admin
from .models import Cliente, Fornecedor


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'tipo_pessoa', 'telefone', 'email', 'is_active']
    list_filter = ['tipo_pessoa', 'is_active', 'created_at']
    search_fields = ['nome', 'cpf_cnpj', 'email', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'tipo_pessoa', 'cpf_cnpj')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
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


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'nome_fantasia', 'cpf_cnpj', 'telefone', 'email', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['razao_social', 'nome_fantasia', 'cpf_cnpj', 'email', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('razao_social', 'nome_fantasia', 'slug', 'cpf_cnpj')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'site')
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
