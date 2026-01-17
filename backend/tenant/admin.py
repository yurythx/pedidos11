"""
Django Admin para app Tenant.
"""
from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome_fantasia', 'razao_social', 'cnpj', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nome_fantasia', 'razao_social', 'cnpj']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_fantasia', 'razao_social', 'slug')
        }),
        ('Documentos', {
            'fields': ('cnpj', 'inscricao_estadual', 'inscricao_municipal')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'website')
        }),
        ('Identidade Visual', {
            'fields': ('logo', 'cor_primaria', 'cor_secundaria'),
            'description': 'Personalização da interface do usuário (tema e logo).'
        }),
        ('Configurações do Sistema', {
            'fields': ('moeda', 'fuso_horario'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
