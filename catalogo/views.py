from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Produto, Categoria, ProdutoImagem, ProdutoAtributo, ProdutoAtributoValor, ProdutoVariacao
from .serializers import ProdutoSerializer, CategoriaSerializer, ProdutoImagemSerializer, ProdutoAtributoSerializer, ProdutoAtributoValorSerializer, ProdutoVariacaoSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from vendas.permissions import IsAdminOrReadOnly
from vendas.pagination import OptionalPagination
from .filters import ProdutoFilterSet


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.select_related('categoria').prefetch_related('imagens', 'atributos_valores__atributo', 'variacoes').all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['preco', 'nome', 'sku']
    ordering = ['nome']
    pagination_class = OptionalPagination
    filterset_class = ProdutoFilterSet


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    from rest_framework.decorators import action
    from rest_framework.response import Response

    @action(detail=True, methods=['get'])
    def produtos(self, request, slug=None):
        categoria = self.get_object()
        produtos = categoria.produtos.filter(disponivel=True).select_related('categoria').prefetch_related('imagens', 'atributos_valores__atributo', 'variacoes')
        return Response(ProdutoSerializer(produtos, many=True).data)


class ProdutoImagemViewSet(viewsets.ModelViewSet):
    queryset = ProdutoImagem.objects.select_related('produto').order_by('pos', 'id')
    serializer_class = ProdutoImagemSerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_scope = 'user'

    def get_queryset(self):
        produto = self.request.query_params.get('produto')
        qs = super().get_queryset()
        if produto:
            qs = qs.filter(produto__slug=produto)
        return qs


class ProdutoAtributoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoAtributo.objects.all().order_by('codigo')
    serializer_class = ProdutoAtributoSerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_scope = 'user'


class ProdutoAtributoValorViewSet(viewsets.ModelViewSet):
    queryset = ProdutoAtributoValor.objects.select_related('produto', 'atributo').order_by('-criado_em')
    serializer_class = ProdutoAtributoValorSerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_scope = 'user'

    def get_queryset(self):
        produto = self.request.query_params.get('produto')
        atributo = self.request.query_params.get('atributo')
        qs = super().get_queryset()
        if produto:
            qs = qs.filter(produto__slug=produto)
        if atributo:
            qs = qs.filter(atributo__codigo=atributo)
        return qs


class ProdutoVariacaoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoVariacao.objects.select_related('produto').order_by('produto__slug', 'sku')
    serializer_class = ProdutoVariacaoSerializer
    permission_classes = [IsAdminOrReadOnly]
    throttle_scope = 'user'

    def get_queryset(self):
        produto = self.request.query_params.get('produto')
        qs = super().get_queryset()
        if produto:
            qs = qs.filter(produto__slug=produto)
        return qs
