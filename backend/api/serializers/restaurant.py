"""
Serializers para módulo Restaurant (Food Service).
"""
from rest_framework import serializers
from restaurant.models import SetorImpressao, Mesa, Comanda


class SetorImpressaoSerializer(serializers.ModelSerializer):
    """Serializer para SetorImpressao."""
    
    class Meta:
        model = SetorImpressao
        fields = [
            'id', 'nome', 'slug', 'ordem', 'cor',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class MesaSerializer(serializers.ModelSerializer):
    """Serializer para Mesa com resumo da conta."""
    
    venda_numero = serializers.IntegerField(source='venda_atual.numero', read_only=True, allow_null=True)
    total_conta = serializers.SerializerMethodField()
    esta_livre = serializers.ReadOnlyField()
    esta_ocupada = serializers.ReadOnlyField()
    
    class Meta:
        model = Mesa
        fields = [
            'id', 'numero', 'capacidade', 'status',
            'venda_atual', 'venda_numero', 'total_conta',
            'observacoes', 'esta_livre', 'esta_ocupada',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_conta(self, obj):
        """Retorna total da venda atual da mesa."""
        if obj.venda_atual:
            return str(obj.venda_atual.total_liquido)
        return '0.00'


class ComandaSerializer(serializers.ModelSerializer):
    """Serializer para Comanda com resumo da conta."""
    
    venda_numero = serializers.IntegerField(source='venda_atual.numero', read_only=True, allow_null=True)
    total_conta = serializers.SerializerMethodField()
    esta_livre = serializers.ReadOnlyField()
    esta_em_uso = serializers.ReadOnlyField()
    
    class Meta:
        model = Comanda
        fields = [
            'id', 'codigo', 'status',
            'venda_atual', 'venda_numero', 'total_conta',
            'observacoes',
            'esta_livre', 'esta_em_uso',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_conta(self, obj):
        """Retorna total da venda atual da comanda."""
        if obj.venda_atual:
            return str(obj.venda_atual.total_liquido)
        return '0.00'
