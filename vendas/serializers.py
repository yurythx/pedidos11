"""Serializers de Vendas (DRF).

Inclui validações de produto, atributos e criação de pedidos com:
- idempotência de criação;
- cálculo de total e verificação de estoque;
- associação de centro de custo (explícito ou default do usuário);
- integração financeira: receita à vista, venda a prazo com parcelas e COGS;
- validação de parcelas (soma = total e due_date ISO).
"""
from decimal import Decimal
from typing import List, Dict
from django.db import transaction
from rest_framework import serializers
from .models import Pedido, ItemPedido
from .services import PedidoService
from estoque.services import EstoqueService
from financeiro.services import FinanceiroService
from financeiro.models import CostCenter, UserDefaultCostCenter
from auditoria.utils import log_action, ensure_idempotency, payload_hash
from django.utils import timezone


class ItemPedidoReadSerializer(serializers.ModelSerializer):
    """Serializa itens do pedido para leitura."""
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_slug = serializers.CharField(source='produto.slug', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['produto_nome', 'produto_slug', 'quantidade', 'preco_unitario']


class PedidoSerializer(serializers.ModelSerializer):
    """Serializa pedidos e processa criação com integrações de estoque e financeiro."""
    itens = ItemPedidoReadSerializer(many=True, read_only=True)
    cost_center = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cost_center_codigo = serializers.CharField(source='cost_center.codigo', read_only=True)
    cost_center_nome = serializers.CharField(source='cost_center.nome', read_only=True)
    payment_type = serializers.ChoiceField(choices=[('AVISTA','À vista'),('PRAZO','A prazo')], write_only=True, required=False)
    parcelas = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    # payload de criação: [{"produto": <slug>, "quantidade": <int>}, ...]
    itens_payload = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Pedido
        fields = ['slug', 'usuario', 'status', 'total', 'data_criacao', 'itens', 'itens_payload', 'cost_center', 'cost_center_codigo', 'cost_center_nome', 'payment_type', 'parcelas']
        read_only_fields = ['slug', 'usuario', 'total', 'data_criacao', 'status']

    def validate_itens_payload(self, value: List[Dict]) -> List[Dict]:
        """Valida e normaliza itens do payload de criação."""
        if not value:
            raise serializers.ValidationError("Itens do pedido são obrigatórios.")
        normalized = []
        seen = set()
        for item in value:
            produto_slug = item.get('produto')
            quantidade = item.get('quantidade')
            if not produto_slug or not isinstance(quantidade, int) or quantidade <= 0:
                raise serializers.ValidationError("Cada item deve conter 'produto' (slug) e 'quantidade' (>0).")
            if produto_slug in seen:
                raise serializers.ValidationError("Itens duplicados para o mesmo produto não são permitidos.")
            seen.add(produto_slug)
            normalized.append({'produto': produto_slug, 'quantidade': quantidade})
        PedidoService.validate_disponibilidade(normalized)
        return normalized

    def create(self, validated_data):
        """Cria pedido com idempotência, movimenta estoque e registra lançamentos financeiros.

        - Valida usuário, itens e centro de custo/default;
        - Calcula total e valida parcelas (se a prazo);
        - Registra saída de estoque e razão: AR/AP/receita e COGS;
        - Retorna pedido criado.
        """
        request = self.context.get('request')
        usuario = request.user if request and request.user and request.user.is_authenticated else None
        if not usuario:
            raise serializers.ValidationError("Usuário não autenticado.")

        itens_payload = validated_data.pop('itens_payload')
        cost_center_code = validated_data.pop('cost_center', None)
        payment_type = validated_data.pop('payment_type', 'AVISTA')
        key = request.headers.get('Idempotency-Key') if request else None
        idem, created = ensure_idempotency(key, usuario, 'pedido/create', {'itens': itens_payload, 'cost_center': cost_center_code})
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            last = Pedido.objects.filter(usuario=usuario, data_criacao__gte=since).order_by('-data_criacao').first()
            if last:
                items = list(ItemPedido.objects.filter(pedido=last).values_list('produto__slug', 'quantidade'))
                expected = sorted([(i['produto'], i['quantidade']) for i in itens_payload])
                if sorted(items) == expected:
                    return last

        with transaction.atomic():
            EstoqueService.verificar_disponibilidade(itens_payload)
            pedido = Pedido.objects.create(usuario=usuario)
            itens_objs: List[ItemPedido] = PedidoService.criar_itens(pedido, itens_payload)
            total = PedidoService.calcular_total(itens_objs)
            parcelas = validated_data.get('parcelas', None)
            if payment_type == 'PRAZO' and parcelas:
                from decimal import Decimal as D
                import datetime
                soma = sum(D(str(p.get('valor'))) for p in parcelas)
                try:
                    for p in parcelas:
                        datetime.date.fromisoformat(p.get('due_date'))
                except Exception:
                    raise serializers.ValidationError("due_date inválida em parcelas.")
                if soma != total:
                    raise serializers.ValidationError("Soma das parcelas difere do total do pedido.")
            pedido.total = total
            if cost_center_code:
                cc = CostCenter.objects.filter(codigo=cost_center_code).first()
                if not cc:
                    raise serializers.ValidationError("Centro de custo inválido.")
                pedido.cost_center = cc
            else:
                mapping = UserDefaultCostCenter.objects.filter(user=usuario).first()
                if mapping:
                    pedido.cost_center = mapping.cost_center
            pedido.save(update_fields=['total', 'cost_center'] if cost_center_code else ['total'])
            EstoqueService.registrar_saida(pedido, itens_objs)
            if payment_type == 'PRAZO':
                FinanceiroService.registrar_venda_a_prazo(pedido, cost_center_code=cost_center_code, parcelas=parcelas)
            else:
                FinanceiroService.registrar_receita_venda(pedido, cost_center_code=cost_center_code)
            FinanceiroService.registrar_custo_venda(pedido, cost_center_code=cost_center_code)
            log_action(usuario, 'create', 'Pedido', pedido.slug, {'total': str(total), 'itens_count': len(itens_objs), 'cost_center': pedido.cost_center.codigo if pedido.cost_center else None})
        return pedido
