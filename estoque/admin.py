"""Admin de Estoque: movimentos, recebimentos e metadados.

Inclui exportações CSV e edição inline de itens de recebimento.
"""
from django.contrib import admin
from .models import StockMovement, Deposito, MotivoAjuste, StockReceipt, StockReceiptItem


class StockMovementAdmin(admin.ModelAdmin):
    """Admin de movimentos com exportação CSV."""
    list_display = ("produto", "tipo", "quantidade", "origem_slug", "pedido", "responsavel", "criado_em")
    list_filter = ("tipo", "produto")
    search_fields = ("produto__slug", "origem_slug", "pedido__slug")
    date_hierarchy = "criado_em"
    @admin.action(description="Exportar movimentos selecionados em CSV")
    def exportar_movimentos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["produto,tipo,quantidade,origem_slug,pedido,responsavel,deposito,motivo_ajuste,criado_em"]
        for m in queryset.select_related("produto", "pedido", "responsavel", "deposito", "motivo_ajuste"):
            rows.append(f"{m.produto.slug},{m.tipo},{m.quantidade},{m.origem_slug or ''},{m.pedido.slug if m.pedido else ''},{m.responsavel.username if m.responsavel else ''},{m.deposito.nome if m.deposito else ''},{m.motivo_ajuste.codigo if m.motivo_ajuste else ''},{m.criado_em.isoformat()}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"movimentos_estoque.csv\"'
        return resp
    actions = ["exportar_movimentos_csv"]


admin.site.register(StockMovement, StockMovementAdmin)


class DepositoAdmin(admin.ModelAdmin):
    """Admin de depósitos com slug readonly."""
    list_display = ("nome", "slug", "endereco", "criado_em")
    search_fields = ("nome", "slug")
    readonly_fields = ("slug",)
    autocomplete_fields = ("endereco",)


class MotivoAjusteAdmin(admin.ModelAdmin):
    """Admin de motivos de ajuste."""
    list_display = ("codigo", "nome", "criado_em")
    search_fields = ("codigo", "nome")


class StockReceiptItemInline(admin.TabularInline):
    """Inline para itens dentro do recebimento."""
    model = StockReceiptItem
    extra = 0
    fields = ("produto", "quantidade", "custo_unitario")
    raw_id_fields = ("produto",)
    show_change_link = True


class StockReceiptAdmin(admin.ModelAdmin):
    """Admin de recebimentos com exportação CSV."""
    list_display = ("documento", "fornecedor", "fornecedor_ref", "deposito", "compra", "responsavel", "criado_em", "estornado_em")
    list_filter = ("deposito", "fornecedor_ref", "compra")
    search_fields = ("documento", "fornecedor", "compra__slug")
    date_hierarchy = "criado_em"
    autocomplete_fields = ("fornecedor_ref", "deposito", "compra", "responsavel")
    inlines = [StockReceiptItemInline]
    @admin.action(description="Exportar recebimentos selecionados em CSV")
    def exportar_recebimentos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["documento,fornecedor,fornecedor_ref,deposito,compra,responsavel,criado_em,estornado_em"]
        for r in queryset.select_related("fornecedor_ref", "deposito", "compra", "responsavel"):
            rows.append(f"{r.documento},{r.fornecedor},{r.fornecedor_ref.nome if r.fornecedor_ref else ''},{r.deposito.nome if r.deposito else ''},{r.compra.slug if r.compra else ''},{r.responsavel.username if r.responsavel else ''},{r.criado_em.isoformat()},{r.estornado_em.isoformat() if r.estornado_em else ''}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"recebimentos.csv\"'
        return resp
    actions = ["exportar_recebimentos_csv"]


class StockReceiptItemAdmin(admin.ModelAdmin):
    """Admin para itens de recebimento."""
    list_display = ("recebimento", "produto", "quantidade", "custo_unitario", "criado_em")
    search_fields = ("recebimento__documento", "produto__slug")
    raw_id_fields = ("recebimento", "produto")


admin.site.register(Deposito, DepositoAdmin)
admin.site.register(MotivoAjuste, MotivoAjusteAdmin)
admin.site.register(StockReceipt, StockReceiptAdmin)
admin.site.register(StockReceiptItem, StockReceiptItemAdmin)
