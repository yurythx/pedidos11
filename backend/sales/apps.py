"""
Configuração do app Sales.
"""
from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales'
    verbose_name = 'Vendas'
    
    def ready(self):
        """Importa signals quando o app estiver pronto."""
        import sales.signals  # noqa
