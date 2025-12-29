from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProdutoViewSet,
    CategoriaViewSet,
    PedidoViewSet,
    ProdutoImagemViewSet,
    ProdutoAtributoViewSet,
    ProdutoAtributoValorViewSet,
    ProdutoVariacaoViewSet,
)

router = DefaultRouter()
router.register('produtos', ProdutoViewSet, basename='produto')
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('pedidos', PedidoViewSet, basename='pedido')
router.register('produtos-imagens', ProdutoImagemViewSet, basename='produto-imagem')
router.register('produtos-atributos', ProdutoAtributoViewSet, basename='produto-atributo')
router.register('produtos-atributos-valores', ProdutoAtributoValorViewSet, basename='produto-atributo-valor')
router.register('produtos-variacoes', ProdutoVariacaoViewSet, basename='produto-variacao')

urlpatterns = [
    path('', include(router.urls)),
]
