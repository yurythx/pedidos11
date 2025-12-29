from django.contrib import admin
from .models import StockMovement


class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("produto", "tipo", "quantidade", "origem_slug", "pedido", "responsavel", "criado_em")
    list_filter = ("tipo", "produto")
    search_fields = ("produto__slug", "origem_slug", "pedido__slug")
    date_hierarchy = "criado_em"


admin.site.register(StockMovement, StockMovementAdmin)
