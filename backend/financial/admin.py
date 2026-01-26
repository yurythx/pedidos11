"""
Django Admin para app Financial.
"""
from django.contrib import admin
from .models import ContaReceber, ContaPagar, Caixa, SessaoCaixa, MovimentoCaixa


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'serial', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'serial']


class MovimentoCaixaInline(admin.TabularInline):
    model = MovimentoCaixa
    extra = 0
    readonly_fields = ['data_hora']


@admin.register(SessaoCaixa)
class SessaoCaixaAdmin(admin.ModelAdmin):
    list_display = ['id', 'caixa', 'operador', 'status', 'data_abertura', 'data_fechamento', 'saldo_final_calculado', 'diferenca_caixa']
    list_filter = ['status', 'data_abertura', 'caixa']
    search_fields = ['operador__username', 'operador__first_name']
    readonly_fields = ['data_abertura', 'saldo_final_calculado', 'diferenca_caixa']
    inlines = [MovimentoCaixaInline]


@admin.register(MovimentoCaixa)
class MovimentoCaixaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'sessao', 'valor', 'descricao', 'data_hora']
    list_filter = ['tipo', 'data_hora']
    search_fields = ['descricao', 'sessao__id']


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
