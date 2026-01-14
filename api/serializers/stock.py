"""
Serializers para módulo Stock (Estoque).
"""
from rest_framework import serializers
from stock.models import Deposito, Saldo, Movimentacao


class DepositoSerializer(serializers.ModelSerializer):
    """Serializer para Deposito."""
    
    class Meta:
        model = Deposito
        fields = [
            'id', 'nome', 'slug', 'codigo',
            'is_padrao', 'is_virtual', 'descricao',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class SaldoSerializer(serializers.ModelSerializer):
    """Serializer para Saldo (read-only)."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_sku = serializers.CharField(source='produto.sku', read_only=True)
    deposito_nome = serializers.CharField(source='deposito.nome', read_only=True)
    disponivel = serializers.ReadOnlyField()
    
    class Meta:
        model = Saldo
        fields = [
            'id', 'produto', 'produto_nome', 'produto_sku',
            'deposito', 'deposito_nome',
            'quantidade', 'disponivel',
            'updated_at'
        ]
        read_only_fields = ['id', 'quantidade', 'updated_at']


class MovimentacaoSerializer(serializers.ModelSerializer):
    """Serializer para Movimentacao."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    deposito_nome = serializers.CharField(source='deposito.nome', read_only=True)
    valor_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Movimentacao
        fields = [
            'id', 'produto', 'produto_nome',
            'deposito', 'deposito_nome',
            'tipo', 'quantidade', 'valor_unitario', 'valor_total',
            'documento', 'observacao', 'usuario',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
