"""
Serializers para módulo Financial (Financeiro).
"""
from rest_framework import serializers
from financial.models import ContaReceber, ContaPagar


class ContaReceberSerializer(serializers.ModelSerializer):
    """Serializer para ContaReceber."""
    
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, allow_null=True)
    venda_numero = serializers.IntegerField(source='venda.numero', read_only=True, allow_null=True)
    valor_total = serializers.ReadOnlyField()
    esta_vencida = serializers.ReadOnlyField()
    dias_atraso = serializers.ReadOnlyField()
    
    class Meta:
        model = ContaReceber
        fields = [
            'id', 'venda', 'venda_numero', 'cliente', 'cliente_nome',
            'descricao', 'valor_original', 'valor_juros', 'valor_multa',
            'valor_desconto', 'valor_total',
            'data_emissao', 'data_vencimento', 'data_pagamento',
            'status', 'tipo_pagamento', 'observacoes',
            'esta_vencida', 'dias_atraso',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContaPagarSerializer(serializers.ModelSerializer):
    """Serializer para ContaPagar."""
    
    fornecedor_nome = serializers.CharField(source='fornecedor.nome_exibicao', read_only=True, allow_null=True)
    valor_total = serializers.ReadOnlyField()
    esta_vencida = serializers.ReadOnlyField()
    dias_atraso = serializers.ReadOnlyField()
    
    class Meta:
        model = ContaPagar
        fields = [
            'id', 'fornecedor', 'fornecedor_nome',
            'descricao', 'categoria', 'numero_documento',
            'valor_original', 'valor_juros', 'valor_multa',
            'valor_desconto', 'valor_total',
            'data_emissao', 'data_vencimento', 'data_pagamento',
            'status', 'tipo_pagamento', 'observacoes',
            'esta_vencida', 'dias_atraso',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
