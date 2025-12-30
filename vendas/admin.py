from django.contrib import admin
"""Admin de Vendas: gestão de pedidos.

Inclui actions para disponibilidade de pedidos, status, recalcular totais,
gerar títulos AR e exportar CSV de pedidos.
"""
from financeiro.services import FinanceiroService
from .models import Pedido, ItemPedido


@admin.action(description="Marcar pedidos como Pendente")
def marcar_pendente(modeladmin, request, queryset):
    updated = queryset.update(status=Pedido.Status.PENDENTE)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Pendente.")


@admin.action(description="Marcar pedidos como Preparando")
def marcar_preparando(modeladmin, request, queryset):
    updated = queryset.update(status=Pedido.Status.PREPARANDO)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Preparando.")


@admin.action(description="Marcar pedidos como Enviado")
def marcar_enviado(modeladmin, request, queryset):
    updated = queryset.update(status=Pedido.Status.ENVIADO)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Enviado.")


@admin.action(description="Marcar pedidos como Entregue")
def marcar_entregue(modeladmin, request, queryset):
    updated = queryset.update(status=Pedido.Status.ENTREGUE)
    modeladmin.message_user(request, f"{updated} pedido(s) marcado(s) como Entregue.")


@admin.action(description="Recalcular totais dos pedidos selecionados")
def recalcular_totais(modeladmin, request, queryset):
    count = 0
    for pedido in queryset.prefetch_related("itens"):
        total = sum(i.quantidade * i.preco_unitario for i in pedido.itens.all())
        pedido.total = total
        pedido.save(update_fields=["total"])
        count += 1
    modeladmin.message_user(request, f"Totais recalculados para {count} pedido(s).")


class ItemPedidoInline(admin.TabularInline):
    """Inline para itens dentro do Pedido."""
    model = ItemPedido
    extra = 0
    fields = ("produto", "quantidade", "preco_unitario")
    readonly_fields = ()
    show_change_link = True


class PedidoAdmin(admin.ModelAdmin):
    """Admin de Pedido com ações de status, totais, AR e exportação CSV."""
    list_display = ("slug", "usuario", "status", "total", "data_criacao")
    list_filter = ("status", "data_criacao")
    search_fields = ("usuario__username", "slug")
    date_hierarchy = "data_criacao"
    actions = [marcar_pendente, marcar_preparando, marcar_enviado, marcar_entregue, recalcular_totais]
    inlines = [ItemPedidoInline]

    @admin.action(description="Gerar Título AR (a receber)")
    def gerar_titulo_ar(self, request, queryset):
        count = 0
        for pedido in queryset:
            FinanceiroService.registrar_venda_a_prazo(pedido)
            count += 1
        self.message_user(request, f"Títulos AR gerados/garantidos para {count} pedido(s).")
    actions = [marcar_pendente, marcar_preparando, marcar_enviado, marcar_entregue, recalcular_totais, gerar_titulo_ar]

    @admin.action(description="Exportar pedidos selecionados em CSV")
    def exportar_pedidos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["slug,usuario,status,total,data_criacao"]
        for p in queryset.select_related("usuario"):
            rows.append(f"{p.slug},{p.usuario.username if p.usuario else ''},{p.status},{p.total:.2f},{p.data_criacao.isoformat()}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"pedidos.csv\"'
        return resp
    actions = [marcar_pendente, marcar_preparando, marcar_enviado, marcar_entregue, recalcular_totais, gerar_titulo_ar, exportar_pedidos_csv]



admin.site.register(Pedido, PedidoAdmin)


class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "produto", "quantidade", "preco_unitario")
    search_fields = ("pedido__slug", "produto__slug")
    raw_id_fields = ("pedido", "produto")


admin.site.register(ItemPedido, ItemPedidoAdmin)
