"""
Configuração do app Financial.
"""
from django.apps import AppConfig


class FinancialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financial'
    verbose_name = 'Financeiro'
    
    def ready(self):
        """Importa signals quando o app estiver pronto."""
        import financial.signals  # noqa
