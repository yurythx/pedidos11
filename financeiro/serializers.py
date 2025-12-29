from rest_framework import serializers
from .models import LedgerEntry, Account, CostCenter, UserDefaultCostCenter


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
