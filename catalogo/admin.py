from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Categoria, Produto, ProdutoImagem, ProdutoAtributo, ProdutoAtributoValor, ProdutoVariacao


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

    @admin.action(description="Exportar produtos selecionados em CSV")
    def exportar_produtos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["nome,categoria,preco,disponivel,slug"]
        for pr in queryset.select_related("categoria"):
            rows.append(f"{pr.nome},{pr.categoria.nome if pr.categoria else ''},{pr.preco:.2f},{pr.disponivel},{pr.slug}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="produtos.csv"'
        return resp
    actions = [marcar_disponiveis, marcar_indisponiveis, exportar_produtos_csv]

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


class ProdutoImagemAdmin(admin.ModelAdmin):
    list_display = ("produto", "alt", "pos", "criado_em")
    search_fields = ("produto__slug", "alt")
    autocomplete_fields = ("produto",)


class ProdutoAtributoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "tipo", "criado_em")
    search_fields = ("codigo", "nome")
    list_filter = ("tipo",)


class ProdutoAtributoValorAdmin(admin.ModelAdmin):
    list_display = ("produto", "atributo", "valor_texto", "valor_numero", "valor_bool", "criado_em")
    search_fields = ("produto__slug", "atributo__codigo")
    autocomplete_fields = ("produto", "atributo")


class ProdutoVariacaoAdmin(admin.ModelAdmin):
    list_display = ("produto", "sku", "nome", "preco", "custo", "disponivel", "criado_em")
    list_filter = ("disponivel",)
    search_fields = ("produto__slug", "sku", "nome")
    autocomplete_fields = ("produto",)


admin.site.register(ProdutoImagem, ProdutoImagemAdmin)
admin.site.register(ProdutoAtributo, ProdutoAtributoAdmin)
admin.site.register(ProdutoAtributoValor, ProdutoAtributoValorAdmin)
admin.site.register(ProdutoVariacao, ProdutoVariacaoAdmin)
