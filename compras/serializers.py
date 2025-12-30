from decimal import Decimal
from typing import List, Dict
from django.db import transaction
from rest_framework import serializers
from cadastro.models import Supplier
from vendas.models import Produto
from .models import PurchaseOrder, PurchaseItem
from estoque.services import EstoqueService
from financeiro.services import FinanceiroService
from auditoria.utils import log_action, ensure_idempotency
from django.utils import timezone


class PurchaseItemPayloadSerializer(serializers.Serializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    quantidade = serializers.IntegerField()
    custo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantidade deve ser > 0.")
        return value

    def validate_custo_unitario(self, value):
        if value < 0:
            raise serializers.ValidationError("Custo unitário não pode ser negativo.")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    fornecedor = serializers.SlugRelatedField(slug_field='slug', queryset=Supplier.objects.all())
    cost_center = serializers.CharField(write_only=True, required=False, allow_blank=True)
    deposito = serializers.CharField(write_only=True, required=False, allow_blank=True)
    itens_payload = serializers.ListField(child=PurchaseItemPayloadSerializer(), write_only=True, required=True)

    class Meta:
        model = PurchaseOrder
        fields = ['slug', 'fornecedor', 'documento', 'status', 'total', 'responsavel', 'criado_em', 'recebido_em', 'cost_center', 'deposito', 'itens_payload']
        read_only_fields = ['slug', 'status', 'total', 'responsavel', 'criado_em', 'recebido_em']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user and request.user.is_authenticated else None
        if not user:
            raise serializers.ValidationError("Usuário não autenticado.")
        itens_payload = validated_data.pop('itens_payload')
        cost_center_code = validated_data.pop('cost_center', None)
        deposito_slug = validated_data.pop('deposito', None)
        from estoque.models import Deposito
        deposito = Deposito.objects.filter(slug=deposito_slug).first() if deposito_slug else None
        key = request.headers.get('Idempotency-Key') if request else None
        idem, created = ensure_idempotency(key, user, 'compras/create', {'itens': [dict(produto=i['produto'].slug, quantidade=i['quantidade'], custo_unitario=str(i['custo_unitario'])) for i in itens_payload], 'cost_center': cost_center_code, 'deposito': deposito_slug})
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            last = PurchaseOrder.objects.filter(responsavel=user, criado_em__gte=since).order_by('-criado_em').first()
            if last:
                return last
        with transaction.atomic():
            order = PurchaseOrder.objects.create(fornecedor=validated_data['fornecedor'], documento=validated_data.get('documento', ''), responsavel=user, cost_center=None, deposito=deposito)
            itens_objs: List[PurchaseItem] = []
            total = Decimal('0.00')
            for item in itens_payload:
                pi = PurchaseItem.objects.create(order=order, produto=item['produto'], quantidade=int(item['quantidade']), custo_unitario=item['custo_unitario'])
                total += pi.subtotal()
                itens_objs.append(pi)
            order.total = total
            if cost_center_code:
                from financeiro.models import CostCenter
                cc = CostCenter.objects.filter(codigo=cost_center_code).first()
                if not cc:
                    raise serializers.ValidationError("Centro de custo inválido.")
                order.cost_center = cc
            order.save(update_fields=['total', 'cost_center'])
        log_action(user, 'create', 'PurchaseOrder', order.slug, {'total': str(total), 'itens_count': len(itens_objs), 'cost_center': order.cost_center.codigo if order.cost_center else None, 'deposito': order.deposito.slug if order.deposito else None})
        return order


class PurchaseReceiveSerializer(serializers.Serializer):
    order_slug = serializers.CharField()

    def validate_order_slug(self, value):
        from .models import PurchaseOrder
        if not PurchaseOrder.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Compra não encontrada.")
        return value

    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user if request and request.user and request.user.is_authenticated else None
        from .models import PurchaseOrder
        from django.utils import timezone as djtz
        order = PurchaseOrder.objects.select_related('deposito', 'fornecedor', 'cost_center').prefetch_related('itens__produto').get(slug=self.validated_data['order_slug'])
        if order.status == PurchaseOrder.Status.RECEBIDO:
            return order
        key = request.headers.get('Idempotency-Key') if request else None
        ensure_idempotency(key, user, 'compras/receber', {'order': order.slug})
        with transaction.atomic():
            from estoque.models import StockReceipt, StockReceiptItem
            recibo = StockReceipt.objects.create(
                fornecedor=order.fornecedor.nome,
                fornecedor_ref=order.fornecedor,
                documento=order.documento,
                responsavel=user,
                deposito=order.deposito,
                compra=order,
            )
            for item in order.itens.all():
                from decimal import Decimal
                current_qty = EstoqueService.saldo_produto(item.produto)
                current_cost = Decimal(item.produto.custo or 0)
                new_qty = current_qty + int(item.quantidade)
                unit_cost = Decimal(item.custo_unitario or 0)
                EstoqueService.registrar_entrada(produto=item.produto, quantidade=item.quantidade, origem_slug=order.slug, responsavel=user, deposito=order.deposito)
                StockReceiptItem.objects.create(recebimento=recibo, produto=item.produto, quantidade=item.quantidade, custo_unitario=item.custo_unitario)
                if new_qty > 0:
                    item.produto.custo = (current_qty * current_cost + int(item.quantidade) * unit_cost) / Decimal(new_qty)
                else:
                    item.produto.custo = unit_cost
                item.produto.save(update_fields=['custo'])
            FinanceiroService.registrar_compra(order)
            order.status = PurchaseOrder.Status.RECEBIDO
            order.recebido_em = djtz.now()
            order.save(update_fields=['status', 'recebido_em'])
        log_action(user, 'receive', 'PurchaseOrder', order.slug, {'total': str(order.total), 'itens_count': order.itens.count(), 'deposito': order.deposito.slug if order.deposito else None})
        return order


class PurchasePaySerializer(serializers.Serializer):
    order_slug = serializers.CharField()
    valor = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        from .models import PurchaseOrder
        slug = attrs.get('order_slug')
        valor = attrs.get('valor')
        order = PurchaseOrder.objects.filter(slug=slug).first()
        if not order:
            raise serializers.ValidationError("Compra não encontrada.")
        if valor <= 0:
            raise serializers.ValidationError("Valor deve ser > 0.")
        aberto = (order.total or 0) - (order.valor_pago or 0)
        if valor > aberto:
            raise serializers.ValidationError("Valor excede o saldo a pagar.")
        return attrs

    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user if request and request.user and request.user.is_authenticated else None
        from .models import PurchaseOrder
        order = PurchaseOrder.objects.get(slug=self.validated_data['order_slug'])
        from django.db import transaction
        from django.utils import timezone as djtz
        from financeiro.services import FinanceiroService
        key = request.headers.get('Idempotency-Key') if request else None
        ensure_idempotency(key, user, 'compras/pagar', {'order': order.slug, 'valor': str(self.validated_data['valor'])})
        with transaction.atomic():
            FinanceiroService.registrar_pagamento_compra(order, self.validated_data['valor'])
            order.valor_pago = (order.valor_pago or 0) + self.validated_data['valor']
            order.pago_em = djtz.now()
            if order.valor_pago >= order.total:
                order.status = PurchaseOrder.Status.QUITADO
            order.save(update_fields=['valor_pago', 'pago_em', 'status'])
        log_action(user, 'pay', 'PurchaseOrder', order.slug, {'valor': str(self.validated_data['valor'])})
        return order
