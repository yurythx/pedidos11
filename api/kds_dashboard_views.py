"""
ViewSets para KDS (Kitchen Display System) e Dashboard.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from sales.models import ItemVenda, Venda, StatusVenda, StatusProducao


class ProducaoItemSerializer(serializers.Serializer):
    """Serializer para itens na produção (KDS)."""
    id = serializers.UUIDField(read_only=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    quantidade = serializers.DecimalField(max_digits=15, decimal_places=3, read_only=True)
    observacoes = serializers.CharField(read_only=True)
    status_producao = serializers.ChoiceField(choices=StatusProducao.choices)
    
    # Venda / Mesa / Comanda
    venda_numero = serializers.IntegerField(source='venda.numero', read_only=True)
    mesa_numero = serializers.SerializerMethodField()
    comanda_codigo = serializers.SerializerMethodField()
    
    # Setor
    setor_nome = serializers.CharField(source='produto.setor_impressao.nome', read_only=True, allow_null=True)
    
    # Complementos
    complementos_texto = serializers.SerializerMethodField()
    
    # Tempo
    hora_pedido = serializers.DateTimeField(source='created_at', read_only=True)
    tempo_espera_minutos = serializers.SerializerMethodField()
    
    def get_mesa_numero(self, obj):
        if hasattr(obj.venda, 'mesa') and obj.venda.mesa:
            return obj.venda.mesa.numero
        return None
    
    def get_comanda_codigo(self, obj):
        if hasattr(obj.venda, 'comanda') and obj.venda.comanda:
            return obj.venda.comanda.codigo
        return None
    
    def get_complementos_texto(self, obj):
        """Retorna complementos em formato texto."""
        comps = obj.complementos.all()
        if not comps:
            return []
        return [
            f"{c.complemento.nome} (x{c.quantidade})"
            for c in comps
        ]
    
    def get_tempo_espera_minutos(self, obj):
        delta = timezone.now() - obj.created_at
        return int(delta.total_seconds() / 60)


class ProducaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para KDS (Kitchen Display System).
    
    Endpoints:
    - GET /api/producao/ - Lista itens para produção
    - GET /api/producao/?setor=uuid - Filtra por setor
    - GET /api/producao/?status=PENDENTE - Filtra por status
    - PATCH /api/producao/{id}/ - Atualiza status do item
    
    Read-only para listagem, permite UPDATE apenas do status_producao.
    """
    serializer_class = ProducaoItemSerializer
    queryset = ItemVenda.objects.select_related(
        'produto', 'produto__setor_impressao', 'venda'
    ).prefetch_related('complementos__complemento').filter(
        venda__status__in=[StatusVenda.ORCAMENTO, StatusVenda.PENDENTE, StatusVenda.FINALIZADA]
    )
    
    def get_queryset(self):
        """Filtra por empresa e permite filtros customizados."""
        qs = super().get_queryset().filter(empresa=self.request.user.empresa)
        
        # Filtro por setor de impressão
        setor_id = self.request.query_params.get('setor')
        if setor_id:
            qs = qs.filter(produto__setor_impressao_id=setor_id)
        
        # Filtro por status de produção
        status_prod = self.request.query_params.get('status')
        if status_prod:
            qs = qs.filter(status_producao=status_prod)
        
        # Filtra apenas itens que devem ser impressos
        qs = qs.filter(produto__imprimir_producao=True)
        
        # Ordena por data (mais antigos primeiro = prioridade)
        return qs.order_by('created_at')
    
    def update(self, request, *args, **kwargs):
        """Permite atualizar apenas o status_producao."""
        instance = self.get_object()
        novo_status = request.data.get('status_producao')
        
        if novo_status not in [choice[0] for choice in StatusProducao.choices]:
            return Response({
                'error': f'Status inválido. Use: {[c[0] for c in StatusProducao.choices]}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.status_producao = novo_status
        instance.save(update_fields=['status_producao', 'updated_at'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Mesmo comportamento para PATCH."""
        return self.update(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumo_dia(request):
    """
    Endpoint de analytics para dashboard.
    
    GET /api/dashboard/resumo-dia/
    
    Retorna métricas do dia atual:
    - total_vendas: Valor total vendido
    - qtd_pedidos: Quantidade de vendas
    - ticket_medio: Média por venda
    - ranking_produtos: Top 5 produtos mais vendidos
    - vendas_por_hora: Distribuição ao longo do dia
    """
    empresa = request.user.empresa
    hoje = timezone.now().date()
    
    # Vendas finalizadas de hoje
    vendas_hoje = Venda.objects.filter(
        empresa=empresa,
        status=StatusVenda.FINALIZADA,
        data_finalizacao__date=hoje
    )
    
    # Métricas básicas
    metricas = vendas_hoje.aggregate(
        total_vendas=Sum('total_liquido'),
        qtd_pedidos=Count('id'),
        ticket_medio=Avg('total_liquido')
    )
    
    # Top 5 produtos
    ranking_produtos = ItemVenda.objects.filter(
        empresa=empresa,
        venda__status=StatusVenda.FINALIZADA,
        venda__data_finalizacao__date=hoje
    ).values(
        'produto__nome'
    ).annotate(
        quantidade_vendida=Sum('quantidade'),
        valor_total=Sum(F('quantidade') * F('preco_unitario'))
    ).order_by('-quantidade_vendida')[:5]
    
    # Vendas por hora (apenas horas com vendas)
    vendas_por_hora = []
    for hora in range(24):
        inicio = timezone.datetime.combine(
            hoje,
            timezone.datetime.min.time()
        ).replace(hour=hora, tzinfo=timezone.get_current_timezone())
        fim = inicio + timedelta(hours=1)
        
        total_hora = vendas_hoje.filter(
            data_finalizacao__gte=inicio,
            data_finalizacao__lt=fim
        ).aggregate(total=Sum('total_liquido'))['total']
        
        if total_hora and total_hora > 0:
            vendas_por_hora.append({
                'hora': hora,
                'total': str(total_hora)
            })
    
    return Response({
        'data': str(hoje),
        'total_vendas': str(metricas['total_vendas'] or 0),
        'qtd_pedidos': metricas['qtd_pedidos'] or 0,
        'ticket_medio': str(round(metricas['ticket_medio'] or 0, 2)),
        'ranking_produtos': [
            {
                'produto': item['produto__nome'],
                'quantidade': str(item['quantidade_vendida']),
                'valor_total': str(item['valor_total'])
            }
            for item in ranking_produtos
        ],
        'vendas_por_hora': vendas_por_hora
    })
