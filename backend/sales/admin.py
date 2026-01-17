"""
Django Admin para app Sales.
"""
from django.contrib import admin
from .models import Venda, ItemVenda, ItemVendaComplemento


class ItemVendaComplementoInline(admin.TabularInline):
    model = ItemVendaComplemento
    extra = 0
    readonly_fields = ['subtotal', 'created_at']
    fields = ['complemento', 'quantidade', 'preco_unitario', 'subtotal']


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ['subtotal', 'total_sem_desconto', 'created_at']
    fields = ['produto', 'quantidade', 'preco_unitario', 'custo_unitario', 'desconto', 'subtotal', 'status_producao']


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'vendedor', 'status', 'total_liquido', 'data_emissao']
    list_filter = ['status', 'tipo_pagamento', 'data_emissao']
    search_fields = ['numero', 'cliente__nome', 'vendedor__username', 'slug']
    readonly_fields = ['id', 'numero', 'slug', 'total_bruto', 'total_desconto', 'total_liquido', 
                      'quantidade_itens', 'created_at', 'updated_at']
    date_hierarchy = 'data_emissao'
    inlines = [ItemVendaInline]
    actions = ['finalizar_vendas', 'cancelar_vendas']
    
    def finalizar_vendas(self, request, queryset):
        from sales.services import VendaService
        from stock.models import Deposito
        
        # Busca depósito padrão para baixar estoque
        deposito = Deposito.objects.filter(is_active=True).first()
        if not deposito:
            self.message_user(request, 'Erro: Nenhum depósito ativo encontrado.', level='error')
            return
            
        contador = 0
        for venda in queryset.filter(status__in=['ORCAMENTO', 'PENDENTE']):
            try:
                VendaService.finalizar_venda(venda.id, deposito.id, request.user.username)
                contador += 1
            except Exception as e:
                self.message_user(request, f'Erro na venda #{venda.numero}: {str(e)}', level='error')
                
        if contador > 0:
            self.message_user(request, f'{contador} venda(s) finalizada(s) com sucesso.', level='success')
    finalizar_vendas.short_description = 'Finalizar selecionadas (Baixar Estoque)'
    
    def cancelar_vendas(self, request, queryset):
        from sales.services import VendaService
        contador = 0
        for venda in queryset.filter(status='FINALIZADA'):
            try:
                VendaService.cancelar_venda(venda.id, motivo='Cancelamento Administrativo', usuario=request.user.username)
                contador += 1
            except Exception as e:
                self.message_user(request, f'Erro na venda #{venda.numero}: {str(e)}', level='error')
                
        if contador > 0:
            self.message_user(request, f'{contador} venda(s) cancelada(s) (Estoque Devolvido).', level='success')
    cancelar_vendas.short_description = 'Cancelar selecionadas (Devolver Estoque)'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'slug', 'cliente', 'vendedor', 'status')
        }),
        ('Totais', {
            'fields': ('total_bruto', 'total_desconto', 'total_liquido', 'quantidade_itens')
        }),
        ('Pagamento', {
            'fields': ('tipo_pagamento',)
        }),
        ('Datas', {
            'fields': ('data_emissao', 'data_finalizacao', 'data_cancelamento')
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


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ['venda', 'produto', 'quantidade', 'preco_unitario', 'custo_unitario', 'subtotal', 'status_producao']
    list_filter = ['status_producao', 'created_at']
    search_fields = ['venda__numero', 'produto__nome']
    readonly_fields = ['id', 'subtotal', 'total_sem_desconto', 'percentual_desconto', 
                      'total_complementos', 'created_at', 'updated_at']
    inlines = [ItemVendaComplementoInline]


@admin.register(ItemVendaComplemento)
class ItemVendaComplementoAdmin(admin.ModelAdmin):
    list_display = ['item_pai', 'complemento', 'quantidade', 'preco_unitario', 'subtotal']
    search_fields = ['item_pai__venda__numero', 'complemento__nome']
    readonly_fields = ['id', 'subtotal', 'possui_produto_vinculado', 'created_at', 'updated_at']
