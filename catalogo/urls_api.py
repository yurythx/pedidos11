from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, CategoriaViewSet, ProdutoImagemViewSet, ProdutoAtributoViewSet, ProdutoAtributoValorViewSet, ProdutoVariacaoViewSet

router = DefaultRouter()
router.register('produtos', ProdutoViewSet, basename='catalogo-produto')
router.register('categorias', CategoriaViewSet, basename='catalogo-categoria')
router.register('produtos-imagens', ProdutoImagemViewSet, basename='catalogo-produto-imagem')
router.register('produtos-atributos', ProdutoAtributoViewSet, basename='catalogo-produto-atributo')
router.register('produtos-atributos-valores', ProdutoAtributoValorViewSet, basename='catalogo-produto-atributo-valor')
router.register('produtos-variacoes', ProdutoVariacaoViewSet, basename='catalogo-produto-variacao')

urlpatterns = [
    path('', include(router.urls)),
]
