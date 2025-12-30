"""Rotas da API de Relatórios."""
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RelatorioViewSet

router = SimpleRouter()
router.register('relatorios', RelatorioViewSet, basename='relatorios')

urlpatterns = [
    path('', include(router.urls)),
]
