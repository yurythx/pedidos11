"""Views de Vendas (DRF ViewSets).

Endpoints de Vendas focados em pedidos.
Catálogo (produtos/categorias e metadados) foi movido para o app catalogo.
"""
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Pedido
from .serializers import PedidoSerializer
from .permissions import IsOwner
from auditoria.utils import ensure_idempotency, log_action
from django.utils import timezone


class PedidoViewSet(viewsets.ModelViewSet):
    """CRUD de pedidos com restrição por usuário e criação idempotente."""
    queryset = Pedido.objects.select_related('usuario').prefetch_related('itens__produto')
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    throttle_scope = 'user'

    def get_queryset(self):
        """Staff enxerga todos; demais somente seus pedidos."""
        user = self.request.user
        qs = super().get_queryset()
        if user.is_staff:
            return qs
        return qs.filter(usuario=user)

    def get_permissions(self):
        """Exige ser dono no retrieve; demais padrões."""
        if self.action in ['retrieve']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Cria pedido com idempotência e log de auditoria."""
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
