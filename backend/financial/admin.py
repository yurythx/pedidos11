"""
Django Admin para app Financial.
"""
from django.contrib import admin
from .models import ContaReceber, ContaPagar


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'cliente', 'valor_total', 'status', 'data_vencimento', 'esta_vencida']
    list_filter = ['status', 'data_vencimento', 'created_at']
    search_fields = ['descricao', 'cliente__nome', 'venda__numero']
    readonly_fields = ['id', 'valor_total', 'dias_atraso', 'esta_vencida', 'created_at', 'updated_at']
    date_hierarchy = 'data_vencimento'
    actions = ['marcar_como_paga']
    
    def marcar_como_paga(self, request, queryset):
        from financial.services import FinanceiroService
        contador = 0
        for conta in queryset.filter(status__in=['PENDENTE', 'VENCIDA']):
            try:
                FinanceiroService.baixar_conta_receber(conta.id)
                contador += 1
            except Exception as e:
                self.message_user(request, f'Erro na conta {conta.id}: {str(e)}', level='error')
        
        if contador > 0:
            self.message_user(request, f'{contador} conta(s) baixada(s) com sucesso.', level='success')
    marcar_como_paga.short_description = 'Marcar selecionadas como PAGAS'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'cliente', 'venda')
        }),
        ('Valores', {
            'fields': ('valor_original', 'valor_juros', 'valor_multa', 'valor_desconto', 'valor_total')
        }),
        ('Datas', {
            'fields': ('data_emissao', 'data_vencimento', 'data_pagamento', 'dias_atraso', 'esta_vencida')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'fornecedor', 'valor_total', 'status', 'data_vencimento', 'esta_vencida']
    list_filter = ['status', 'data_vencimento', 'created_at']
    search_fields = ['descricao', 'fornecedor__razao_social']
    readonly_fields = ['id', 'valor_total', 'dias_atraso', 'esta_vencida', 'created_at', 'updated_at']
    date_hierarchy = 'data_vencimento'
    actions = ['marcar_como_paga']
    
    def marcar_como_paga(self, request, queryset):
        from financial.services import FinanceiroService
        contador = 0
        for conta in queryset.filter(status__in=['PENDENTE', 'VENCIDA']):
            try:
                FinanceiroService.baixar_conta_pagar(conta.id)
                contador += 1
            except Exception as e:
                self.message_user(request, f'Erro na conta {conta.id}: {str(e)}', level='error')
        
        if contador > 0:
            self.message_user(request, f'{contador} conta(s) baixada(s) com sucesso.', level='success')
    marcar_como_paga.short_description = 'Marcar selecionadas como PAGAS'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'fornecedor')
        }),
        ('Valores', {
            'fields': ('valor_original', 'valor_juros', 'valor_multa', 'valor_desconto', 'valor_total')
        }),
        ('Datas', {
            'fields': ('data_emissao', 'data_vencimento', 'data_pagamento', 'dias_atraso', 'esta_vencida')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
