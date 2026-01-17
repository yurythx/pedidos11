"""
URLs para NFe - Projeto Nix.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProdutoFornecedorViewSet, ImportacaoNFeViewSet

router = DefaultRouter()
router.register(r'vinculos', ProdutoFornecedorViewSet, basename='vinculo-fornecedor')
router.register(r'importacao', ImportacaoNFeViewSet, basename='importacao-nfe')

urlpatterns = [
    path('', include(router.urls)),
]
