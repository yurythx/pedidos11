"""
Django Admin para app Partners.
"""
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Cliente, Fornecedor
from locations.models import Endereco


class EnderecoInline(GenericTabularInline):
    """Inline genérico para endereços."""
    model = Endereco
    extra = 1
    fields = ['tipo', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'tipo_pessoa', 'telefone', 'email', 'is_active']
    list_filter = ['tipo_pessoa', 'is_active', 'created_at']
    search_fields = ['nome', 'cpf_cnpj', 'email', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    inlines = [EnderecoInline]
    
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
    inlines = [EnderecoInline]
    
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
