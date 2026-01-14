"""
ViewSets para API REST do módulo Restaurant.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from restaurant.models import SetorImpressao, Mesa, Comanda
from restaurant.services import RestaurantService, ComandaService
from api.serializers.restaurant import SetorImpressaoSerializer, MesaSerializer, ComandaSerializer


class TenantFilteredViewSet(viewsets.ModelViewSet):
    """ViewSet base com filtragem automática por tenant."""
    
    def get_queryset(self):
        """Filtra queryset pela empresa do usuário."""
        from core.managers import TenantManager
        qs = super().get_queryset()
        if hasattr(qs.model.objects, 'for_tenant'):
            return qs.model.objects.for_tenant(self.request.user)
        return qs.filter(empresa=self.request.user.empresa)
    
    def perform_create(self, serializer):
        """Adiciona empresa automaticamente."""
        serializer.save(empresa=self.request.user.empresa)


class SetorImpressaoViewSet(TenantFilteredViewSet):
    """
    ViewSet para gerenciar SetoresImpressao (Cozinha, Bar, etc).
    
    Endpoints:
    - GET /api/setores-impressao/ - Listar setores
    - POST /api/setores-impressao/ - Criar setor
    - GET/PUT/PATCH/DELETE /api/setores-impressao/{id}/
    """
    queryset = SetorImpressao.objects.all()
    serializer_class = SetorImpressaoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering = ['ordem', 'nome']


class MesaViewSet(TenantFilteredViewSet):
    """
    ViewSet para gerenciar Mesas do restaurante.
    
    Endpoints padrão + Actions customizadas:
    - POST /api/mesas/{id}/abrir/ - Abre mesa
    - POST /api/mesas/{id}/adicionar_pedido/ - Adiciona item
    - GET /api/mesas/{id}/conta/ - Resumo da conta
    - POST /api/mesas/{id}/fechar/ - Fecha conta e finaliza venda
    - POST /api/mesas/{id}/liberar/ - Libera mesa suja
    - POST /api/mesas/{id}/transferir/ - Transfere para outra mesa
    """
    queryset = Mesa.objects.select_related('venda_atual').all()
    serializer_class = MesaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['numero']
    
    @action(detail=True, methods=['post'])
    def abrir(self, request, pk=None):
        """
        Abre uma mesa para atendimento.
        
        Body: {} (vazio, usa o usuário logado como garçom)
        
        Returns:
            200: Mesa aberta com sucesso (retorna venda criada)
            400: Erro (mesa já ocupada, etc)
        """
        mesa = self.get_object()
        
        try:
            venda = RestaurantService.abrir_mesa(
                mesa_id=mesa.id,
                garcom_user=request.user
            )
            
            return Response({
                'success': True,
                'message': f'Mesa {mesa.numero} aberta',
                'mesa': MesaSerializer(mesa).data,
                'venda': {
                    'id': str(venda.id),
                    'numero': venda.numero,
                    'status': venda.status
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def adicionar_pedido(self, request, pk=None):
        """
        Adiciona item ao pedido da mesa.
        
        Body:
        {
            "produto_id": "uuid",
            "quantidade": 2,
            "complementos": [
                {"complemento_id": "uuid", "quantidade": 1},
                {"complemento_id": "uuid", "quantidade": 2}
            ],
            "observacao": "Sem cebola"
        }
        
        Returns:
            201: Item adicionado
            400: Erro de validação
        """
        mesa = self.get_object()
        
        produto_id = request.data.get('produto_id')
        quantidade = request.data.get('quantidade', 1)
        complementos = request.data.get('complementos', [])
        observacao = request.data.get('observacao', '')
        
        if not produto_id:
            return Response({
                'success': False,
                'error': 'produto_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item = RestaurantService.adicionar_item_mesa(
                mesa_id=mesa.id,
                produto_id=produto_id,
                quantidade=quantidade,
                complementos_list=complementos,
                observacao=observacao
            )
            
            return Response({
                'success': True,
                'message': 'Item adicionado',
                'item': {
                    'id': str(item.id),
                    'produto': item.produto.nome,
                    'quantidade': str(item.quantidade),
                    'preco_unitario': str(item.preco_unitario),
                    'subtotal': str(item.subtotal),
                    'complementos_count': item.complementos.count()
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def conta(self, request, pk=None):
        """
        Retorna resumo da conta da mesa.
        
        Returns:
            200: Resumo completo (total, itens, etc)
        """
        mesa = self.get_object()
        
        try:
            resumo = RestaurantService.obter_resumo_conta(mesa.id)
            return Response(resumo, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        """
        Fecha a conta e finaliza a venda (baixa estoque).
        
        Body:
        {
            "deposito_id": "uuid"
        }
        
        Returns:
            200: Conta fechada com sucesso
            400: Erro
        """
        mesa = self.get_object()
        deposito_id = request.data.get('deposito_id')
        
        if not deposito_id:
            return Response({
                'success': False,
                'error': 'deposito_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = RestaurantService.fechar_mesa(
                mesa_id=mesa.id,
                deposito_id=deposito_id
            )
            
            return Response({
                'success': True,
                'message': f'Mesa {mesa.numero} fechada',
                'venda': {
                    'id': str(venda.id),
                    'numero': venda.numero,
                    'total_liquido': str(venda.total_liquido),
                    'status': venda.status
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def liberar(self, request, pk=None):
        """
        Libera mesa suja (após limpeza).
        
        Returns:
            200: Mesa liberada
        """
        mesa = self.get_object()
        
        try:
            RestaurantService.liberar_mesa(mesa.id)
            
            return Response({
                'success': True,
                'message': f'Mesa {mesa.numero} liberada'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transferir(self, request, pk=None):
        """
        Transfere venda para outra mesa.
        
        Body:
        {
            "mesa_destino_id": "uuid"
        }
        
        Returns:
            200: Transferência realizada
        """
        mesa_origem = self.get_object()
        mesa_destino_id = request.data.get('mesa_destino_id')
        
        if not mesa_destino_id:
            return Response({
                'success': False,
                'error': 'mesa_destino_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            origem, destino = RestaurantService.transferir_mesa(
                mesa_origem_id=mesa_origem.id,
                mesa_destino_id=mesa_destino_id
            )
            
            return Response({
                'success': True,
                'message': f'Venda transferida da mesa {origem.numero} para {destino.numero}'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ComandaViewSet(TenantFilteredViewSet):
    """
    ViewSet para gerenciar Comandas.
    
    Actions customizadas:
    - POST /api/comandas/{id}/abrir/ - Abre comanda
    - POST /api/comandas/{id}/adicionar_pedido/ - Adiciona item
    - GET /api/comandas/{id}/conta/ - Resumo
    - POST /api/comandas/{id}/fechar/ - Fecha comanda
    - POST /api/comandas/{id}/bloquear/ - Bloqueia comanda
    """
    queryset = Comanda.objects.select_related('venda_atual').all()
    serializer_class = ComandaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['codigo']
    ordering = ['codigo']
    
    @action(detail=True, methods=['post'])
    def abrir(self, request, pk=None):
        """Abre comanda (mesmo padrão de mesa)."""
        comanda = self.get_object()
        
        try:
            venda = ComandaService.abrir_comanda(
                comanda_id=comanda.id,
                garcom_user=request.user
            )
            
            return Response({
                'success': True,
                'message': f'Comanda {comanda.codigo} aberta',
                'venda_numero': venda.numero
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def adicionar_pedido(self, request, pk=None):
        """Adiciona item à comanda."""
        comanda = self.get_object()
        
        produto_id = request.data.get('produto_id')
        quantidade = request.data.get('quantidade', 1)
        complementos = request.data.get('complementos', [])
        observacao = request.data.get('observacao', '')
        
        if not produto_id:
            return Response({
                'error': 'produto_id obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item = ComandaService.adicionar_item_comanda(
                comanda_id=comanda.id,
                produto_id=produto_id,
                quantidade=quantidade,
                complementos_list=complementos,
                observacao=observacao
            )
            
            return Response({
                'success': True,
                'item_id': str(item.id)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        """Fecha comanda."""
        comanda = self.get_object()
        deposito_id = request.data.get('deposito_id')
        
        if not deposito_id:
            return Response({
                'error': 'deposito_id obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = ComandaService.fechar_comanda(
                comanda_id=comanda.id,
                deposito_id=deposito_id
            )
            
            return Response({
                'success': True,
                'venda_numero': venda.numero,
                'total': str(venda.total_liquido)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def bloquear(self, request, pk=None):
        """Bloqueia comanda (ex: cartão perdido)."""
        comanda = self.get_object()
        motivo = request.data.get('motivo', 'Bloqueada manualmente')
        
        try:
            comanda.bloquear(motivo)
            
            return Response({
                'success': True,
                'message': f'Comanda {comanda.codigo} bloqueada'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
