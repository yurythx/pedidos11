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
from sales.models import ItemVenda, StatusProducao, StatusVenda
from rest_framework.permissions import IsAuthenticated


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

    def create(self, request, *args, **kwargs):
        """Cria mesa com tratamento de erro para duplicidade."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # Captura IntegrityError (duplicidade de numero+empresa)
            if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                return Response(
                    {'error': 'Já existe uma mesa com este número.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise e
    
    @action(detail=True, methods=['post'])
    def abrir(self, request, pk=None):
        """
        Abre uma mesa para atendimento.
        
        Body: {"atendente_id": "uuid"} (opcional)
        """
        mesa = self.get_object()
        atendente_id = request.data.get('atendente_id')
        
        atendente_user = None
        if atendente_id:
             from authentication.models import CustomUser
             try:
                 atendente_user = CustomUser.objects.get(id=atendente_id, empresa=request.user.empresa)
             except CustomUser.DoesNotExist:
                 return Response({'error': 'Atendente não encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = RestaurantService.abrir_mesa(
                mesa_id=mesa.id,
                garcom_user=request.user,
                atendente_user=atendente_user
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
    

    @action(detail=True, methods=['post'])
    def remover_pedido(self, request, pk=None):
        """
        Remove item do pedido da mesa (cancelamento).
        
        Body: {"item_id": "uuid"}
        """
        mesa = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response({'error': 'item_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            RestaurantService.remover_item_mesa(mesa.id, item_id)
            return Response({'success': True, 'message': 'Item cancelado com sucesso'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
    def remover_pedido(self, request, pk=None):
        """Remove item da comanda (cancelamento)."""
        comanda = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response({'error': 'item_id obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            ComandaService.remover_item_comanda(comanda.id, item_id)
            return Response({'success': True, 'message': 'Item cancelado'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        """
        Fecha a conta e finaliza a venda (baixa estoque).
        """
        from django.core.exceptions import ValidationError
        
        mesa = self.get_object()
        deposito_id = request.data.get('deposito_id')
        tipo_pagamento = request.data.get('tipo_pagamento')
        valor_pago = request.data.get('valor_pago')
        colaborador_id = request.data.get('colaborador_id')
        cpf_cliente = request.data.get('cpf_cliente')
        
        if not deposito_id:
            return Response({'error': 'deposito_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = RestaurantService.fechar_mesa(
                mesa_id=mesa.id,
                deposito_id=deposito_id,
                tipo_pagamento=tipo_pagamento,
                usuario=request.user,
                valor_pago=valor_pago,
                colaborador_id=colaborador_id,
                cpf_cliente=cpf_cliente
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

        except ValidationError as e:
            # Retorna erro de validação (ex: estoque) estruturado
            return Response(
                e.message_dict if hasattr(e, 'message_dict') else {'error': e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
        atendente_id = request.data.get('atendente_id')
        
        atendente_user = None
        if atendente_id:
             from authentication.models import CustomUser
             try:
                 atendente_user = CustomUser.objects.get(id=atendente_id, empresa=request.user.empresa)
             except CustomUser.DoesNotExist:
                 return Response({'error': 'Atendente não encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = ComandaService.abrir_comanda(
                comanda_id=comanda.id,
                garcom_user=request.user,
                atendente_user=atendente_user
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
        tipo_pagamento = request.data.get('tipo_pagamento')
        valor_pago = request.data.get('valor_pago')
        colaborador_id = request.data.get('colaborador_id')
        cpf_cliente = request.data.get('cpf_cliente')
        
        if not deposito_id:
            return Response({
                'error': 'deposito_id obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            venda = ComandaService.fechar_comanda(
                comanda_id=comanda.id,
                deposito_id=deposito_id,
                tipo_pagamento=tipo_pagamento,
                valor_pago=valor_pago,
                colaborador_id=colaborador_id,
                cpf_cliente=cpf_cliente
            )
            
            return Response({
                'success': True,
                'venda_numero': venda.numero,
                'total': str(venda.total_liquido),
                'venda_id': venda.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def liberar(self, request, pk=None):
        """Libera comanda (cancelamento/limpeza)."""
        comanda = self.get_object()
        try:
            from sales.models import StatusVenda
            if comanda.venda_atual:
                venda = comanda.venda_atual
                venda.status = StatusVenda.CANCELADA
                venda.observacoes = (venda.observacoes or "") + " | Liberada manualmente"
                venda.save()
            
            comanda.liberar()
            return Response({'success': True, 'message': 'Comanda liberada'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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


class KdsViewSet(viewsets.ViewSet):
    """
    API para o Kitchen Display System (KDS).
    Gerencia itens de produção (Cozinha/Bar).
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Lista itens pendentes de produção."""
        setor_id = request.query_params.get('setor_id')
        
        # Filtra itens não finalizados e que devem ser produzidos
        qs = ItemVenda.objects.filter(
            venda__status__in=[StatusVenda.ORCAMENTO, StatusVenda.PENDENTE],
            status_producao__in=[StatusProducao.PENDENTE, StatusProducao.EM_PREPARO],
            produto__imprimir_producao=True
        ).select_related(
            'venda', 'venda__mesa', 'venda__comanda', 'venda__cliente',
            'produto', 'produto__setor_impressao'
        ).prefetch_related('complementos', 'complementos__complemento').order_by('created_at')
        
        if setor_id:
            qs = qs.filter(produto__setor_impressao_id=setor_id)
            
        # Agrupamento manual
        grouped = {}
        for item in qs:
            venda_id = str(item.venda.id)
            
            if venda_id not in grouped:
                identificacao = f"Venda #{item.venda.numero}"
                # Tenta identificar origem
                try:
                    if hasattr(item.venda, 'mesa') and item.venda.mesa:
                        identificacao = f"Mesa {item.venda.mesa.numero}"
                    elif hasattr(item.venda, 'comanda') and item.venda.comanda:
                        identificacao = f"Comanda {item.venda.comanda.codigo}"
                    elif item.venda.cliente:
                        identificacao = f"{item.venda.cliente.nome}"
                except Exception:
                    pass
                
                grouped[venda_id] = {
                    'venda_id': venda_id,
                    'identificacao': identificacao,
                    'inicio': item.venda.created_at,
                    'itens': []
                }
            
            grouped[venda_id]['itens'].append({
                'id': str(item.id),
                'produto': item.produto.nome,
                'quantidade': float(item.quantidade),
                'status': item.status_producao,
                'observacoes': item.observacoes,
                'complementos': [
                    f"{float(c.quantidade)}x {c.complemento.nome}" 
                    for c in item.complementos.all()
                ]
            })
            
        return Response(list(grouped.values()))

    @action(detail=True, methods=['post'])
    def avancar(self, request, pk=None):
        """Avança status: PENDENTE -> EM_PREPARO -> PRONTO -> ENTREGUE"""
        try:
            item = ItemVenda.objects.get(id=pk)
            status_map = {
                StatusProducao.PENDENTE: StatusProducao.EM_PREPARO,
                StatusProducao.EM_PREPARO: StatusProducao.PRONTO,
                StatusProducao.PRONTO: StatusProducao.ENTREGUE
            }
            
            next_status = status_map.get(item.status_producao)
            if next_status:
                item.status_producao = next_status
                item.save()
                return Response({'status': next_status})
            
            return Response({'status': item.status_producao}) # Já está entregue
        except ItemVenda.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
