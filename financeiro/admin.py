from django.contrib import admin
"""Admin Financeiro: gestão de razão, contas, centros, títulos e parcelas.

Inclui actions para receber/pagar títulos, marcar atrasados e exportar CSVs.
"""
from .models import LedgerEntry, Account, CostCenter, UserDefaultCostCenter, Title, TitleParcel
from .services import FinanceiroService
from django.utils import timezone


class LedgerEntryAdmin(admin.ModelAdmin):
    """Admin para lançamentos do razão com exportação CSV."""
    list_display = ("pedido", "descricao", "debit_account", "credit_account", "valor", "criado_em")
    search_fields = ("pedido__slug", "descricao", "debit_account", "credit_account")
    date_hierarchy = "criado_em"
    list_select_related = ("pedido", "usuario", "cost_center")
    @admin.action(description="Exportar lançamentos selecionados em CSV")
    def exportar_lancamentos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["pedido,descricao,debit_account,credit_account,valor,cost_center,criado_em"]
        for le in queryset.select_related("pedido", "cost_center"):
            rows.append(f"{le.pedido.slug if le.pedido else ''},{le.descricao},{le.debit_account},{le.credit_account},{le.valor:.2f},{le.cost_center.codigo if le.cost_center else ''},{le.criado_em.isoformat()}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"lancamentos.csv\"'
        return resp
    actions = ["exportar_lancamentos_csv"]


admin.site.register(LedgerEntry, LedgerEntryAdmin)


class AccountAdmin(admin.ModelAdmin):
    """Admin para plano de contas."""
    list_display = ("codigo", "nome", "tipo")
    list_filter = ("tipo",)
    search_fields = ("codigo", "nome")


class CostCenterAdmin(admin.ModelAdmin):
    """Admin para centros de custo."""
    list_display = ("codigo", "nome")
    search_fields = ("codigo", "nome")


class UserDefaultCostCenterAdmin(admin.ModelAdmin):
    """Admin para mapeamento de centro de custo padrão por usuário."""
    list_display = ("user", "cost_center")
    search_fields = ("user__username", "cost_center__codigo")
    autocomplete_fields = ("user", "cost_center")


class TitleParcelInline(admin.TabularInline):
    """Inline de parcelas dentro do Título."""
    model = TitleParcel
    extra = 0
    fields = ("valor", "valor_pago", "due_date", "status")
    readonly_fields = ()
    show_change_link = True


class TitleAdmin(admin.ModelAdmin):
    """Admin de Títulos com ações de baixa e exportação."""
    list_display = ("id", "tipo", "status", "pedido", "compra", "due_date", "valor", "valor_pago", "cost_center", "criado_em")
    list_filter = ("tipo", "status", "due_date", "cost_center")
    search_fields = ("pedido__slug", "compra__slug", "descricao")
    date_hierarchy = "criado_em"
    autocomplete_fields = ("pedido", "compra", "usuario", "cost_center")
    inlines = [TitleParcelInline]
    list_select_related = ("pedido", "compra", "usuario", "cost_center")

    @admin.action(description="Quitar (receber) títulos AR em aberto")
    def receber_outstanding(self, request, queryset):
        count = 0
        for t in queryset.select_related("pedido"):
            if t.tipo != Title.Tipo.AR or not t.pedido:
                continue
            outstanding = (t.valor or 0) - (t.valor_pago or 0)
            if outstanding > 0:
                FinanceiroService.receber_venda(t.pedido, outstanding)
                t.valor_pago = (t.valor_pago or 0) + outstanding
                t.status = Title.Status.QUITADO
                t.save(update_fields=["valor_pago", "status"])
                count += 1
        self.message_user(request, f"{count} título(s) AR quitado(s).")

    @admin.action(description="Quitar (pagar) títulos AP em aberto")
    def pagar_outstanding(self, request, queryset):
        count = 0
        for t in queryset.select_related("compra"):
            if t.tipo != Title.Tipo.AP or not t.compra:
                continue
            outstanding = (t.valor or 0) - (t.valor_pago or 0)
            if outstanding > 0:
                FinanceiroService.registrar_pagamento_compra(t.compra, outstanding)
                t.valor_pago = (t.valor_pago or 0) + outstanding
                t.status = Title.Status.QUITADO
                t.save(update_fields=["valor_pago", "status"])
                count += 1
        self.message_user(request, f"{count} título(s) AP quitado(s).")

    @admin.action(description="Marcar como Atrasado quando vencido")
    def marcar_atrasados(self, request, queryset):
        today = timezone.now().date()
        count = queryset.filter(due_date__lt=today, status__in=[Title.Status.ABERTO]).update(status=Title.Status.ATRASADO)
        self.message_user(request, f"{count} título(s) marcado(s) como Atrasado.")

    actions = ["receber_outstanding", "pagar_outstanding", "marcar_atrasados"]
    @admin.action(description="Exportar títulos selecionados em CSV")
    def exportar_titulos_csv(self, request, queryset):
        from django.http import HttpResponse
        rows = ["id,tipo,status,pedido,compra,due_date,valor,valor_pago,cost_center"]
        for t in queryset.select_related("pedido", "compra", "cost_center"):
            rows.append(f"{t.id},{t.tipo},{t.status},{t.pedido.slug if t.pedido else ''},{t.compra.slug if t.compra else ''},{t.due_date.isoformat()},{t.valor:.2f},{(t.valor_pago or 0):.2f},{t.cost_center.codigo if t.cost_center else ''}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"titulos.csv\"'
        return resp
    actions = ["receber_outstanding", "pagar_outstanding", "marcar_atrasados", "exportar_titulos_csv"]


class TitleParcelAdmin(admin.ModelAdmin):
    """Admin para parcelas de títulos."""
    list_display = ("title", "valor", "valor_pago", "due_date", "status", "criado_em")
    list_filter = ("status", "due_date")
    search_fields = ("title__id",)


admin.site.register(Account, AccountAdmin)
admin.site.register(CostCenter, CostCenterAdmin)
admin.site.register(UserDefaultCostCenter, UserDefaultCostCenterAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(TitleParcel, TitleParcelAdmin)
