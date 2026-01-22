"""
URLs para NFe - Projeto Nix.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProdutoFornecedorViewSet, ImportacaoNFeViewSet, EmissaoNFeViewSet

router = DefaultRouter()
router.register(r'vinculos', ProdutoFornecedorViewSet, basename='vinculo-fornecedor')
router.register(r'importacao', ImportacaoNFeViewSet, basename='importacao-nfe')
router.register(r'emissao', EmissaoNFeViewSet, basename='emissao-nfe')

urlpatterns = [
    path('', include(router.urls)),
]
