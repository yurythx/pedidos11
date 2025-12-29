from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Produto, Categoria, Pedido, ProdutoImagem, ProdutoAtributo, ProdutoAtributoValor, ProdutoVariacao
from .serializers import (
    ProdutoSerializer,
    CategoriaSerializer,
    PedidoSerializer,
    ProdutoImagemSerializer,
    ProdutoAtributoSerializer,
    ProdutoAtributoValorSerializer,
    ProdutoVariacaoSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwner
from .services import ProdutoService
from .pagination import OptionalPagination
from auditoria.utils import ensure_idempotency, log_action
from django.utils import timezone


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['preco', 'nome', 'sku']
    ordering = ['nome']
    pagination_class = OptionalPagination
    from .filters import ProdutoFilterSet
    filterset_class = ProdutoFilterSet

    def get_queryset(self):
        categoria = self.request.query_params.get('categoria')
        texto = self.request.query_params.get('q')
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return ProdutoService.filtrar(categoria_slug=categoria, texto=texto)
        return Produto.objects.all()


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def produtos(self, request, slug=None):
        categoria = self.get_object()
        produtos = categoria.produtos.filter(disponivel=True)
        return Response(ProdutoSerializer(produtos, many=True).data)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related('usuario').prefetch_related('itens__produto')
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    throttle_scope = 'user'

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_staff:
            return qs
        return qs.filter(usuario=user)

    def get_permissions(self):
        if self.action in ['retrieve']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        key = request.headers.get('Idempotency-Key')
        payload = {
            'itens_payload': request.data.get('itens_payload'),
            'cost_center': request.data.get('cost_center'),
        }
        idem, created = ensure_idempotency(key, request.user, 'vendas/pedidos', payload)
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing = Pedido.objects.filter(usuario=request.user, data_criacao__gte=since).order_by('-data_criacao').first()
            if existing:
                ser = self.get_serializer(existing)
                return Response(ser.data)
        response = super().create(request, *args, **kwargs)
        try:
            slug = response.data.get('slug')
        except Exception:
            slug = None
        log_action(request.user, 'criar_pedido', 'Pedido', slug, payload)
        return response


class ProdutoImagemViewSet(viewsets.ModelViewSet):
    queryset = ProdutoImagem.objects.select_related('produto').order_by('pos', 'id')
    serializer_class = ProdutoImagemSerializer
    permission_classes = [permissions.IsAdminUser]
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
    permission_classes = [permissions.IsAdminUser]
    throttle_scope = 'user'


class ProdutoAtributoValorViewSet(viewsets.ModelViewSet):
    queryset = ProdutoAtributoValor.objects.select_related('produto', 'atributo').order_by('-criado_em')
    serializer_class = ProdutoAtributoValorSerializer
    permission_classes = [permissions.IsAdminUser]
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
    permission_classes = [permissions.IsAdminUser]
    throttle_scope = 'user'

    def get_queryset(self):
        produto = self.request.query_params.get('produto')
        qs = super().get_queryset()
        if produto:
            qs = qs.filter(produto__slug=produto)
        return qs
