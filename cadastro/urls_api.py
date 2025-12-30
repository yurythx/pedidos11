"""Rotas da API de Cadastro (endereços, fornecedores e clientes)."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, SupplierViewSet, CustomerViewSet
from catalogo.views import ProdutoViewSet, CategoriaViewSet

router = DefaultRouter()
router.register('enderecos', AddressViewSet, basename='endereco')
router.register('fornecedores', SupplierViewSet, basename='fornecedor')
router.register('clientes', CustomerViewSet, basename='cliente')
router.register('produtos', ProdutoViewSet, basename='produto-cadastro')
router.register('categorias', CategoriaViewSet, basename='categoria-cadastro')

urlpatterns = [
    path('', include(router.urls)),
]
