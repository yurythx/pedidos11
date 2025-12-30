"""Rotas da API de Compras (ordens e operações)."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseOrderViewSet

router = DefaultRouter()
router.register('compras', PurchaseOrderViewSet, basename='compras')

urlpatterns = [
    path('', include(router.urls)),
]
