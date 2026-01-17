"""
ViewSets para API REST - Projeto Nix.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from catalog.models import Categoria, Produto, FichaTecnicaItem
from stock.models import Deposito, Saldo, Movimentacao, Lote
from sales.models import Venda, ItemVenda
from partners.models import Cliente, Fornecedor
from financial.models import ContaReceber, ContaPagar

from sales.services import VendaService
from financial.services import FinanceiroService
from catalog.services import CatalogService
from stock.services import StockService

from .serializers import *
from .filters import (
    VendaFilter, ProdutoFilter, MovimentacaoFilter,
    ClienteFilter, FornecedorFilter, ContaReceberFilter, ContaPagarFilter
)
from .throttling import VendaRateThrottle, RelatorioRateThrottle


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
    """
    ViewSet para Produtos do catálogo.
    
    ## Filtros disponíveis:
    - preco_min / preco_max - Filtrar por faixa de preço
    - categoria_nome - Buscar por nome da categoria
    - search - Busca em nome, SKU ou código de barras
    - tipo - Filtrar por tipo (FINAL, INSUMO, COMPOSTO)
    - destaque - Apenas produtos em destaque
    - is_active - Apenas ativos/inativos
    
    ## Exemplos:
    ```
    GET /api/produtos/?preco_min=10&preco_max=100
    GET /api/produtos/?categoria_nome=Bebidas&destaque=true
    GET /api/produtos/?search=coca
    GET /api/produtos/?tipo=COMPOSTO  # Produtos com ficha técnica
    ```
    """
    queryset = Produto.objects.select_related('categoria')
    filterset_class = ProdutoFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
    
    @action(detail=True, methods=['post'])
    def recalcular_custo(self, request, pk=None):
        """
        Recalcula o custo de um produto composto baseado na ficha técnica.
        
        Apenas para produtos do tipo COMPOSTO.
        """
        produto = self.get_object()
        
        try:
            custo_calculado = CatalogService.recalcular_custo_produto(produto)
            return Response({
                'success': True,
                'custo_anterior': float(request.data.get('custo_anterior', 0)),
                'custo_atual': float(custo_calculado),
                'message': f'Custo recalculado: R$ {custo_calculado}'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FichaTecnicaItemViewSet(TenantFilteredViewSet):
    """
    ViewSet para Itens da Ficha Técnica.
    
    Permite gerenciar a composição de produtos compostos (Bill of Materials).
    """
    queryset = FichaTecnicaItem.objects.select_related('produto_pai', 'componente')
    serializer_class = FichaTecnicaItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['produto_pai', 'componente']
    
    def perform_create(self, serializer):
        """Ao criar item, recalcula custo do produto pai."""
        super().perform_create(serializer)
        item = serializer.instance
        CatalogService.recalcular_custo_produto(item.produto_pai)
    
    def perform_update(self, serializer):
        """Ao atualizar item, recalcula custo do produto pai."""
        super().perform_update(serializer)
        item = serializer.instance
        CatalogService.recalcular_custo_produto(item.produto_pai)
    
    def perform_destroy(self, instance):
        """Ao deletar item, recalcula custo do produto pai."""
        produto_pai = instance.produto_pai
        super().perform_destroy(instance)
        CatalogService.recalcular_custo_produto(produto_pai)


# ==================== STOCK ====================

class DepositoViewSet(TenantFilteredViewSet):
    """ViewSet para Depósitos."""
    queryset = Deposito.objects.all()
    serializer_class = DepositoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'codigo']
    ordering = ['-is_padrao', 'nome']


class LoteViewSet(TenantFilteredViewSet):
    """
    ViewSet para Lotes (controle de validade e rastreabilidade).
    
    ## Filtros:
    - produto - UUID do produto
    - deposito - UUID do depósito
    - status_validade - OK, ATENCAO, CRITICO, VENCIDO
    - search - Busca em código do lote ou nome do produto
    
    ## Actions customizadas:
    - GET /api/lotes/vencendo/ - Lotes próximos ao vencimento
    - POST /api/lotes/dar_entrada/ - Entrada de mercadoria com lote
    - GET /api/lotes/{id}/movimentacoes/ - Rastreabilidade do lote
    """
    queryset = Lote.objects.select_related('produto', 'deposito')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['produto', 'deposito']
    search_fields = ['codigo_lote', 'produto__nome']
    ordering = ['data_validade']  # FIFO por padrão
    
    def get_serializer_class(self):
        """Retorna serializer baseado na action."""
        if self.action == 'list':
            return LoteListSerializer
        return LoteSerializer
    
    def get_queryset(self):
        """Filtra por status de validade se informado."""
        queryset = super().get_queryset()
        status_validade = self.request.query_params.get('status_validade')
        
        if status_validade:
            hoje = timezone.now().date()
            
            if status_validade == 'VENCIDO':
                queryset = queryset.filter(data_validade__lt=hoje)
            elif status_validade == 'CRITICO':
                limite = hoje + timedelta(days=7)
                queryset = queryset.filter(
                    data_validade__gte=hoje,
                    data_validade__lte=limite
                )
            elif status_validade == 'ATENCAO':
                limite_min= hoje + timedelta(days=8)
                limite_max = hoje + timedelta(days=30)
                queryset = queryset.filter(
                    data_validade__gte=limite_min,
                    data_validade__lte=limite_max
                )
            elif status_validade == 'OK':
                limite = hoje + timedelta(days=31)
                queryset = queryset.filter(data_validade__gt=limite)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def vencendo(self, request):
        """
        Lista lotes próximos ao vencimento.
        
        Query params:
            - dias (default: 30): Dias até o vencimento
            - deposito: UUID do depósito (opcional)
        """
        dias = int(request.query_params.get('dias', 30))
        deposito_id = request.query_params.get('deposito')
        
        hoje = timezone.now().date()
        data_limite = hoje + timedelta(days=dias)
        
        queryset = self.get_queryset().filter(
            data_validade__lte=data_limite,
            data_validade__gte=hoje,
            quantidade_atual__gt=0
        )
        
        if deposito_id:
            queryset = queryset.filter(deposito_id=deposito_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def movimentacoes(self, request, pk=None):
        """
        Lista todas as movimentações de um lote específico (rastreabilidade).
        """
        lote = self.get_object()
        movimentacoes = lote.movimentacoes.select_related('produto', 'deposito').order_by('-created_at')
        
        page = self.paginate_queryset(movimentacoes)
        if page is not None:
            serializer = MovimentacaoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MovimentacaoSerializer(movimentacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def dar_entrada(self, request):
        """
        Dá entrada de mercadoria criando/atualizando lote.
        
        Body:
            - produto_id: UUID do produto
            - deposito_id: UUID do depósito
            - quantidade: Quantidade a dar entrada
            - codigo_lote: Código do lote
            - data_validade: Data de validade (YYYY-MM-DD)
            - data_fabricacao: Data de fabricação (opcional)
            - valor_unitario: Valor unitário (opcional)
            - documento: Número da NF (opcional)
            - observacao: Observações (opcional)
        """
        from catalog.models import Produto
        
        try:
            produto = Produto.objects.get(
                id=request.data['produto_id'],
                empresa=request.user.empresa
            )
            deposito = Deposito.objects.get(
                id=request.data['deposito_id'],
                empresa=request.user.empresa
            )
            
            lote, movimentacao = StockService.dar_entrada_com_lote(
                produto=produto,
                deposito=deposito,
                quantidade=request.data['quantidade'],
                codigo_lote=request.data['codigo_lote'],
                data_validade=request.data['data_validade'],
                data_fabricacao=request.data.get('data_fabricacao'),
                valor_unitario=request.data.get('valor_unitario'),
                documento=request.data.get('documento', ''),
                observacao=request.data.get('observacao', '')
            )
            
            serializer = self.get_serializer(lote)
            return Response({
                'lote': serializer.data,
                'movimentacao_id': str(movimentacao.id),
                'message': f'Entrada realizada: {lote.quantidade_atual} unidades'
            }, status=status.HTTP_201_CREATED)
        
        except KeyError as e:
            return Response(
                {'error': f'Campo obrigatório ausente: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    """
    ViewSet para Movimentações de Estoque.
    
    ## Filtros:
    - tipo - ENTRADA, SAIDA, BALANCO, TRANSFERENCIA
    - data_inicio / data_fim - Filtrar por período
    - produto_nome - Buscar por nome do produto
    - documento - Buscar por número do documento
    - lote - UUID do lote (para rastreabilidade)
    """
    queryset = Movimentacao.objects.select_related('produto', 'deposito', 'lote')
    serializer_class = MovimentacaoSerializer
    filterset_class = MovimentacaoFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ['-created_at']


# ==================== SALES ====================

class VendaViewSet(TenantFilteredViewSet):
    """
    ViewSet para Vendas.
    
    ## Rate Limiting: 100 requests/minuto
    
    ## Filtros:
    - status - ORCAMENTO, PENDENTE, FINALIZADA, CANCELADA
    - tipo_pagamento - PIX, DINHEIRO, CARTAO_CREDITO, etc
    - data_inicio / data_fim - Período de vendas
    - valor_min / valor_max - Faixa de valor
    - cliente_nome - Buscar por nome do cliente
    - vendedor_username - Buscar por vendedor
    
    ## Exemplos:
    ```
    GET /api/vendas/?status=FINALIZADA&data_inicio=2026-01-01
    GET /api/vendas/?valor_min=100&valor_max=1000
    GET /api/vendas/?cliente_nome=João
    ```
    """
    queryset = Venda.objects.select_related('cliente', 'vendedor').prefetch_related('itens__produto')
    filterset_class = VendaFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero', 'cliente__nome', 'observacoes']
    ordering = ['-data_emissao']
    throttle_classes = [VendaRateThrottle]
    
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
            - usar_lotes: bool (opcional, default: True)
        """
        deposito_id = request.data.get('deposito_id')
        usar_lotes = request.data.get('usar_lotes', True)
        gerar_conta_receber = request.data.get('gerar_conta_receber', False)
        
        if not deposito_id:
            return Response(
                {'error': 'deposito_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            venda = VendaService.finalizar_venda(
                venda_id=pk,
                deposito_id=deposito_id,
                usuario=request.user.username,
                usar_lotes=usar_lotes,
                gerar_conta_receber=gerar_conta_receber
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
    
    @action(detail=True, methods=['post'])
    def adicionar_item(self, request, pk=None):
        try:
            venda = Venda.objects.get(id=pk)
        except Venda.DoesNotExist:
            return Response({'error': 'Venda inexistente.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['venda'] = str(venda.id)
        serializer = ItemVendaSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        item = serializer.save(empresa=request.user.empresa, venda=venda)
        out = ItemVendaSerializer(item)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ItemVendaViewSet(TenantFilteredViewSet):
    """
    ViewSet para Itens de Venda (KDS).
    
    Permite visualizar e atualizar o status de produção dos itens.
    """
    queryset = ItemVenda.objects.select_related('produto', 'venda')
    serializer_class = ItemVendaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['venda', 'produto', 'status_producao']
    ordering = ['created_at']
    
    def perform_create(self, serializer):
        venda_id = self.request.data.get('venda')
        if not venda_id:
            raise Exception('venda é obrigatória')
        venda = Venda.objects.get(id=venda_id)
        serializer.save(empresa=self.request.user.empresa, venda=venda)
    
    def create(self, request, *args, **kwargs):
        venda_id = request.data.get('venda')
        if not venda_id:
            return Response({'venda': ['Este campo é obrigatório.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Venda.objects.get(id=venda_id)
        except Venda.DoesNotExist:
            return Response({'venda': ['Venda inexistente.']}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def preparar(self, request, pk=None):
        """Marca o item como 'Em Preparo'."""
        item = self.get_object()
        from sales.models import StatusProducao
        item.status_producao = StatusProducao.EM_PREPARO
        item.save(update_fields=['status_producao', 'updated_at'])
        return Response({'status': 'EM_PREPARO'})

    @action(detail=True, methods=['post'])
    def pronto(self, request, pk=None):
        """Marca o item como 'Pronto'."""
        item = self.get_object()
        from sales.models import StatusProducao
        item.status_producao = StatusProducao.PRONTO
        item.save(update_fields=['status_producao', 'updated_at'])
        return Response({'status': 'PRONTO'})

    @action(detail=True, methods=['post'])
    def entregar(self, request, pk=None):
        """Marca o item como 'Entregue'."""
        item = self.get_object()
        from sales.models import StatusProducao
        item.status_producao = StatusProducao.ENTREGUE
        item.save(update_fields=['status_producao', 'updated_at'])
        return Response({'status': 'ENTREGUE'})


# ==================== PARTNERS ====================

class ClienteViewSet(TenantFilteredViewSet):
    """ViewSet para Clientes."""
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filterset_class = ClienteFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'nome_fantasia', 'cpf_cnpj', 'email']
    ordering = ['nome']


class FornecedorViewSet(TenantFilteredViewSet):
    """ViewSet para Fornecedores."""
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    filterset_class = FornecedorFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['razao_social', 'nome_fantasia', 'cpf_cnpj', 'email']
    ordering = ['razao_social']


# ==================== FINANCIAL ====================

class ContaReceberViewSet(TenantFilteredViewSet):
    """
    ViewSet para Contas a Receber.
    
    ## Filtros:
    - status - PENDENTE, PAGA, CANCELADA
    - vencimento_inicio / vencimento_fim - Período de vencimento
    - vencidas=true - Apenas contas vencidas
    """
    queryset = ContaReceber.objects.select_related('cliente', 'venda')
    serializer_class = ContaReceberSerializer
    filterset_class = ContaReceberFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
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
    """
    ViewSet para Contas a Pagar.
    
    ## Filtros:
    - status - PENDENTE, PAGA, CANCELADA
    - vencimento_inicio / vencimento_fim - Período de vencimento
    - vencidas=true - Apenas contas vencidas
    """
    queryset = ContaPagar.objects.select_related('fornecedor')
    serializer_class = ContaPagarSerializer
    filterset_class = ContaPagarFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
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
