from django.contrib import admin
from .models import LedgerEntry


class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("pedido", "descricao", "debit_account", "credit_account", "valor", "criado_em")
    search_fields = ("pedido__slug", "descricao", "debit_account", "credit_account")
    date_hierarchy = "criado_em"


admin.site.register(LedgerEntry, LedgerEntryAdmin)
