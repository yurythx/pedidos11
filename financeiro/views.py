"""Views e endpoints financeiros (DRF ViewSets e ações).

Responsável por:
- listar e exportar lançamentos do razão (LedgerEntry);
- aging de contas a receber por lançamento e por due_date;
- livro-caixa por dia com saldo;
- títulos (AR/AP) com operações de receber/pagar e gerenciar parcelas;
- posição por cliente e CSV correlatos;
- filtros, ordenação, caching e ETag/Last-Modified em respostas.
"""
from datetime import datetime
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Sum
from .models import LedgerEntry, Account, CostCenter, UserDefaultCostCenter, Title
from .serializers import LedgerEntrySerializer, AccountSerializer, CostCenterSerializer, UserDefaultCostCenterSerializer, TitleSerializer, TitleParcelSerializer
from .permissions import IsSuperUser, IsFinanceiroOrAdmin
import hashlib
from django.utils.http import http_date
from auditoria.utils import log_action, ensure_idempotency
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class LedgerEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta de lançamentos do livro razão."""
    queryset = LedgerEntry.objects.select_related('pedido', 'usuario')
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsFinanceiroOrAdmin]
    throttle_scope = 'financeiro'

    @action(detail=False, methods=['get'])
    def resumo(self, request):
        """Resumo simples de valores e contagem com ETag/Last-Modified."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"fin_resumo:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset()
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        total = sum((le.valor for le in qs), 0)
        data = {'total_receita': f"{total:.2f}", 'count': qs.count()}
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def resumo_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        total = sum((le.valor for le in qs), 0)
        csv = "total_receita,count,cost_center\n" + f"{total:.2f},{qs.count()},{cost_center or ''}\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="financeiro_resumo.csv"'
        return resp

    @action(detail=False, methods=['get'])
    def contas_resumo(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        side = request.query_params.get('side', 'debit')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"fin_contas:{start}:{end}:{cost_center}:{side}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset()
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        field = 'debit_account' if side == 'debit' else 'credit_account'
        agg = qs.values(field).annotate(total=Sum('valor')).order_by('-total')
        data = [{'account': a[field], 'total': f"{a['total']:.2f}"} for a in agg if a[field]]
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def contas_resumo_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        side = request.query_params.get('side', 'debit')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        field = 'debit_account' if side == 'debit' else 'credit_account'
        agg = qs.values(field).annotate(total=Sum('valor')).order_by('-total')
        rows = ["account,total,cost_center,side"]
        for a in agg:
            if a[field]:
                rows.append(f"{a[field]},{a['total']:.2f},{cost_center or ''},{side}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_contas_resumo.csv\"'
        return resp

    @action(detail=False, methods=['get'])
    def centros_resumo(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"fin_centros:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset().select_related('cost_center')
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        qs = self.get_queryset().select_related('cost_center')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        agg = qs.values('cost_center__codigo', 'cost_center__nome').annotate(total=Sum('valor')).order_by('-total')
        data = [{'centro_codigo': a['cost_center__codigo'], 'centro_nome': a['cost_center__nome'], 'total': f"{a['total']:.2f}"} for a in agg if a['cost_center__codigo']]
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def balanco(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        total = qs.aggregate(total=Sum('valor'))['total'] or 0
        data = {'debito_total': f"{total:.2f}", 'credito_total': f"{total:.2f}", 'balanced': True, 'count': qs.count()}
        return Response(data)

    @action(detail=False, methods=['get'])
    def centros_resumo_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset().select_related('cost_center')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        agg = qs.values('cost_center__codigo', 'cost_center__nome').annotate(total=Sum('valor')).order_by('-total')
        rows = ["cost_center_codigo,cost_center_nome,total,cost_center_filter"]
        for a in agg:
            if a['cost_center__codigo']:
                rows.append(f"{a['cost_center__codigo']},{a['cost_center__nome']},{a['total']:.2f},{cost_center or ''}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_centros_resumo.csv\"'
        return resp

    @action(detail=False, methods=['post'])
    def receber_venda(self, request):
        from vendas.models import Pedido
        from decimal import Decimal
        slug = request.data.get('pedido')
        valor = request.data.get('valor')
        try:
            valor_dec = Decimal(str(valor))
        except Exception:
            return Response({'detail': 'Valor inválido'}, status=400)
        try:
            pedido = Pedido.objects.get(slug=slug)
        except Pedido.DoesNotExist:
            return Response({'detail': 'Pedido não encontrado'}, status=404)
        from .services import FinanceiroService
        key = request.headers.get('Idempotency-Key')
        idem, created = ensure_idempotency(key, request.user if request.user.is_authenticated else None, 'financeiro/receber_venda', {'pedido': slug, 'valor': str(valor_dec)})
        if idem and not created:
            return Response({'pedido': pedido.slug, 'valor': f"{valor_dec:.2f}"})
        try:
            FinanceiroService.receber_venda(pedido, valor_dec)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        log_action(request.user if request.user.is_authenticated else None, 'receive', 'Pedido', pedido.slug, {'valor': f"{valor_dec:.2f}"})
        return Response({'pedido': pedido.slug, 'valor': f"{valor_dec:.2f}"})

    @action(detail=False, methods=['get'])
    def saldo_caixa(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        deb = qs.filter(debit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0
        cred = qs.filter(credit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0
        saldo = deb - cred
        return Response({'entrada': f"{deb:.2f}", 'saida': f"{cred:.2f}", 'saldo': f"{saldo:.2f}"})

    @action(detail=False, methods=['get'])
    def a_receber(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        usuario = request.query_params.get('usuario')
        cache_key = f"ar_ped:{start}:{end}:{cost_center}:{usuario}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset()
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            import hashlib
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        if usuario:
            qs = qs.filter(pedido__usuario__username=usuario)
        pedidos = {}
        for le in qs:
            key = le.pedido_id
            if not key:
                continue
            if key not in pedidos:
                pedidos[key] = {'pedido': le.pedido.slug, 'usuario': str(le.pedido.usuario), 'sale_total': 0.0, 'received_total': 0.0}
            if le.debit_account == 'Clientes':
                pedidos[key]['sale_total'] += float(le.valor)
            if le.credit_account == 'Clientes':
                pedidos[key]['received_total'] += float(le.valor)
        result = []
        for v in pedidos.values():
            outstanding = v['sale_total'] - v['received_total']
            if outstanding > 0:
                v['outstanding'] = f"{outstanding:.2f}"
                v['sale_total'] = f"{v['sale_total']:.2f}"
                v['received_total'] = f"{v['received_total']:.2f}"
                result.append(v)
        data = sorted(result, key=lambda x: x['pedido'])
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        import hashlib
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def a_receber_cliente(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"ar_cli:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset().select_related('pedido__usuario')
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            import hashlib
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        clientes = {}
        for le in qs:
            if not le.pedido_id:
                continue
            user_key = le.pedido.usuario.username
            clientes.setdefault(user_key, {'usuario': user_key, 'sale_total': 0.0, 'received_total': 0.0})
            if le.debit_account == 'Clientes':
                clientes[user_key]['sale_total'] += float(le.valor)
            if le.credit_account == 'Clientes':
                clientes[user_key]['received_total'] += float(le.valor)
        data = []
        for k, v in clientes.items():
            outstanding = v['sale_total'] - v['received_total']
            if outstanding > 0:
                data.append({'usuario': k, 'outstanding': f"{outstanding:.2f}", 'sale_total': f"{v['sale_total']:.2f}", 'received_total': f"{v['received_total']:.2f}"})
        data = sorted(data, key=lambda x: x['usuario'])
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        import hashlib
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def posicao_pedido(self, request):
        slug = request.query_params.get('pedido')
        from vendas.models import Pedido
        try:
            pedido = Pedido.objects.get(slug=slug)
        except Pedido.DoesNotExist:
            return Response({'detail': 'Pedido não encontrado'}, status=404)
        qs = self.get_queryset().filter(pedido=pedido)
        sale = sum((le.valor for le in qs.filter(debit_account='Clientes')), 0)
        recv = sum((le.valor for le in qs.filter(credit_account='Clientes')), 0)
        outstanding = sale - recv
        hist = [{'descricao': le.descricao, 'debit': le.debit_account, 'credit': le.credit_account, 'valor': f"{le.valor:.2f}", 'criado_em': le.criado_em.isoformat()} for le in qs.order_by('criado_em')]
        return Response({'pedido': pedido.slug, 'sale_total': f"{sale:.2f}", 'received_total': f"{recv:.2f}", 'outstanding': f"{outstanding:.2f}", 'historico': hist})

    @action(detail=False, methods=['get'])
    def a_receber_aging(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"ar_aging:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset()
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            log_action(request.user if request.user.is_authenticated else None, 'list', 'Aging', None, {'params': dict(request.query_params)})
            return resp
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.datetime.fromisoformat(end) if end else None
        pedidos = {}
        for le in qs.order_by('criado_em'):
            if not le.pedido_id:
                continue
            if le.debit_account == 'Clientes' or le.credit_account == 'Clientes':
                p = pedidos.setdefault(le.pedido_id, {'pedido': le.pedido.slug, 'usuario': le.pedido.usuario.username if le.pedido and le.pedido.usuario else 'desconhecido', 'sale': 0.0, 'recv': 0.0, 'first_date': None})
                if le.debit_account == 'Clientes':
                    p['sale'] += float(le.valor)
                    p['first_date'] = p['first_date'] or le.criado_em
                if le.credit_account == 'Clientes':
                    p['recv'] += float(le.valor)
                    p['first_date'] = p['first_date'] or le.criado_em
        buckets = []
        for v in pedidos.values():
            out = v['sale'] - v['recv']
            if out <= 0:
                continue
            base = ref_date or v['first_date']
            delta = (base.date() - v['first_date'].date()).days if base else 0
            if delta <= 30:
                b = '0-30'
            elif delta <= 60:
                b = '31-60'
            elif delta <= 90:
                b = '61-90'
            else:
                b = '90+'
            buckets.append({'pedido': v['pedido'], 'usuario': v['usuario'], 'bucket': b, 'outstanding': f"{out:.2f}"})
        data = sorted(buckets, key=lambda x: (x['usuario'], x['bucket']))
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'list', 'Aging', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def a_receber_aging_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"ar_aging_csv:{start}:{end}:{cost_center}"
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.datetime.fromisoformat(end) if end else None
        pedidos = {}
        for le in qs.order_by('criado_em'):
            if not le.pedido_id:
                continue
            if le.debit_account == 'Clientes' or le.credit_account == 'Clientes':
                p = pedidos.setdefault(le.pedido_id, {'pedido': le.pedido.slug, 'usuario': le.pedido.usuario.username if le.pedido and le.pedido.usuario else 'desconhecido', 'sale': 0.0, 'recv': 0.0, 'first_date': None})
                if le.debit_account == 'Clientes':
                    p['sale'] += float(le.valor)
                    p['first_date'] = p['first_date'] or le.criado_em
                if le.credit_account == 'Clientes':
                    p['recv'] += float(le.valor)
                    p['first_date'] = p['first_date'] or le.criado_em
        rows = ["pedido,usuario,bucket,outstanding"]
        for v in pedidos.values():
            out = v['sale'] - v['recv']
            if out <= 0:
                continue
            base = ref_date or v['first_date']
            delta = (base.date() - v['first_date'].date()).days if base else 0
            if delta <= 30:
                b = '0-30'
            elif delta <= 60:
                b = '31-60'
            elif delta <= 90:
                b = '61-90'
            else:
                b = '90+'
            rows.append(f"{v['pedido']},{v['usuario']},{b},{out:.2f}")
        from django.http import HttpResponse
        csv = "\n".join(rows) + "\n"
        cached = cache.get(cache_key)
        if cached == csv:
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(csv.encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                log_action(request.user if request.user.is_authenticated else None, 'export', 'AgingCSV', None, {'params': dict(request.query_params)})
                return resp
        cache.set(cache_key, csv, 60)
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_a_receber_aging.csv\"'
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'export', 'AgingCSV', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def livro_caixa(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        from django.db.models import Sum
        import datetime
        if start:
            saldo_in = (qs.filter(criado_em__lt=start, debit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0) - (qs.filter(criado_em__lt=start, credit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0)
        else:
            saldo_in = 0
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        days = {}
        for le in qs.order_by('criado_em'):
            d = le.criado_em.date().isoformat()
            agg = days.setdefault(d, {'entrada': 0.0, 'saida': 0.0})
            if le.debit_account == 'Caixa':
                agg['entrada'] += float(le.valor)
            if le.credit_account == 'Caixa':
                agg['saida'] += float(le.valor)
        saldo = float(saldo_in)
        out = []
        for d in sorted(days):
            entrada = days[d]['entrada']
            saida = days[d]['saida']
            saldo = saldo + entrada - saida
            out.append({'data': d, 'entrada': f"{entrada:.2f}", 'saida': f"{saida:.2f}", 'saldo': f"{saldo:.2f}"})
        last = self.get_queryset().order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{out}".encode()).hexdigest()
        resp = Response({'saldo_inicial': f"{float(saldo_in):.2f}", 'dias': out, 'saldo_final': f"{saldo:.2f}"})
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'list', 'Caixa', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def livro_caixa_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset()
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        from django.db.models import Sum
        if start:
            saldo_in = (qs.filter(criado_em__lt=start, debit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0) - (qs.filter(criado_em__lt=start, credit_account='Caixa').aggregate(Sum('valor'))['valor__sum'] or 0)
        else:
            saldo_in = 0
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        days = {}
        for le in qs.order_by('criado_em'):
            d = le.criado_em.date().isoformat()
            agg = days.setdefault(d, {'entrada': 0.0, 'saida': 0.0})
            if le.debit_account == 'Caixa':
                agg['entrada'] += float(le.valor)
            if le.credit_account == 'Caixa':
                agg['saida'] += float(le.valor)
        saldo = float(saldo_in)
        rows = ["data,entrada,saida,saldo"]
        for d in sorted(days):
            entrada = days[d]['entrada']
            saida = days[d]['saida']
            saldo = saldo + entrada - saida
            rows.append(f"{d},{entrada:.2f},{saida:.2f},{saldo:.2f}")
        from django.http import HttpResponse
        csv = "\n".join(rows) + "\n"
        last = self.get_queryset().order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_livro_caixa.csv\"'
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'export', 'CaixaCSV', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def cliente_posicao(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"cli_pos:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = self.get_queryset().select_related('pedido__usuario')
            if start:
                qs = qs.filter(criado_em__gte=start)
            if end:
                qs = qs.filter(criado_em__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(f"{cached}".encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
            resp = Response(cached)
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            log_action(request.user if request.user.is_authenticated else None, 'list', 'CliPos', None, {'params': dict(request.query_params)})
            return resp
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.datetime.fromisoformat(end) if end else None
        clientes = {}
        for le in qs.order_by('criado_em'):
            if not le.pedido_id:
                continue
            user_key = le.pedido.usuario.username if le.pedido and le.pedido.usuario else 'desconhecido'
            c = clientes.setdefault(user_key, {'usuario': user_key, 'sale': 0.0, 'recv': 0.0, 'first_date': None})
            if le.debit_account == 'Clientes':
                c['sale'] += float(le.valor)
                c['first_date'] = c['first_date'] or le.criado_em
            if le.credit_account == 'Clientes':
                c['recv'] += float(le.valor)
                c['first_date'] = c['first_date'] or le.criado_em
        data = []
        for k, v in clientes.items():
            out = v['sale'] - v['recv']
            if out <= 0:
                continue
            base = ref_date or v['first_date']
            delta = (base.date() - v['first_date'].date()).days if base else 0
            if delta <= 30:
                b = '0-30'
            elif delta <= 60:
                b = '31-60'
            elif delta <= 90:
                b = '61-90'
            else:
                b = '90+'
            data.append({'usuario': k, 'sale_total': f"{v['sale']:.2f}", 'received_total': f"{v['recv']:.2f}", 'outstanding': f"{out:.2f}", 'bucket': b})
        cache.set(cache_key, data, 60)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(sorted(data, key=lambda x: x['usuario']))
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'list', 'CliPos', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def cliente_posicao_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.datetime.fromisoformat(end) if end else None
        clientes = {}
        for le in qs.order_by('criado_em'):
            if not le.pedido_id:
                continue
            user_key = le.pedido.usuario.username if le.pedido and le.pedido.usuario else 'desconhecido'
            c = clientes.setdefault(user_key, {'sale': 0.0, 'recv': 0.0, 'first_date': None})
            if le.debit_account == 'Clientes':
                c['sale'] += float(le.valor)
                c['first_date'] = c['first_date'] or le.criado_em
            if le.credit_account == 'Clientes':
                c['recv'] += float(le.valor)
                c['first_date'] = c['first_date'] or le.criado_em
        rows = ["usuario,sale_total,received_total,outstanding,bucket"]
        for k, v in clientes.items():
            out = v['sale'] - v['recv']
            if out <= 0:
                continue
            base = ref_date or v['first_date']
            delta = (base.date() - v['first_date'].date()).days if base else 0
            if delta <= 30:
                b = '0-30'
            elif delta <= 60:
                b = '31-60'
            elif delta <= 90:
                b = '61-90'
            else:
                b = '90+'
            rows.append(f"{k},{v['sale']:.2f},{v['recv']:.2f},{out:.2f},{b}")
        from django.http import HttpResponse, HttpResponseNotModified
        csv = "\n".join(rows) + "\n"
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        if request.headers.get('If-None-Match') == etag_val:
            resp = HttpResponseNotModified()
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            log_action(request.user if request.user.is_authenticated else None, 'export', 'CliPosCSV', None, {'params': dict(request.query_params)})
            return resp
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_cliente_posicao.csv\"'
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'export', 'CliPosCSV', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def a_receber_aging_due(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = Title.objects.filter(tipo='AR')
        if start:
            qs = qs.filter(due_date__gte=start)
        if end:
            qs = qs.filter(due_date__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.date.fromisoformat(end) if end else datetime.date.today()
        data = []
        for t in qs.select_related('pedido__usuario'):
            out = float(t.valor) - float(t.valor_pago or 0)
            if out <= 0:
                continue
            delta = (ref_date - t.due_date).days
            if delta <= 0:
                b = '0-30'
            elif delta <= 30:
                b = '31-60'
            elif delta <= 60:
                b = '61-90'
            else:
                b = '90+'
            data.append({'pedido': t.pedido.slug if t.pedido else None, 'usuario': t.pedido.usuario.username if t.pedido and t.pedido.usuario else None, 'bucket': b, 'outstanding': f"{out:.2f}", 'due_date': t.due_date.isoformat()})
        data = sorted(data, key=lambda x: (x['usuario'] or '', x['due_date']))
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        if request.headers.get('If-None-Match') == etag_val:
            from django.http import HttpResponseNotModified
            resp = HttpResponseNotModified()
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'list', 'AgingDue', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def a_receber_aging_due_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = Title.objects.filter(tipo='AR')
        if start:
            qs = qs.filter(due_date__gte=start)
        if end:
            qs = qs.filter(due_date__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        import datetime
        ref_date = datetime.date.fromisoformat(end) if end else datetime.date.today()
        rows = ["pedido,usuario,due_date,bucket,outstanding"]
        for t in qs.select_related('pedido__usuario'):
            out = float(t.valor) - float(t.valor_pago or 0)
            if out <= 0:
                continue
            delta = (ref_date - t.due_date).days
            if delta <= 0:
                b = '0-30'
            elif delta <= 30:
                b = '31-60'
            elif delta <= 60:
                b = '61-90'
            else:
                b = '90+'
            rows.append(f"{t.pedido.slug if t.pedido else ''},{t.pedido.usuario.username if t.pedido and t.pedido.usuario else ''},{t.due_date.isoformat()},{b},{out:.2f}")
        from django.http import HttpResponse
        csv = "\n".join(rows) + "\n"
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        if request.headers.get('If-None-Match') == etag_val:
            from django.http import HttpResponseNotModified
            resp = HttpResponseNotModified()
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_a_receber_aging_due.csv\"'
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'export', 'AgingDue', None, {'params': dict(request.query_params)})
        return resp

    @action(detail=False, methods=['get'])
    def a_receber_csv(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"ar_csv:{start}:{end}:{cost_center}"
        qs = self.get_queryset().select_related('pedido__usuario')
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        pedidos = {}
        for le in qs:
            key = le.pedido_id
            if not key:
                continue
            if key not in pedidos:
                pedidos[key] = {'pedido': le.pedido.slug, 'usuario': le.pedido.usuario.username, 'sale_total': 0.0, 'received_total': 0.0}
            if le.debit_account == 'Clientes':
                pedidos[key]['sale_total'] += float(le.valor)
            if le.credit_account == 'Clientes':
                pedidos[key]['received_total'] += float(le.valor)
        rows = ["pedido,usuario,sale_total,received_total,outstanding"]
        for v in pedidos.values():
            outstanding = v['sale_total'] - v['received_total']
            if outstanding > 0:
                rows.append(f"{v['pedido']},{v['usuario']},{v['sale_total']:.2f},{v['received_total']:.2f},{outstanding:.2f}")
        from django.http import HttpResponse
        csv = "\n".join(rows) + "\n"
        cached = cache.get(cache_key)
        if cached == csv:
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            etag_val = hashlib.sha256(csv.encode()).hexdigest()
            if request.headers.get('If-None-Match') == etag_val:
                from django.http import HttpResponseNotModified
                resp = HttpResponseNotModified()
                if last:
                    resp['Last-Modified'] = http_date(last.timestamp())
                resp['ETag'] = etag_val
                return resp
        cache.set(cache_key, csv, 60)
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_a_receber.csv\"'
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp


class AccountViewSet(viewsets.ModelViewSet):
    """CRUD de contas contábeis."""
    queryset = Account.objects.all().order_by('codigo')
    serializer_class = AccountSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'


class CostCenterViewSet(viewsets.ModelViewSet):
    """CRUD de centros de custo."""
    queryset = CostCenter.objects.all().order_by('codigo')
    serializer_class = CostCenterSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'


class TitleViewSet(viewsets.ModelViewSet):
    """CRUD e operações sobre títulos (AR/AP)."""
    queryset = Title.objects.select_related('pedido', 'compra', 'usuario', 'cost_center').order_by('-criado_em')
    serializer_class = TitleSerializer
    permission_classes = [IsFinanceiroOrAdmin]
    throttle_scope = 'financeiro'
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tipo', 'status', 'due_date', 'cost_center__codigo', 'pedido__slug', 'compra__slug']
    ordering_fields = ['due_date', 'valor', 'valor_pago', 'criado_em']
    def list(self, request, *args, **kwargs):
        """Listagem com filtros/ordenação e ETag/Last-Modified."""
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            data = TitleSerializer(page, many=True).data
            etag_val = hashlib.sha256(str([(d['id'], d['valor'], d['valor_pago'], d['due_date']) for d in data]).encode()).hexdigest()
            resp = self.get_paginated_response(data)
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            log_action(request.user if request.user.is_authenticated else None, 'list', 'Title', None, {'params': dict(request.query_params)})
            return resp
        data = TitleSerializer(qs, many=True).data
        etag_val = hashlib.sha256(str([(d['id'], d['valor'], d['valor_pago'], d['due_date']) for d in data]).encode()).hexdigest()
        resp = Response(data)
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'list', 'Title', None, {'params': dict(request.query_params)})
        return resp
    @action(detail=False, methods=['get'])
    def csv(self, request):
        """Exporta títulos filtrados/ordenados em CSV com ETag."""
        qs = self.filter_queryset(self.get_queryset())
        rows = ["id,tipo,status,pedido,compra,due_date,valor,valor_pago,cost_center"]
        for t in qs:
            rows.append(f"{t.id},{t.tipo},{t.status},{t.pedido.slug if t.pedido else ''},{t.compra.slug if t.compra else ''},{t.due_date.isoformat()},{t.valor:.2f},{(t.valor_pago or 0):.2f},{t.cost_center.codigo if t.cost_center else ''}")
        from django.http import HttpResponse
        csv = "\n".join(rows) + "\n"
        etag_val = hashlib.sha256(csv.encode()).hexdigest()
        if request.headers.get('If-None-Match') == etag_val:
            from django.http import HttpResponseNotModified
            resp = HttpResponseNotModified()
            last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
            if last:
                resp['Last-Modified'] = http_date(last.timestamp())
            resp['ETag'] = etag_val
            return resp
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename=\"financeiro_titulos.csv\"'
        last = qs.order_by('-criado_em').values_list('criado_em', flat=True).first()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        log_action(request.user if request.user.is_authenticated else None, 'export', 'Title', None, {'params': dict(request.query_params)})
        return resp
    @action(detail=True, methods=['post'])
    def receber(self, request, pk=None):
        """Recebe valor de título AR (baixa total/parcial)."""
        from decimal import Decimal
        t = self.get_object()
        if t.tipo != Title.Tipo.AR:
            return Response({'detail': 'Título não é AR'}, status=400)
        valor = request.data.get('valor')
        try:
            valor_dec = Decimal(str(valor))
        except Exception:
            return Response({'detail': 'Valor inválido'}, status=400)
        from .services import FinanceiroService
        try:
            FinanceiroService.receber_venda(t.pedido, valor_dec)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        t.valor_pago = (t.valor_pago or 0) + valor_dec
        if t.valor_pago >= t.valor:
            t.status = Title.Status.QUITADO
        t.save(update_fields=['valor_pago', 'status'])
        return Response(TitleSerializer(t).data)
    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        """Paga valor de título AP (baixa total/parcial)."""
        from decimal import Decimal
        t = self.get_object()
        if t.tipo != Title.Tipo.AP:
            return Response({'detail': 'Título não é AP'}, status=400)
        valor = request.data.get('valor')
        try:
            valor_dec = Decimal(str(valor))
        except Exception:
            return Response({'detail': 'Valor inválido'}, status=400)
        from .services import FinanceiroService
        FinanceiroService.registrar_pagamento_compra(t.compra, valor_dec)
        t.valor_pago = (t.valor_pago or 0) + valor_dec
        if t.valor_pago >= t.valor:
            t.status = Title.Status.QUITADO
        t.save(update_fields=['valor_pago', 'status'])
        return Response(TitleSerializer(t).data)
    @action(detail=False, methods=['post'])
    def add_parcela(self, request):
        """Adiciona parcela a um título."""
        ser = TitleParcelSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        p = ser.save()
        return Response(TitleParcelSerializer(p).data, status=201)
    @action(detail=True, methods=['post'])
    def receber_parcela(self, request, pk=None):
        """Recebe valor de uma parcela de título AR."""
        from decimal import Decimal
        t = self.get_object()
        pid = request.data.get('parcela')
        try:
            p = t.parcelas.get(id=pid)
        except TitleParcel.DoesNotExist:
            return Response({'detail': 'Parcela não encontrada'}, status=404)
        valor = request.data.get('valor')
        try:
            v = Decimal(str(valor))
        except Exception:
            return Response({'detail': 'Valor inválido'}, status=400)
        if t.tipo != Title.Tipo.AR:
            return Response({'detail': 'Título não é AR'}, status=400)
        from .services import FinanceiroService
        try:
            FinanceiroService.receber_venda(t.pedido, v)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        p.valor_pago = (p.valor_pago or 0) + v
        if p.valor_pago >= p.valor:
            p.status = 'Quitado'
        p.save(update_fields=['valor_pago', 'status'])
        t.valor_pago = (t.valor_pago or 0) + v
        if t.valor_pago >= t.valor:
            t.status = Title.Status.QUITADO
        t.save(update_fields=['valor_pago', 'status'])
        return Response(TitleSerializer(t).data)
    @action(detail=True, methods=['post'])
    def pagar_parcela(self, request, pk=None):
        """Paga valor de uma parcela de título AP."""
        from decimal import Decimal
        t = self.get_object()
        pid = request.data.get('parcela')
        try:
            p = t.parcelas.get(id=pid)
        except TitleParcel.DoesNotExist:
            return Response({'detail': 'Parcela não encontrada'}, status=404)
        valor = request.data.get('valor')
        try:
            v = Decimal(str(valor))
        except Exception:
            return Response({'detail': 'Valor inválido'}, status=400)
        if t.tipo != Title.Tipo.AP:
            return Response({'detail': 'Título não é AP'}, status=400)
        from .services import FinanceiroService
        FinanceiroService.registrar_pagamento_compra(t.compra, v)
        p.valor_pago = (p.valor_pago or 0) + v
        if p.valor_pago >= p.valor:
            p.status = 'Quitado'
        p.save(update_fields=['valor_pago', 'status'])
        t.valor_pago = (t.valor_pago or 0) + v
        if t.valor_pago >= t.valor:
            t.status = Title.Status.QUITADO
        t.save(update_fields=['valor_pago', 'status'])
        return Response(TitleSerializer(t).data)
    @action(detail=True, methods=['post'])
    def update_parcela(self, request, pk=None):
        """Atualiza valor e due_date de uma parcela não quitada."""
        t = self.get_object()
        pid = request.data.get('parcela')
        try:
            p = t.parcelas.get(id=pid)
        except TitleParcel.DoesNotExist:
            return Response({'detail': 'Parcela não encontrada'}, status=404)
        if p.status == 'Quitado':
            return Response({'detail': 'Parcela quitada não pode ser alterada'}, status=400)
        from decimal import Decimal
        val = request.data.get('valor')
        due = request.data.get('due_date')
        updates = {}
        if val is not None:
            try:
                v = Decimal(str(val))
            except Exception:
                return Response({'detail': 'Valor inválido'}, status=400)
            diff = v - p.valor
            updates['valor'] = v
            t.valor = (t.valor or 0) + diff
        if due is not None:
            import datetime
            try:
                d = datetime.date.fromisoformat(due)
            except Exception:
                return Response({'detail': 'due_date inválida'}, status=400)
            updates['due_date'] = d
        for k, v in updates.items():
            setattr(p, k, v)
        p.save(update_fields=list(updates.keys()))
        t.save(update_fields=['valor'])
        return Response(TitleSerializer(t).data)
    @action(detail=True, methods=['post'])
    def remove_parcela(self, request, pk=None):
        """Remove parcela sem pagamento, ajustando o valor do título."""
        t = self.get_object()
        pid = request.data.get('parcela')
        try:
            p = t.parcelas.get(id=pid)
        except TitleParcel.DoesNotExist:
            return Response({'detail': 'Parcela não encontrada'}, status=404)
        if p.valor_pago and p.valor_pago > 0:
            return Response({'detail': 'Parcela com pagamento não pode ser removida'}, status=400)
        from decimal import Decimal
        t.valor = (t.valor or Decimal('0')) - p.valor
        p.delete()
        t.save(update_fields=['valor'])
        return Response(TitleSerializer(t).data)

class UserDefaultCostCenterViewSet(viewsets.ModelViewSet):
    """Mapeia centro de custo padrão por usuário."""
    queryset = UserDefaultCostCenter.objects.select_related('user', 'cost_center').all()
    serializer_class = UserDefaultCostCenterSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'
