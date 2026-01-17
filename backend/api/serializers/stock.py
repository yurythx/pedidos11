"""
Serializers para módulo Stock (Estoque).
"""
from rest_framework import serializers
from stock.models import Deposito, Saldo, Movimentacao, Lote


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


class LoteSerializer(serializers.ModelSerializer):
    """Serializer para Lote (controle de validade)."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_sku = serializers.CharField(source='produto.sku', read_only=True)
    deposito_nome = serializers.CharField(source='deposito.nome', read_only=True)
    
    # Propriedades calculadas
    dias_ate_vencer = serializers.IntegerField(read_only=True)
    status_validade = serializers.CharField(read_only=True)
    percentual_consumido = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Lote
        fields = [
            'id', 'produto', 'produto_nome', 'produto_sku',
            'deposito', 'deposito_nome',
            'codigo_lote', 'data_fabricacao', 'data_validade',
            'quantidade_atual', 'observacao',
            'dias_ate_vencer', 'status_validade', 'percentual_consumido',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'quantidade_atual', 'created_at', 'updated_at']


class LoteListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de lotes."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    deposito_nome = serializers.CharField(source='deposito.nome', read_only=True)
    dias_ate_vencer = serializers.IntegerField(read_only=True)
    status_validade = serializers.CharField(read_only=True)
    
    class Meta:
        model = Lote
        fields = [
            'id', 'codigo_lote', 'produto_nome', 'deposito_nome',
            'data_validade', 'quantidade_atual',
            'dias_ate_vencer', 'status_validade'
        ]


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
    lote_codigo = serializers.CharField(source='lote.codigo_lote', read_only=True, allow_null=True)
    valor_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Movimentacao
        fields = [
            'id', 'produto', 'produto_nome',
            'deposito', 'deposito_nome',
            'lote', 'lote_codigo',
            'tipo', 'quantidade', 'valor_unitario', 'valor_total',
            'documento', 'observacao', 'usuario',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
