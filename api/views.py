"""
ViewSets para API REST - ProjetoRavenna.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from catalog.models import Categoria, Produto
from stock.models import Deposito, Saldo, Movimentacao
from sales.models import Venda, ItemVenda
from partners.models import Cliente, Fornecedor
from financial.models import ContaReceber, ContaPagar

from sales.services import VendaService
from financial.services import FinanceiroService

from .serializers import *


class TenantFilteredViewSet(viewsets.ModelViewSet):
    """
    ViewSet base com filtragem automática por tenant (empresa).
    """
    
    def get_queryset(self):
        """Filtra queryset pela empresa do usuário."""
        return super().get_queryset().for_tenant(self.request.user)
    
    def perform_create(self, serializer):
        """Adiciona empresa automaticamente ao criar."""
        serializer.save(empresa=self.request.user.empresa)


# ==================== CATALOG ====================

class CategoriaViewSet(TenantFilteredViewSet):
    """ViewSet para Categorias."""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'ordem', 'created_at']
    ordering = ['ordem', 'nome']


class ProdutoViewSet(TenantFilteredViewSet):
    """ViewSet para Produtos."""
    queryset = Produto.objects.select_related('categoria')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'tipo', 'destaque', 'is_active']
    search_fields = ['nome', 'sku', 'codigo_barras', 'descricao']
    ordering_fields = ['nome', 'preco_venda', 'created_at']
    ordering = ['nome']
    
    def get_serializer_class(self):
        """Retorna serializer baseado na action."""
        if self.action == 'list':
            return ProdutoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProdutoCreateUpdateSerializer
        return ProdutoDetailSerializer


# ==================== STOCK ====================

class DepositoViewSet(TenantFilteredViewSet):
    """ViewSet para Depósitos."""
    queryset = Deposito.objects.all()
    serializer_class = DepositoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'codigo']
    ordering = ['-is_padrao', 'nome']


class SaldoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Saldos (read-only)."""
    queryset = Saldo.objects.select_related('produto', 'deposito')
    serializer_class = SaldoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['produto', 'deposito']
    search_fields = ['produto__nome', 'produto__sku']
    
    def get_queryset(self):
        return super().get_queryset().for_tenant(self.request.user)
    
    @action(detail=False, methods=['get'])
    def consultar(self, request):
        """
        Consulta saldo de um produto em um depósito.
        
        Query params:
            - produto_id: UUID do produto
            - deposito_id: UUID do depósito
        """
        produto_id = request.query_params.get('produto_id')
        deposito_id = request.query_params.get('deposito_id')
        
        if not all([produto_id, deposito_id]):
            return Response(
                {'error': 'produto_id e deposito_id são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            saldo = Saldo.objects.get(
                empresa=request.user.empresa,
                produto_id=produto_id,
                deposito_id=deposito_id
            )
            serializer = self.get_serializer(saldo)
            return Response(serializer.data)
        except Saldo.DoesNotExist:
            return Response(
                {'error': 'Saldo não encontrado', 'quantidade': 0},
                status=status.HTTP_404_NOT_FOUND
            )


class MovimentacaoViewSet(TenantFilteredViewSet):
    """ViewSet para Movimentações."""
    queryset = Movimentacao.objects.select_related('produto', 'deposito')
    serializer_class = MovimentacaoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['produto', 'deposito', 'tipo']
    ordering = ['-created_at']


# ==================== SALES ====================

class VendaViewSet(TenantFilteredViewSet):
    """ViewSet para Vendas."""
    queryset = Venda.objects.select_related('cliente', 'vendedor').prefetch_related('itens__produto')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'cliente', 'vendedor', 'tipo_pagamento']
    search_fields = ['numero', 'cliente__nome', 'observacoes']
    ordering = ['-data_emissao']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VendaListSerializer
        elif self.action == 'create':
            return VendaCreateSerializer
        return VendaDetailSerializer
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        Finaliza uma venda e baixa estoque.
        
        Body:
            - deposito_id: UUID do depósito
        """
        deposito_id = request.data.get('deposito_id')
        
        if not deposito_id:
            return Response(
                {'error': 'deposito_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            venda = VendaService.finalizar_venda(
                venda_id=pk,
                deposito_id=deposito_id,
                usuario=request.user.username
            )
            serializer = self.get_serializer(venda)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela uma venda e devolve estoque.
        
        Body:
            - motivo: Motivo do cancelamento (opcional)
        """
        motivo = request.data.get('motivo')
        
        try:
            venda = VendaService.cancelar_venda(
                venda_id=pk,
                motivo=motivo,
                usuario=request.user.username
            )
            serializer = self.get_serializer(venda)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def validar_estoque(self, request, pk=None):
        """
        Valida se há estoque disponível para a venda.
        
        Query params:
            - deposito_id: UUID do depósito
        """
        deposito_id = request.query_params.get('deposito_id')
        
        if not deposito_id:
            return Response(
                {'error': 'deposito_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultado = VendaService.validar_estoque_disponivel(pk, deposito_id)
        return Response(resultado)


class ItemVendaViewSet(TenantFilteredViewSet):
    """ViewSet para Itens de Venda."""
    queryset = ItemVenda.objects.select_related('produto', 'venda')
    serializer_class = ItemVendaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venda', 'produto']


# ==================== PARTNERS ====================

class ClienteViewSet(TenantFilteredViewSet):
    """ViewSet para Clientes."""
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_pessoa', 'is_active']
    search_fields = ['nome', 'nome_fantasia', 'cpf_cnpj', 'email']
    ordering = ['nome']


class FornecedorViewSet(TenantFilteredViewSet):
    """ViewSet para Fornecedores."""
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_pessoa', 'is_active']
    search_fields = ['razao_social', 'nome_fantasia', 'cpf_cnpj', 'email']
    ordering = ['razao_social']


# ==================== FINANCIAL ====================

class ContaReceberViewSet(TenantFilteredViewSet):
    """ViewSet para Contas a Receber."""
    queryset = ContaReceber.objects.select_related('cliente', 'venda')
    serializer_class = ContaReceberSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'cliente', 'venda']
    ordering = ['data_vencimento']
    
    @action(detail=True, methods=['post'])
    def baixar(self, request, pk=None):
        """
        Baixa (marca como paga) uma conta a receber.
        
        Body:
            - data_pagamento: Data do pagamento (opcional, default: hoje)
            - tipo_pagamento: Forma de pagamento
            - valor_juros: Juros (opcional, calculado automaticamente)
            - valor_multa: Multa (opcional, calculado automaticamente)
            - valor_desconto: Desconto (opcional)
        """
        try:
            conta = FinanceiroService.baixar_conta_receber(
                conta_id=pk,
                **request.data
            )
            serializer = self.get_serializer(conta)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContaPagarViewSet(TenantFilteredViewSet):
    """ViewSet para Contas a Pagar."""
    queryset = ContaPagar.objects.select_related('fornecedor')
    serializer_class = ContaPagarSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'fornecedor', 'categoria']
    ordering = ['data_vencimento']
    
    @action(detail=True, methods=['post'])
    def baixar(self, request, pk=None):
        """Baixa uma conta a pagar."""
        try:
            conta = FinanceiroService.baixar_conta_pagar(
                conta_id=pk,
                **request.data
            )
            serializer = self.get_serializer(conta)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
