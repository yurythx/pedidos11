from rest_framework import serializers
from vendas.models import Produto
from .models import StockMovement, StockReceipt, StockReceiptItem, Deposito, MotivoAjuste
from cadastro.models import Supplier


class StockMovementSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    deposito = serializers.SlugRelatedField(slug_field='slug', queryset=Deposito.objects.all(), required=False, allow_null=True)
    motivo_ajuste = serializers.SlugRelatedField(slug_field='codigo', queryset=MotivoAjuste.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StockMovement
        fields = ['produto', 'tipo', 'quantidade', 'origem_slug', 'pedido', 'responsavel', 'observacao', 'deposito', 'motivo_ajuste', 'criado_em']
        read_only_fields = ['criado_em', 'pedido', 'responsavel']


class StockReceiptItemSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_slug = serializers.CharField(source='produto.slug', read_only=True)

    class Meta:
        model = StockReceiptItem
        fields = ['produto', 'produto_nome', 'produto_slug', 'quantidade', 'custo_unitario', 'criado_em']
        read_only_fields = ['criado_em', 'produto_nome', 'produto_slug']


class StockReceiptSerializer(serializers.ModelSerializer):
    fornecedor = serializers.SlugRelatedField(source='fornecedor_ref', slug_field='slug', queryset=Supplier.objects.all(), required=False, allow_null=True)
    itens = StockReceiptItemSerializer(many=True, read_only=True)
    itens_payload = StockReceiptItemSerializer(many=True, write_only=True)
    deposito = serializers.SlugRelatedField(slug_field='slug', queryset=Deposito.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StockReceipt
        fields = ['id', 'fornecedor', 'documento', 'observacao', 'responsavel', 'deposito', 'criado_em', 'estornado_em', 'itens', 'itens_payload']
        read_only_fields = ['id', 'responsavel', 'criado_em', 'estornado_em', 'itens']

    def create(self, validated_data):
        itens_payload = validated_data.pop('itens_payload', [])
        user = self.context['request'].user if 'request' in self.context else None
        recibo = StockReceipt.objects.create(responsavel=user, **validated_data)
        for item in itens_payload:
            produto = item['produto']
            quantidade = int(item['quantidade'])
            custo_unitario = item.get('custo_unitario')
            StockReceiptItem.objects.create(
                recebimento=recibo,
                produto=produto,
                quantidade=quantidade,
                custo_unitario=custo_unitario,
            )
            from .services import EstoqueService
            EstoqueService.registrar_entrada(produto=produto, quantidade=quantidade, origem_slug=recibo.documento or str(recibo.id), responsavel=user, observacao='recebimento', deposito=recibo.deposito)
            if custo_unitario is not None:
                produto.custo = custo_unitario
                produto.save(update_fields=['custo'])
        return recibo
