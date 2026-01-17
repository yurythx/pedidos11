"""
Django Admin para app Stock.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import Deposito, Saldo, Movimentacao, Lote


class LoteInline(admin.TabularInline):
    """Inline para ver lotes vinculados a um produto."""
    model = Lote
    extra = 0
    readonly_fields = ['codigo_lote', 'deposito', 'quantidade_atual', 'data_validade']
    fields = ['codigo_lote', 'deposito', 'quantidade_atual', 'data_validade']
    can_delete = False
    show_change_link = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(quantidade_atual__gt=0)


class SaldoInline(admin.TabularInline):
    """Inline para ver saldo consolidado por depósito."""
    model = Saldo
    extra = 0
    readonly_fields = ['deposito', 'quantidade', 'updated_at']
    fields = ['deposito', 'quantidade', 'updated_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Deposito)
class DepositoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'is_padrao', 'is_active']
    list_filter = ['is_padrao', 'is_active']
    search_fields = ['nome', 'codigo']
    readonly_fields = ['id', 'created_at', 'updated_at']


class StatusValidadeFilter(admin.SimpleListFilter):
    """Filtro customizado por status de validade."""
    title = 'Status de Validade'
    parameter_name = 'status_validade'
    
    def lookups(self, request, model_admin):
        return (
            ('vencido', 'Vencidos'),
            ('critico', 'Crítico (≤ 7 dias)'),
            ('atencao', 'Atenção (8-30 dias)'),
            ('ok', 'OK (> 30 dias)'),
        )
    
    def queryset(self, request, queryset):
        hoje = timezone.now().date()
        
        if self.value() == 'vencido':
            return queryset.filter(data_validade__lt=hoje)
        elif  self.value() == 'critico':
            return queryset.filter(
                data_validade__gte=hoje,
                data_validade__lte=hoje + timedelta(days=7)
            )
        elif self.value() == 'atencao':
            return queryset.filter(
                data_validade__gt=hoje + timedelta(days=7),
                data_validade__lte=hoje + timedelta(days=30)
            )
        elif self.value() == 'ok':
            return queryset.filter(data_validade__gt=hoje + timedelta(days=30))


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    """Admin customizado para Lotes com alertas de validade."""
    list_display = ['codigo_lote', 'produto', 'deposito', 'quantidade_atual', 'data_validade', 'status_badge', 'dias_restantes']
    list_filter = ['deposito', 'produto__categoria', StatusValidadeFilter]
    search_fields = ['codigo_lote', 'produto__nome', 'produto__sku']
    readonly_fields = ['id', 'quantidade_atual', 'dias_ate_vencer', 'status_validade', 'percentual_consumido', 'created_at', 'updated_at']
    date_hierarchy = 'data_validade'
    autocomplete_fields = ['produto', 'deposito']
    
    fieldsets = (
        ('Informações do Lote', {
            'fields': ('produto', 'deposito', 'codigo_lote')
        }),
        ('Datas', {
            'fields': ('data_fabricacao', 'data_validade')
        }),
        ('Quantidade', {
            'fields': ('quantidade_atual', 'percentual_consumido'),
            'description': 'Quantidade atualizada automaticamente pelas movimentações.'
        }),
        ('Status de Validade', {
            'fields': ('dias_ate_vencer', 'status_validade'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Exibe status com badge colorido."""
        status = obj.status_validade
        colors = {
            'VENCIDO': '#f44336',    # Vermelho
            'CRITICO': '#FF5722',    # Vermelho alaranjado
            'ATENCAO': '#FF9800',    # Laranja
            'OK': '#4CAF50',         # Verde
        }
        color = colors.get(status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'
    
    def dias_restantes(self, obj):
        """Exibe dias restantes com formatação condicional."""
        dias = obj.dias_ate_vencer
        if dias  < 0:
            return format_html('<span style="color: #f44336; font-weight: bold;">Vencido há {} dias</span>', abs(dias))
        elif dias == 0:
            return format_html('<span style="color: #FF5722; font-weight: bold;">Vence hoje!</span>')
        elif dias <= 7:
            return format_html('<span style="color: #FF5722; font-weight: bold;">{} dias</span>', dias)
        elif dias <= 30:
            return format_html('<span style="color: #FF9800;">{} dias</span>', dias)
        else:
            return f'{dias} dias'
    dias_restantes.short_description = 'Dias p/ Vencer'
    dias_restantes.admin_order_field = 'data_validade'
    
    def has_delete_permission(self, request, obj=None):
        """Permite deletar apenas lotes zerados."""
        if obj and obj.quantidade_atual > 0:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Saldo)
class SaldoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'deposito', 'quantidade', 'updated_at']
    list_filter = ['deposito']
    search_fields = ['produto__nome', 'produto__sku']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Saldo é gerado automaticamente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar saldo diretamente
        return False


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'produto', 'deposito', 'lote_display', 'quantidade', 'documento', 'created_at']
    list_filter = ['tipo', 'deposito', 'created_at']
    search_fields = ['produto__nome', 'documento', 'observacao', 'lote__codigo_lote']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['produto', 'deposito', 'lote']
    
    def lote_display(self, obj):
        """Exibe lote se houver."""
        if obj.lote:
            return format_html(
                '<a href="/admin/stock/lote/{}/change/">{}</a>',
                obj.lote.id,
                obj.lote.codigo_lote
            )
        return '-'
    lote_display.short_description = 'Lote'
    
    def has_change_permission(self, request, obj=None):
        # Movimentações são imutáveis
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Movimentações são imutáveis
        return False
