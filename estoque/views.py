"""Views de Estoque (DRF ViewSets e ações customizadas).

Exponem histórico, saldo, entrada, ajuste, transferência,
além de CRUD de recebimentos com exportação CSV e estorno.
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from vendas.models import Produto
from .models import StockMovement
from .serializers import StockMovementSerializer, StockReceiptSerializer
from .services import EstoqueService
from auditoria.utils import log_action, ensure_idempotency
from django.utils import timezone
from .models import Deposito, MotivoAjuste


from .permissions import IsOperacaoOrAdmin


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta de movimentos de estoque e ações operacionais."""
    queryset = StockMovement.objects.select_related('produto', 'pedido', 'responsavel')
    serializer_class = StockMovementSerializer
    permission_classes = [IsOperacaoOrAdmin]
    throttle_scope = 'estoque'

    @action(detail=False, methods=['post'])
    def entrada(self, request):
        """Registra entrada com idempotência e log."""
        produto_slug = request.data.get('produto')
        quantidade = int(request.data.get('quantidade', 0))
        observacao = request.data.get('observacao', '')
        deposito_slug = request.data.get('deposito')
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        key = request.headers.get('Idempotency-Key')
        payload = {'produto': produto_slug, 'quantidade': quantidade, 'observacao': observacao, 'deposito': deposito_slug, 'tipo': 'entrada'}
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'estoque/entrada', payload)
        if idem and not created:
            produto = Produto.objects.get(slug=produto_slug)
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing = StockMovement.objects.filter(produto=produto, tipo=StockMovement.Tipo.IN, quantidade=quantidade, origem_slug='api', deposito=deposito, criado_em__gte=since).order_by('-criado_em').first()
            if existing:
                return Response(StockMovementSerializer(existing).data)
        produto = Produto.objects.get(slug=produto_slug)
        mv = EstoqueService.registrar_entrada(
            produto=produto,
            quantidade=quantidade,
            origem_slug='api',
            responsavel=request.user if request.user.is_authenticated else None,
            observacao=observacao,
            deposito=deposito,
        )
        log_action(request.user if request.user.is_authenticated else None, 'entrada', 'StockMovement', mv.id, {'produto': produto.slug, 'quantidade': quantidade, 'observacao': observacao})
        return Response(StockMovementSerializer(mv).data, status=201)

    @action(detail=False, methods=['post'])
    def ajuste(self, request):
        """Registra ajuste (positivo/negativo) com idempotência e log."""
        produto_slug = request.data.get('produto')
        quantidade = int(request.data.get('quantidade', 0))
        observacao = request.data.get('observacao', '')
        deposito_slug = request.data.get('deposito')
        motivo_codigo = request.data.get('motivo')
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        motivo = MotivoAjuste.objects.filter(codigo=motivo_codigo).first() if motivo_codigo else None
        key = request.headers.get('Idempotency-Key')
        payload = {'produto': produto_slug, 'quantidade': quantidade, 'observacao': observacao, 'deposito': deposito_slug, 'motivo': motivo_codigo, 'tipo': 'ajuste'}
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'estoque/ajuste', payload)
        if idem and not created:
            produto = Produto.objects.get(slug=produto_slug)
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing = StockMovement.objects.filter(produto=produto, tipo=StockMovement.Tipo.ADJUST, quantidade=quantidade, origem_slug='api', deposito=deposito, criado_em__gte=since).order_by('-criado_em').first()
            if existing:
                return Response(StockMovementSerializer(existing).data)
        produto = Produto.objects.get(slug=produto_slug)
        mv = EstoqueService.registrar_ajuste(
            produto=produto,
            quantidade=quantidade,
            origem_slug='api',
            responsavel=request.user if request.user.is_authenticated else None,
            observacao=observacao,
            deposito=deposito,
            motivo=motivo,
        )
        log_action(request.user if request.user.is_authenticated else None, 'ajuste', 'StockMovement', mv.id, {'produto': produto.slug, 'quantidade': quantidade, 'observacao': observacao})
        return Response(StockMovementSerializer(mv).data, status=201)

    @action(detail=False, methods=['get'])
    def saldo(self, request):
        """Retorna saldo do produto (opcional por depósito)."""
        produto_slug = request.query_params.get('produto')
        deposito_slug = request.query_params.get('deposito')
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        produto = Produto.objects.get(slug=produto_slug)
        saldo = EstoqueService.saldo_produto(produto, deposito=deposito)
        return Response({'produto': produto.slug, 'deposito': deposito.slug if deposito else None, 'saldo': saldo})

    @action(detail=False, methods=['get'])
    def historico(self, request):
        """Lista históricos filtrados por período, depósito e cost center."""
        produto_slug = request.query_params.get('produto')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        deposito_slug = request.query_params.get('deposito')
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        produto = Produto.objects.get(slug=produto_slug)
        qs = StockMovement.objects.filter(produto=produto).order_by('-criado_em')
        if deposito:
            qs = qs.filter(deposito=deposito)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        data = [{
            'tipo': mv.tipo,
            'quantidade': mv.quantidade,
            'origem_slug': mv.origem_slug,
            'pedido': mv.pedido.slug if mv.pedido else None,
            'cost_center': mv.pedido.cost_center.codigo if (mv.pedido and mv.pedido.cost_center) else None,
            'deposito': mv.deposito.slug if mv.deposito else None,
            'motivo': mv.motivo_ajuste.codigo if mv.motivo_ajuste else None,
            'criado_em': mv.criado_em.isoformat(),
        } for mv in qs]
        return Response(data)

    @action(detail=False, methods=['get'])
    def historico_csv(self, request):
        """Exporta histórico filtrado em CSV."""
        produto_slug = request.query_params.get('produto')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        deposito_slug = request.query_params.get('deposito')
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        produto = Produto.objects.get(slug=produto_slug)
        qs = StockMovement.objects.filter(produto=produto).order_by('-criado_em')
        if deposito:
            qs = qs.filter(deposito=deposito)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        rows = ["tipo,quantidade,origem_slug,pedido,cost_center,deposito,motivo,criado_em"]
        for mv in qs:
            rows.append(f"{mv.tipo},{mv.quantidade},{mv.origem_slug or ''},{mv.pedido.slug if mv.pedido else ''},{mv.pedido.cost_center.codigo if (mv.pedido and mv.pedido.cost_center) else ''},{mv.deposito.slug if mv.deposito else ''},{mv.motivo_ajuste.codigo if mv.motivo_ajuste else ''},{mv.criado_em.isoformat()}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = f'attachment; filename=\"historico_{produto.slug}.csv\"'
        return resp

    @action(detail=False, methods=['post'])
    def transferir(self, request):
        """Transfere saldo entre depósitos com validações e transação."""
        produto_slug = request.data.get('produto')
        quantidade = int(request.data.get('quantidade', 0))
        origem_slug = request.data.get('origem')
        destino_slug = request.data.get('destino')
        observacao = request.data.get('observacao', '')
        key = request.headers.get('Idempotency-Key')
        payload = {'produto': produto_slug, 'quantidade': quantidade, 'origem': origem_slug, 'destino': destino_slug, 'observacao': observacao, 'tipo': 'transfer'}
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'estoque/transfer', payload)
        origem = Deposito.objects.filter(slug=origem_slug).first() if origem_slug else None
        destino = Deposito.objects.filter(slug=destino_slug).first() if destino_slug else None
        produto = Produto.objects.get(slug=produto_slug)
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing_out = StockMovement.objects.filter(produto=produto, tipo='saida', quantidade=quantidade, origem_slug__startswith='transfer:', deposito=origem, criado_em__gte=since).order_by('-criado_em').first()
            if existing_out:
                return Response(StockMovementSerializer(existing_out).data)
        if quantidade <= 0 or not origem or not destino or origem == destino:
            return Response({'detail': 'Dados inválidos para transferência'}, status=400)
        # valida saldo no depósito de origem
        if EstoqueService.saldo_produto(produto, deposito=origem) < quantidade:
            return Response({'detail': 'Saldo insuficiente no depósito de origem'}, status=400)
        from django.db import transaction
        with transaction.atomic():
            StockMovement.objects.create(
                produto=produto,
                tipo=StockMovement.Tipo.OUT,
                quantidade=quantidade,
                origem_slug=f"transfer:{origem.slug}->{destino.slug}",
                responsavel=request.user if request.user.is_authenticated else None,
                observacao=observacao,
                deposito=origem,
            )
            mv_in = EstoqueService.registrar_entrada(
                produto=produto,
                quantidade=quantidade,
                origem_slug=f"transfer:{origem.slug}->{destino.slug}",
                responsavel=request.user if request.user.is_authenticated else None,
                observacao=observacao,
                deposito=destino,
            )
        log_action(request.user if request.user.is_authenticated else None, 'transfer', 'StockMovement', mv_in.id, {'produto': produto.slug, 'quantidade': quantidade, 'origem': origem.slug, 'destino': destino.slug})
        return Response(StockMovementSerializer(mv_in).data, status=201)


class StockReceiptViewSet(viewsets.ModelViewSet):
    """CRUD de recebimentos, CSV e estorno com movimentação reversa."""
    queryset = StockMovement.objects.none()
    serializer_class = StockReceiptSerializer
    permission_classes = [IsOperacaoOrAdmin]
    throttle_scope = 'estoque'

    def get_queryset(self):
        """Lista recebimentos com relacionamentos carregados."""
        from .models import StockReceipt
        return StockReceipt.objects.select_related('responsavel', 'deposito', 'fornecedor_ref').prefetch_related('itens__produto').order_by('-criado_em')

    def create(self, request, *args, **kwargs):
        """Cria recebimento com idempotência e log."""
        key = request.headers.get('Idempotency-Key')
        payload = request.data
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'estoque/recebimentos', payload)
        if idem and not created:
            from .models import StockReceipt
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing = StockReceipt.objects.filter(responsavel=request.user if request.user.is_authenticated else None, criado_em__gte=since).order_by('-criado_em').first()
            if existing:
                ser = self.get_serializer(existing)
                return Response(ser.data)
        resp = super().create(request, *args, **kwargs)
        try:
            rid = resp.data.get('id')
        except Exception:
            rid = None
        log_action(request.user if request.user.is_authenticated else None, 'recebimento', 'StockReceipt', rid, payload)
        return resp

    @action(detail=False, methods=['get'])
    def csv(self, request):
        """Exporta recebimentos filtrados em CSV."""
        from .models import StockReceipt
        fornecedor = request.query_params.get('fornecedor')
        deposito_slug = request.query_params.get('deposito')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = StockReceipt.objects.all().order_by('-criado_em')
        if fornecedor:
            qs = qs.filter(fornecedor_ref__slug=fornecedor)
        if deposito_slug:
            qs = qs.filter(deposito__slug=deposito_slug)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        rows = ["id,fornecedor,documento,deposito,itens_count,criado_em"]
        for r in qs:
            rows.append(f"{r.id},{(r.fornecedor_ref.slug if r.fornecedor_ref else r.fornecedor)},{r.documento},{(r.deposito.slug if r.deposito else '')},{r.itens.count()},{r.criado_em.isoformat()}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="recebimentos.csv"'
        return resp

    @action(detail=True, methods=['post'])
    def estornar(self, request, pk=None):
        """Estorna recebimento gerando saídas e marcando estornado_em."""
        from .models import StockReceipt
        from django.utils import timezone as djtz
        recibo = StockReceipt.objects.select_related('deposito').prefetch_related('itens__produto').get(pk=pk)
        if recibo.estornado_em:
            ser = self.get_serializer(recibo)
            return Response(ser.data)
        from django.db import transaction
        with transaction.atomic():
            for item in recibo.itens.all():
                StockMovement.objects.create(
                    produto=item.produto,
                    tipo=StockMovement.Tipo.OUT,
                    quantidade=int(item.quantidade),
                    origem_slug=f"estorno:{recibo.id}",
                    responsavel=request.user if request.user.is_authenticated else None,
                    observacao='estorno de recebimento',
                    deposito=recibo.deposito,
                )
            recibo.estornado_em = djtz.now()
            recibo.save(update_fields=['estornado_em'])
        ser = self.get_serializer(recibo)
        return Response(ser.data)
