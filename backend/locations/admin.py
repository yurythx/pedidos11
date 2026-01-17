"""
Django Admin para app Locations.
"""
from django.contrib import admin
from .models import Endereco


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['cep', 'logradouro', 'numero', 'cidade', 'uf', 'content_type', 'object_id']
    list_filter = ['uf', 'cidade']
    search_fields = ['cep', 'logradouro', 'bairro', 'cidade']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro')
        }),
        ('Localização', {
            'fields': ('cidade', 'uf')
        }),
        ('Vinculação', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
