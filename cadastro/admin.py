"""Admin de Cadastro: endereços, fornecedores e clientes."""
from django.contrib import admin
from .models import Address, Supplier, Customer


class AddressAdmin(admin.ModelAdmin):
    """Admin para Address."""
    list_display = ("logradouro", "numero", "cidade", "estado", "cep", "pais", "criado_em")
    search_fields = ("logradouro", "cidade", "estado", "cep", "pais")


class SupplierAdmin(admin.ModelAdmin):
    """Admin para Supplier com slug readonly."""
    list_display = ("nome", "slug", "email", "telefone", "documento", "criado_em")
    search_fields = ("nome", "slug", "email", "telefone", "documento")
    readonly_fields = ("slug",)
    filter_horizontal = ("enderecos",)


class CustomerAdmin(admin.ModelAdmin):
    """Admin para Customer com autocomplete de usuário."""
    list_display = ("nome", "slug", "email", "telefone", "documento", "user", "criado_em")
    search_fields = ("nome", "slug", "email", "telefone", "documento", "user__username")
    readonly_fields = ("slug",)
    autocomplete_fields = ("user",)
    filter_horizontal = ("enderecos",)


admin.site.register(Address, AddressAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Customer, CustomerAdmin)
