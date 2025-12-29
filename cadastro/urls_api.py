from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, SupplierViewSet, CustomerViewSet

router = DefaultRouter()
router.register('enderecos', AddressViewSet, basename='endereco')
router.register('fornecedores', SupplierViewSet, basename='fornecedor')
router.register('clientes', CustomerViewSet, basename='cliente')

urlpatterns = [
    path('', include(router.urls)),
]
