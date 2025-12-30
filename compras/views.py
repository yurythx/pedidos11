"""Views de Compras (DRF ViewSet).

CRUD de ordens de compra com ações de receber, pagar, cancelar,
exportação CSV e cálculo de saldo por fornecedor. Idempotência na criação.
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer, PurchaseReceiveSerializer
from financeiro.permissions import IsFinanceiroOrAdmin
from auditoria.utils import ensure_idempotency, log_action
from django.utils import timezone


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """CRUD de PurchaseOrder com ações financeiras e de estoque."""
    queryset = PurchaseOrder.objects.select_related('fornecedor', 'responsavel', 'deposito', 'cost_center').prefetch_related('itens__produto').order_by('-criado_em')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsFinanceiroOrAdmin]
    lookup_field = 'slug'
    throttle_scope = 'financeiro'

    def create(self, request, *args, **kwargs):
        """Cria ordem com idempotência e log de auditoria."""
        key = request.headers.get('Idempotency-Key')
        payload = request.data
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'compras/pedidos', payload)
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            existing = PurchaseOrder.objects.filter(responsavel=request.user if request.user.is_authenticated else None, criado_em__gte=since).order_by('-criado_em').first()
            if existing:
                ser = self.get_serializer(existing)
                return Response(ser.data)
        resp = super().create(request, *args, **kwargs)
        try:
            slug = resp.data.get('slug')
        except Exception:
            slug = None
        log_action(request.user if request.user.is_authenticated else None, 'criar_compra', 'PurchaseOrder', slug, payload)
        return resp

    @action(detail=True, methods=['post'])
    def receber(self, request, slug=None):
        """Recebe itens da ordem (gera recebimento/estoque)."""
        ser = PurchaseReceiveSerializer(data={'order_slug': slug}, context={'request': request})
        ser.is_valid(raise_exception=True)
        order = ser.save()
        from .serializers import PurchaseOrderSerializer
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def pagar(self, request, slug=None):
        """Paga valor da ordem (baixa de título AP)."""
        from .serializers import PurchasePaySerializer, PurchaseOrderSerializer
        ser = PurchasePaySerializer(data={'order_slug': slug, 'valor': request.data.get('valor')}, context={'request': request})
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(PurchaseOrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def csv(self, request):
        """Exporta ordens filtradas em CSV."""
        from django.http import HttpResponse
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        fornecedor = request.query_params.get('fornecedor')
        deposito = request.query_params.get('deposito')
        cost_center = request.query_params.get('cost_center')
        qs = PurchaseOrder.objects.all().order_by('-criado_em')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if fornecedor:
            qs = qs.filter(fornecedor__slug=fornecedor)
        if deposito:
            qs = qs.filter(deposito__slug=deposito)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        rows = ["slug,fornecedor,documento,status,total,valor_pago,deposito,cost_center,criado_em,recebido_em,pago_em"]
        for o in qs:
            rows.append(f"{o.slug},{o.fornecedor.slug},{o.documento},{o.status},{o.total},{o.valor_pago},{o.deposito.slug if o.deposito else ''},{o.cost_center.codigo if o.cost_center else ''},{o.criado_em.isoformat()},{o.recebido_em.isoformat() if o.recebido_em else ''},{o.pago_em.isoformat() if o.pago_em else ''}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="compras.csv"'
        return resp

    @action(detail=True, methods=['post'])
    def cancelar(self, request, slug=None):
        """Cancela ordem recebida: estorna estoque, ajusta custo e registra estorno financeiro."""
        from django.db import transaction
        from django.utils import timezone as djtz
        from .models import PurchaseOrder
        from estoque.models import StockMovement, StockReceipt
        from financeiro.services import FinanceiroService
        order = PurchaseOrder.objects.select_related('deposito').prefetch_related('itens__produto').get(slug=slug)
        if order.valor_pago and order.valor_pago > 0:
            return Response({'detail': 'Compra com pagamentos não pode ser cancelada'}, status=400)
        if order.status != PurchaseOrder.Status.RECEBIDO:
            return Response({'detail': 'Somente compras recebidas podem ser canceladas'}, status=400)
        with transaction.atomic():
            for item in order.itens.all():
                StockMovement.objects.create(
                    produto=item.produto,
                    tipo=StockMovement.Tipo.OUT,
                    quantidade=int(item.quantidade),
                    origem_slug=f"cancel:{order.slug}",
                    responsavel=request.user if request.user.is_authenticated else None,
                    deposito=order.deposito,
                )
            from decimal import Decimal
            # recalcula custo médio removendo o lote cancelado
            by_prod = {}
            for item in order.itens.all():
                key = item.produto_id
                acc = by_prod.get(key, {'produto': item.produto, 'qty': 0, 'value': Decimal('0')})
                acc['qty'] += int(item.quantidade)
                acc['value'] += Decimal(item.quantidade) * Decimal(item.custo_unitario or 0)
                by_prod[key] = acc
            for acc in by_prod.values():
                produto = acc['produto']
                cancel_qty = acc['qty']
                cancel_val = acc['value']
                new_qty = EstoqueService.saldo_produto(produto)
                old_qty = new_qty + cancel_qty
                old_cost = Decimal(produto.custo or 0)
                if new_qty > 0:
                    new_cost = (Decimal(old_qty) * old_cost - cancel_val) / Decimal(new_qty)
                else:
                    new_cost = Decimal('0')
                produto.custo = new_cost
                produto.save(update_fields=['custo'])
            rec = StockReceipt.objects.filter(compra=order).order_by('-criado_em').first()
            if rec and not rec.estornado_em:
                rec.estornado_em = djtz.now()
                rec.save(update_fields=['estornado_em'])
            FinanceiroService.registrar_estorno_compra(order)
            order.status = PurchaseOrder.Status.CANCELADO
            order.save(update_fields=['status'])
        ser = PurchaseOrderSerializer(order)
        return Response(ser.data)

    @action(detail=False, methods=['get'])
    def saldo(self, request):
        """Saldo aberto por fornecedor (total - pagos) no período/fornecedor filtrado."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        fornecedor = request.query_params.get('fornecedor')
        from .models import PurchaseOrder
        qs = PurchaseOrder.objects.all()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if fornecedor:
            qs = qs.filter(fornecedor__slug=fornecedor)
        from decimal import Decimal
        data = {}
        for o in qs:
            key = o.fornecedor.slug
            aberto = Decimal(o.total or 0) - Decimal(o.valor_pago or 0)
            data[key] = Decimal(data.get(key, 0)) + aberto
        result = [{'fornecedor': k, 'saldo': f"{v:.2f}"} for k, v in data.items()]
        return Response(result)
