"""Views de Relatórios: faturamento, itens, categorias e estoque por depósito/motivo.

Implementa caching via Django cache + ETag/Last-Modified para eficiência,
além de versões CSV dos relatórios.
"""
from django.db.models import Sum, F
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from vendas.models import Pedido, ItemPedido, Categoria
from estoque.models import StockMovement
import hashlib
from django.utils.http import http_date
from django.utils import timezone


class RelatorioViewSet(viewsets.ViewSet):
    """Endpoints de relatórios administrativos com throttling."""
    permission_classes = [permissions.IsAdminUser]
    throttle_scope = 'relatorios'

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Resumo geral: pedidos por status, faturamento à vista/a prazo, AR pendente e saldo de estoque."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs_ped = Pedido.objects.all()
        if start:
            qs_ped = qs_ped.filter(data_criacao__gte=start)
        if end:
            qs_ped = qs_ped.filter(data_criacao__lte=end)
        if cost_center:
            qs_ped = qs_ped.filter(cost_center__codigo=cost_center)
        total_pedidos = qs_ped.count()
        por_status = {
            s: qs_ped.filter(status=s).count()
            for s, _ in Pedido.Status.choices
        }
        from django.db.models import Sum
        le = LedgerEntry.objects.all()
        if cost_center:
            le = le.filter(cost_center__codigo=cost_center)
        faturamento_total = qs_ped.aggregate(total=Sum('total'))['total'] or 0
        faturamento_avista = le.filter(debit_account="Caixa", credit_account="Receita de Vendas").aggregate(Sum('valor'))['valor__sum'] or 0
        faturamento_prazo = le.filter(debit_account="Clientes", credit_account="Receita de Vendas").aggregate(Sum('valor'))['valor__sum'] or 0
        recebimentos_clientes = le.filter(debit_account="Caixa", credit_account="Clientes").aggregate(Sum('valor'))['valor__sum'] or 0
        ar_outstanding = (faturamento_prazo or 0) - (recebimentos_clientes or 0)
        mv = StockMovement.objects.all()
        if start:
            mv = mv.filter(criado_em__gte=start)
        if end:
            mv = mv.filter(criado_em__lte=end)
        # saldo total de estoque (agregado)
        in_sum = mv.filter(tipo=StockMovement.Tipo.IN).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        out_sum = mv.filter(tipo=StockMovement.Tipo.OUT).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        adj_sum = mv.filter(tipo=StockMovement.Tipo.ADJUST).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        saldo_estoque_total = int(in_sum) - int(out_sum) + int(adj_sum)
        data = {
            'total_pedidos': total_pedidos,
            'pedidos_por_status': por_status,
            'faturamento_total': f"{faturamento_total:.2f}",
            'faturamento_avista': f"{(faturamento_avista or 0):.2f}",
            'faturamento_prazo': f"{(faturamento_prazo or 0):.2f}",
            'ar_outstanding': f"{(ar_outstanding or 0):.2f}",
            'saldo_estoque_total': saldo_estoque_total,
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def faturamento(self, request):
        """Total faturado e contagem de pedidos, com cache e ETag."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        cache_key = f"rel_faturamento:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = Pedido.objects.all()
            if start:
                qs = qs.filter(data_criacao__gte=start)
            if end:
                qs = qs.filter(data_criacao__lte=end)
            if cost_center:
                qs = qs.filter(cost_center__codigo=cost_center)
            last = qs.order_by('-data_criacao').values_list('data_criacao', flat=True).first()
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
        qs = Pedido.objects.all()
        if start:
            qs = qs.filter(data_criacao__gte=start)
        if end:
            qs = qs.filter(data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        total = qs.aggregate(total=Sum('total'))['total'] or 0
        count = qs.count()
        data = {'total_faturamento': f"{total:.2f}", 'pedidos': count}
        cache.set(cache_key, data, 60)
        last = qs.order_by('-data_criacao').values_list('data_criacao', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        resp = Response(data)
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def itens(self, request):
        """Top de itens vendidos, paginação simples e ETag."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        limit = int(request.query_params.get('limit', 10))
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', limit))
        cache_key = f"rel_itens:{start}:{end}:{cost_center}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = ItemPedido.objects.select_related('produto', 'pedido__cost_center')
            if start:
                qs = qs.filter(pedido__data_criacao__gte=start)
            if end:
                qs = qs.filter(pedido__data_criacao__lte=end)
            if cost_center:
                qs = qs.filter(pedido__cost_center__codigo=cost_center)
            last = qs.order_by('-pedido__data_criacao').values_list('pedido__data_criacao', flat=True).first()
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
        qs = ItemPedido.objects.select_related('produto', 'pedido__cost_center')
        if start:
            qs = qs.filter(pedido__data_criacao__gte=start)
        if end:
            qs = qs.filter(pedido__data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        agg = qs.values('produto__slug', 'produto__nome').annotate(
            quantidade_total=Sum('quantidade'),
            faturamento_item=Sum(F('quantidade') * F('preco_unitario')),
        ).order_by('-quantidade_total')
        total = agg.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        agg = agg[start_idx:end_idx]
        data = [{
            'produto_slug': a['produto__slug'],
            'produto_nome': a['produto__nome'],
            'quantidade_total': a['quantidade_total'],
            'faturamento_item': f"{a['faturamento_item']:.2f}" if a['faturamento_item'] else "0.00",
        } for a in agg]
        cache.set(cache_key, data, 60)
        resp = Response(data)
        resp['X-Total-Count'] = str(total)
        resp['X-Page'] = str(page)
        resp['X-Page-Size'] = str(page_size)
        last = qs.order_by('-pedido__data_criacao').values_list('pedido__data_criacao', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def faturamento_csv(self, request):
        """CSV de faturamento por período e cost center."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = Pedido.objects.all()
        if start:
            qs = qs.filter(data_criacao__gte=start)
        if end:
            qs = qs.filter(data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(cost_center__codigo=cost_center)
        total = qs.aggregate(total=Sum('total'))['total'] or 0
        count = qs.count()
        csv = "total_faturamento,pedidos,cost_center\n" + f"{total:.2f},{count},{cost_center or ''}\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="faturamento.csv"'
        return resp

    @action(detail=False, methods=['get'])
    def itens_csv(self, request):
        """CSV dos itens mais vendidos."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        limit = int(request.query_params.get('limit', 10))
        qs = ItemPedido.objects.select_related('produto', 'pedido__cost_center')
        if start:
            qs = qs.filter(pedido__data_criacao__gte=start)
        if end:
            qs = qs.filter(pedido__data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        agg = qs.values('produto__slug', 'produto__nome').annotate(
            quantidade_total=Sum('quantidade'),
            faturamento_item=Sum(F('quantidade') * F('preco_unitario')),
        ).order_by('-quantidade_total')[:limit]
        rows = ["produto_slug,produto_nome,quantidade_total,faturamento_item,cost_center"]
        for a in agg:
            faturamento = f"{a['faturamento_item']:.2f}" if a['faturamento_item'] else "0.00"
            rows.append(f"{a['produto__slug']},{a['produto__nome']},{a['quantidade_total']},{faturamento},{cost_center or ''}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="itens.csv"'
        return resp

    @action(detail=False, methods=['get'])
    def categorias_csv(self, request):
        """CSV de agregação por categorias."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        qs = ItemPedido.objects.select_related('produto__categoria', 'pedido__cost_center')
        if start:
            qs = qs.filter(pedido__data_criacao__gte=start)
        if end:
            qs = qs.filter(pedido__data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        agg = qs.values('produto__categoria__slug', 'produto__categoria__nome').annotate(
            quantidade_total=Sum('quantidade'),
            faturamento_categoria=Sum(F('quantidade') * F('preco_unitario')),
        ).order_by('-quantidade_total')
        rows = ["categoria_slug,categoria_nome,quantidade_total,faturamento_categoria,cost_center"]
        for a in agg:
            faturamento = f"{a['faturamento_categoria']:.2f}" if a['faturamento_categoria'] else "0.00"
            rows.append(f"{a['produto__categoria__slug']},{a['produto__categoria__nome']},{a['quantidade_total']},{faturamento},{cost_center or ''}")
        csv = "\n".join(rows) + "\n"
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="categorias.csv"'
        return resp

    @action(detail=False, methods=['get'])
    def categorias(self, request):
        """Agregação por categorias com cache e ETag."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        cost_center = request.query_params.get('cost_center')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        cache_key = f"rel_categorias:{start}:{end}:{cost_center}"
        cached = cache.get(cache_key)
        if cached is not None:
            qs = ItemPedido.objects.select_related('produto__categoria', 'pedido__cost_center')
            if start:
                qs = qs.filter(pedido__data_criacao__gte=start)
            if end:
                qs = qs.filter(pedido__data_criacao__lte=end)
            if cost_center:
                qs = qs.filter(pedido__cost_center__codigo=cost_center)
            last = qs.order_by('-pedido__data_criacao').values_list('pedido__data_criacao', flat=True).first()
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
        qs = ItemPedido.objects.select_related('produto__categoria', 'pedido__cost_center')
        if start:
            qs = qs.filter(pedido__data_criacao__gte=start)
        if end:
            qs = qs.filter(pedido__data_criacao__lte=end)
        if cost_center:
            qs = qs.filter(pedido__cost_center__codigo=cost_center)
        agg = qs.values('produto__categoria__slug', 'produto__categoria__nome').annotate(
            quantidade_total=Sum('quantidade'),
            faturamento_categoria=Sum(F('quantidade') * F('preco_unitario')),
        ).order_by('-quantidade_total')
        total = agg.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        agg = agg[start_idx:end_idx]
        data = [{
            'categoria_slug': a['produto__categoria__slug'],
            'categoria_nome': a['produto__categoria__nome'],
            'quantidade_total': a['quantidade_total'],
            'faturamento_categoria': f"{a['faturamento_categoria']:.2f}" if a['faturamento_categoria'] else "0.00",
        } for a in agg]
        cache.set(cache_key, data, 60)
        resp = Response(data)
        resp['X-Total-Count'] = str(total)
        resp['X-Page'] = str(page)
        resp['X-Page-Size'] = str(page_size)
        last = qs.order_by('-pedido__data_criacao').values_list('pedido__data_criacao', flat=True).first()
        etag_val = hashlib.sha256(f"{data}".encode()).hexdigest()
        if last:
            resp['Last-Modified'] = http_date(last.timestamp())
        resp['ETag'] = etag_val
        return resp

    @action(detail=False, methods=['get'])
    def estoque_depositos(self, request):
        """Resumo de entradas/saídas/ajustes e saldo por depósito."""
        produto = request.query_params.get('produto')
        deposito_slug = request.query_params.get('deposito')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = StockMovement.objects.select_related('deposito', 'produto').order_by('-criado_em')
        if produto:
            qs = qs.filter(produto__slug=produto)
        if deposito_slug:
            qs = qs.filter(deposito__slug=deposito_slug)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        agg = {}
        for mv in qs.values('deposito__slug', 'tipo', 'quantidade'):
            dep = mv['deposito__slug'] or ''
            if dep not in agg:
                agg[dep] = {'IN': 0, 'OUT': 0, 'ADJUST': 0}
            agg[dep][mv['tipo']] += int(mv['quantidade'])
        data = []
        for dep, sums in agg.items():
            saldo = sums['IN'] - sums['OUT'] + sums['ADJUST']
            data.append({'deposito': dep or None, 'entradas': sums['IN'], 'saidas': sums['OUT'], 'ajustes': sums['ADJUST'], 'saldo': saldo})
        return Response(sorted(data, key=lambda x: x['deposito'] or ''))

    @action(detail=False, methods=['get'])
    def estoque_depositos_csv(self, request):
        """CSV de estoque por depósito."""
        produto = request.query_params.get('produto')
        deposito_slug = request.query_params.get('deposito')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = StockMovement.objects.select_related('deposito', 'produto').order_by('-criado_em')
        if produto:
            qs = qs.filter(produto__slug=produto)
        if deposito_slug:
            qs = qs.filter(deposito__slug=deposito_slug)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        agg = {}
        for mv in qs.values('deposito__slug', 'tipo', 'quantidade'):
            dep = mv['deposito__slug'] or ''
            if dep not in agg:
                agg[dep] = {'IN': 0, 'OUT': 0, 'ADJUST': 0}
            agg[dep][mv['tipo']] += int(mv['quantidade'])
        rows = ["deposito,entradas,saidas,ajustes,saldo"]
        for dep, sums in agg.items():
            saldo = sums['IN'] - sums['OUT'] + sums['ADJUST']
            rows.append(f"{dep},{sums['IN']},{sums['OUT']},{sums['ADJUST']},{saldo}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="estoque_depositos.csv"'
        return resp

    @action(detail=False, methods=['get'])
    def ajustes_motivo(self, request):
        """Resumo de ajustes agregados por motivo."""
        produto = request.query_params.get('produto')
        deposito_slug = request.query_params.get('deposito')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = StockMovement.objects.select_related('motivo_ajuste', 'produto', 'deposito').filter(tipo=StockMovement.Tipo.ADJUST).order_by('-criado_em')
        if produto:
            qs = qs.filter(produto__slug=produto)
        if deposito_slug:
            qs = qs.filter(deposito__slug=deposito_slug)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        agg = {}
        for mv in qs.values('motivo_ajuste__codigo', 'motivo_ajuste__nome', 'quantidade'):
            code = mv['motivo_ajuste__codigo'] or ''
            name = mv['motivo_ajuste__nome'] or ''
            key = (code, name)
            agg[key] = agg.get(key, 0) + int(mv['quantidade'])
        data = [{'motivo': k[0], 'nome': k[1], 'quantidade_ajustada': v} for k, v in agg.items()]
        return Response(sorted(data, key=lambda x: x['motivo'] or ''))

    @action(detail=False, methods=['get'])
    def ajustes_motivo_csv(self, request):
        """CSV de ajustes agregados por motivo."""
        produto = request.query_params.get('produto')
        deposito_slug = request.query_params.get('deposito')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = StockMovement.objects.select_related('motivo_ajuste', 'produto', 'deposito').filter(tipo=StockMovement.Tipo.ADJUST).order_by('-criado_em')
        if produto:
            qs = qs.filter(produto__slug=produto)
        if deposito_slug:
            qs = qs.filter(deposito__slug=deposito_slug)
        if start:
            qs = qs.filter(criado_em__gte=start)
        if end:
            qs = qs.filter(criado_em__lte=end)
        agg = {}
        for mv in qs.values('motivo_ajuste__codigo', 'motivo_ajuste__nome', 'quantidade'):
            code = mv['motivo_ajuste__codigo'] or ''
            name = mv['motivo_ajuste__nome'] or ''
            key = (code, name)
            agg[key] = agg.get(key, 0) + int(mv['quantidade'])
        rows = ["motivo,nome,quantidade_ajustada"]
        for (code, name), qty in agg.items():
            rows.append(f"{code},{name},{qty}")
        csv = "\n".join(rows) + "\n"
        from django.http import HttpResponse
        resp = HttpResponse(csv, content_type="text/csv")
        resp['Content-Disposition'] = 'attachment; filename="ajustes_motivo.csv"'
        return resp
