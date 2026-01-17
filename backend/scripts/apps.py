"""
App de scripts e utilitários do Projeto Nix.
"""
from django.apps import AppConfig


class ScriptsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scripts'
    verbose_name = 'Scripts e Utilitários'
