"""
App de Importação de NFe para Projeto Nix.
"""
from django.apps import AppConfig


class NfeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nfe'
    verbose_name = 'Importação de NFe'
