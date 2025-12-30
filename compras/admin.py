"""Admin de Compras: ordens e itens com ações de AP e totais."""
from django.contrib import admin
from .models import PurchaseOrder, PurchaseItem
from financeiro.services import FinanceiroService


class PurchaseItemInline(admin.TabularInline):
    """Inline de itens dentro da ordem de compra."""
    model = PurchaseItem
    extra = 0
    fields = ("produto", "quantidade", "custo_unitario")
    raw_id_fields = ("produto",)
    show_change_link = True


class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin de ordem de compra com geração de AP e recalcular total."""
    list_display = ("slug", "fornecedor", "documento", "status", "total", "responsavel", "cost_center", "deposito", "criado_em", "recebido_em", "valor_pago", "pago_em")
    list_filter = ("status", "fornecedor", "cost_center", "deposito")
    search_fields = ("slug", "documento", "fornecedor__nome")
    date_hierarchy = "criado_em"
    autocomplete_fields = ("fornecedor", "responsavel", "cost_center", "deposito")
    inlines = [PurchaseItemInline]

    @admin.action(description="Gerar Título AP (a pagar)")
    def gerar_titulo_ap(self, request, queryset):
        count = 0
        for po in queryset:
            FinanceiroService.registrar_compra(po)
            count += 1
        self.message_user(request, f"Títulos AP gerados/garantidos para {count} compra(s).")
    @admin.action(description="Recalcular total da compra")
    def recalcular_total(self, request, queryset):
        count = 0
        for po in queryset.prefetch_related("itens"):
            total = sum((i.subtotal() for i in po.itens.all()), 0)
            po.total = total
            po.save(update_fields=["total"])
            count += 1
        self.message_user(request, f"Totais recalculados para {count} compra(s).")
    actions = ["gerar_titulo_ap", "recalcular_total"]


class PurchaseItemAdmin(admin.ModelAdmin):
    """Admin para item de compra."""
    list_display = ("order", "produto", "quantidade", "custo_unitario", "criado_em")
    search_fields = ("order__slug", "produto__slug")
    raw_id_fields = ("order", "produto")


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseItem, PurchaseItemAdmin)
