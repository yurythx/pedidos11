from rest_framework import serializers
from .models import LedgerEntry, Account, CostCenter, UserDefaultCostCenter, Title, TitleParcel
from vendas.models import Pedido
from compras.models import PurchaseOrder


class LedgerEntrySerializer(serializers.ModelSerializer):
    debit_account_ref = serializers.SlugRelatedField(slug_field='codigo', queryset=Account.objects.all(), required=False, allow_null=True)
    credit_account_ref = serializers.SlugRelatedField(slug_field='codigo', queryset=Account.objects.all(), required=False, allow_null=True)
    cost_center = serializers.SlugRelatedField(slug_field='codigo', queryset=CostCenter.objects.all(), required=False, allow_null=True)
    class Meta:
        model = LedgerEntry
        fields = ['pedido', 'descricao', 'debit_account', 'credit_account', 'debit_account_ref', 'credit_account_ref', 'cost_center', 'valor', 'criado_em', 'usuario']
        read_only_fields = ['criado_em']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['codigo', 'nome', 'tipo']


class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = ['codigo', 'nome']


class UserDefaultCostCenterSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    cost_center_codigo = serializers.CharField(source='cost_center.codigo', read_only=True)
    class Meta:
        model = UserDefaultCostCenter
        fields = ['id', 'user', 'user_username', 'cost_center', 'cost_center_codigo']


class TitleSerializer(serializers.ModelSerializer):
    pedido = serializers.SlugRelatedField(slug_field='slug', queryset=Pedido.objects.all(), required=False, allow_null=True)
    compra = serializers.SlugRelatedField(slug_field='slug', queryset=PurchaseOrder.objects.all(), required=False, allow_null=True)
    cost_center = serializers.SlugRelatedField(slug_field='codigo', queryset=CostCenter.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Title
        fields = ['id', 'tipo', 'pedido', 'compra', 'descricao', 'valor', 'valor_pago', 'due_date', 'status', 'criado_em', 'usuario', 'cost_center']
        read_only_fields = ['id', 'valor_pago', 'status', 'criado_em', 'usuario']
    def validate(self, attrs):
        tipo = attrs.get('tipo')
        pedido = attrs.get('pedido')
        compra = attrs.get('compra')
        if tipo == Title.Tipo.AR and not pedido:
            raise serializers.ValidationError("Título AR requer pedido.")
        if tipo == Title.Tipo.AP and not compra:
            raise serializers.ValidationError("Título AP requer compra.")
        if attrs.get('valor') <= 0:
            raise serializers.ValidationError("Valor deve ser > 0.")
        return attrs
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user and request.user.is_authenticated else None
        t = Title.objects.create(usuario=user, **validated_data)
        if not t.cost_center:
            if t.pedido and t.pedido.cost_center:
                t.cost_center = t.pedido.cost_center
            if t.compra and t.compra.cost_center and not t.cost_center:
                t.cost_center = t.compra.cost_center
            t.save(update_fields=['cost_center'])
        return t


class TitleParcelSerializer(serializers.ModelSerializer):
    title = serializers.PrimaryKeyRelatedField(queryset=Title.objects.all())
    class Meta:
        model = TitleParcel
        fields = ['id', 'title', 'valor', 'valor_pago', 'due_date', 'status', 'criado_em']
        read_only_fields = ['id', 'valor_pago', 'status', 'criado_em']
    def validate(self, attrs):
        if attrs.get('valor') <= 0:
            raise serializers.ValidationError("Valor deve ser > 0.")
        return attrs
    def create(self, validated_data):
        p = TitleParcel.objects.create(**validated_data)
        t = p.title
        t.valor = (t.valor or 0) + p.valor
        t.save(update_fields=['valor'])
        return p
