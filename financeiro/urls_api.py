"""Rotas da API Financeira (razão, contas, centros, títulos)."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LedgerEntryViewSet, AccountViewSet, CostCenterViewSet, UserDefaultCostCenterViewSet, TitleViewSet

router = DefaultRouter()
router.register('lancamentos', LedgerEntryViewSet, basename='financeiro-lancamento')
router.register('contas', AccountViewSet, basename='financeiro-conta')
router.register('centros', CostCenterViewSet, basename='financeiro-centro')
router.register('defaults', UserDefaultCostCenterViewSet, basename='financeiro-default')
router.register('titulos', TitleViewSet, basename='financeiro-titulo')

urlpatterns = [
    path('', include(router.urls)),
]
