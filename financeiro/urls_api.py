from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LedgerEntryViewSet, AccountViewSet, CostCenterViewSet, UserDefaultCostCenterViewSet

router = DefaultRouter()
router.register('lancamentos', LedgerEntryViewSet, basename='financeiro-lancamento')
router.register('contas', AccountViewSet, basename='financeiro-conta')
router.register('centros', CostCenterViewSet, basename='financeiro-centro')
router.register('defaults', UserDefaultCostCenterViewSet, basename='financeiro-default')

urlpatterns = [
    path('', include(router.urls)),
]
