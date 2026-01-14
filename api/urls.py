"""
URLs da API REST.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet, ProdutoViewSet,
    DepositoViewSet, SaldoViewSet, MovimentacaoViewSet,
    VendaViewSet, ItemVendaViewSet,
    ClienteViewSet, FornecedorViewSet,
    ContaReceberViewSet, ContaPagarViewSet
)
from restaurant.views import SetorImpressaoViewSet, MesaViewSet, ComandaViewSet
from .kds_dashboard_views import ProducaoViewSet, dashboard_resumo_dia

# Router para registrar ViewSets
router = DefaultRouter()

# Catalog
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'produtos', ProdutoViewSet, basename='produto')

# Stock
router.register(r'depositos', DepositoViewSet, basename='deposito')
router.register(r'saldos', SaldoViewSet, basename='saldo')
router.register(r'movimentacoes', MovimentacaoViewSet, basename='movimentacao')

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

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard Analytics
    path('dashboard/resumo-dia/', dashboard_resumo_dia, name='dashboard-resumo-dia'),
]
