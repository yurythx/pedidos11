"""Rotas da API de Vendas (DRF Router).

Catálogo (produtos/categorias e metadados) está disponível em /api/v1/catalogo.
Endpoints de catálogo aqui foram descontinuados.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PedidoViewSet,
)

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('', include(router.urls)),
]
