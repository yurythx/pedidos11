"""
URLs da API REST.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet, ProdutoViewSet, FichaTecnicaItemViewSet,
    DepositoViewSet, SaldoViewSet, MovimentacaoViewSet, LoteViewSet,
    VendaViewSet, ItemVendaViewSet,
    ClienteViewSet, FornecedorViewSet,
    ContaReceberViewSet, ContaPagarViewSet
)
from restaurant.views import SetorImpressaoViewSet, MesaViewSet, ComandaViewSet
from .kds_dashboard_views import ProducaoViewSet, dashboard_resumo_dia
from authentication.models import CustomUser
from authentication.serializers import UserSerializer
from locations.models import Endereco
from .serializers import EnderecoSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

# Router para registrar ViewSets
router = DefaultRouter()

# Catalog
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'fichas-tecnicas', FichaTecnicaItemViewSet, basename='ficha-tecnica')

# Stock
router.register(r'depositos', DepositoViewSet, basename='deposito')
router.register(r'saldos', SaldoViewSet, basename='saldo')
router.register(r'movimentacoes', MovimentacaoViewSet, basename='movimentacao')
router.register(r'lotes', LoteViewSet, basename='lote')

# Sales
router.register(r'vendas', VendaViewSet, basename='venda')
router.register(r'itens-venda', ItemVendaViewSet, basename='item-venda')

# Partners
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')

# Financial
router.register(r'contas-receber', ContaReceberViewSet, basename='conta-receber')
router.register(r'contas-pagar', ContaPagarViewSet, basename='conta-pagar')

# Restaurant (Food Service)
router.register(r'setores-impressao', SetorImpressaoViewSet, basename='setor-impressao')
router.register(r'mesas', MesaViewSet, basename='mesa')
router.register(r'comandas', ComandaViewSet, basename='comanda')

# KDS (Kitchen Display System)
router.register(r'producao', ProducaoViewSet, basename='producao')

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return qs.filter(empresa=user.empresa)
        return qs.filter(Q(id=user.id))

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class EnderecoViewSet(viewsets.ModelViewSet):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().for_tenant(self.request.user)

    def perform_create(self, serializer):
        serializer.save()

router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'enderecos', EnderecoViewSet, basename='endereco')

urlpatterns = [
    path('', include(router.urls)),
    
    # NFe Import
    path('nfe/', include('nfe.urls')),
    
    # Dashboard Analytics
    path('dashboard/resumo-dia/', dashboard_resumo_dia, name='dashboard-resumo-dia'),
]
