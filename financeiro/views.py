from datetime import datetime
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Sum
from .models import LedgerEntry, Account, CostCenter, UserDefaultCostCenter
from .serializers import LedgerEntrySerializer, AccountSerializer, CostCenterSerializer, UserDefaultCostCenterSerializer
from .permissions import IsSuperUser, IsFinanceiroOrAdmin
import hashlib
from django.utils.http import http_date


class LedgerEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LedgerEntry.objects.select_related('pedido', 'usuario')
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsFinanceiroOrAdmin]
    throttle_scope = 'financeiro'

    @action(detail=False, methods=['get'])
    def resumo(self, request):
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


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('codigo')
    serializer_class = AccountSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'


class CostCenterViewSet(viewsets.ModelViewSet):
    queryset = CostCenter.objects.all().order_by('codigo')
    serializer_class = CostCenterSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'


class UserDefaultCostCenterViewSet(viewsets.ModelViewSet):
    queryset = UserDefaultCostCenter.objects.select_related('user', 'cost_center').all()
    serializer_class = UserDefaultCostCenterSerializer
    permission_classes = [IsSuperUser]
    throttle_scope = 'financeiro'
