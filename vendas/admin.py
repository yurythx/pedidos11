from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Categoria, Produto, Pedido, ItemPedido


@admin.action(description="Marcar produtos como disponíveis")
def marcar_disponiveis(modeladmin, request, queryset):
    updated = queryset.update(disponivel=True)
    modeladmin.message_user(request, f"{updated} produto(s) marcado(s) como disponíveis.")


@admin.action(description="Marcar produtos como indisponíveis")
def marcar_indisponiveis(modeladmin, request, queryset):
    updated = queryset.update(disponivel=False)
    modeladmin.message_user(request, f"{updated} produto(s) marcado(s) como indisponíveis.")


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "preco", "disponivel", "slug", "imagem_preview")
    list_filter = ("categoria", "disponivel")
    search_fields = ("nome", "descricao")
    readonly_fields = ("slug", "imagem_preview")
    actions = [marcar_disponiveis, marcar_indisponiveis]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("categoria")

    def imagem_preview(self, obj):
        if obj.imagem:
            return mark_safe(f'<img src="{obj.imagem.url}" style="height:60px" />')
        return "-"
    imagem_preview.short_description = "Imagem"


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 0
    fields = ("nome", "preco", "disponivel")
    show_change_link = True


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "total_produtos")
    search_fields = ("nome",)
    readonly_fields = ("slug",)
    inlines = [ProdutoInline]

    def total_produtos(self, obj):
        return obj.produtos.count()
    total_produtos.short_description = "Qtde Produtos"


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Categoria, CategoriaAdmin)


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
    model = ItemPedido
    extra = 0
    fields = ("produto", "quantidade", "preco_unitario")
    readonly_fields = ()
    show_change_link = True


class PedidoAdmin(admin.ModelAdmin):
    list_display = ("slug", "usuario", "status", "total", "data_criacao")
    list_filter = ("status", "data_criacao")
    search_fields = ("usuario__username", "slug")
    date_hierarchy = "data_criacao"
    actions = [marcar_pendente, marcar_preparando, marcar_enviado, marcar_entregue, recalcular_totais]
    inlines = [ItemPedidoInline]


admin.site.register(Pedido, PedidoAdmin)
