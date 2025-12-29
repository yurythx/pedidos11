from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockMovementViewSet, StockReceiptViewSet
from rest_framework.routers import DefaultRouter
from .models import Deposito, MotivoAjuste
from rest_framework import viewsets, permissions
from cadastro.serializers import AddressSerializer
from cadastro.models import Address
from rest_framework.serializers import ModelSerializer

class DepositoSerializer(ModelSerializer):
    endereco = AddressSerializer(required=False, allow_null=True)
    class Meta:
        model = Deposito
        fields = ['nome', 'slug', 'endereco', 'criado_em']
        read_only_fields = ['slug', 'criado_em']

class DepositoViewSet(viewsets.ModelViewSet):
    queryset = Deposito.objects.select_related('endereco').order_by('-criado_em')
    serializer_class = DepositoSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'

class MotivoAjusteSerializer(ModelSerializer):
    class Meta:
        model = MotivoAjuste
        fields = ['codigo', 'nome', 'criado_em']
        read_only_fields = ['criado_em']

class MotivoAjusteViewSet(viewsets.ModelViewSet):
    queryset = MotivoAjuste.objects.all().order_by('codigo')
    serializer_class = MotivoAjusteSerializer
    permission_classes = [permissions.IsAdminUser]

router = DefaultRouter()
router.register('movimentos', StockMovementViewSet, basename='estoque-movimento')
router.register('recebimentos', StockReceiptViewSet, basename='estoque-recebimento')
router.register('depositos', DepositoViewSet, basename='estoque-deposito')
router.register('motivos-ajuste', MotivoAjusteViewSet, basename='estoque-motivo')

urlpatterns = [
    path('', include(router.urls)),
]
