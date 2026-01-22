"""
Serializers para módulo Financial (Financeiro).
"""
from rest_framework import serializers
from financial.models import ContaReceber, ContaPagar, Caixa, SessaoCaixa, MovimentoCaixa


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


class CaixaSerializer(serializers.ModelSerializer):
    """Serializer para Caixa."""
    
    class Meta:
        model = Caixa
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MovimentoCaixaSerializer(serializers.ModelSerializer):
    """Serializer para Movimento de Caixa."""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = MovimentoCaixa
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'data_hora']


class SessaoCaixaSerializer(serializers.ModelSerializer):
    """Serializer para Sessão de Caixa (Abertura/Fechamento)."""
    
    operador_nome = serializers.CharField(source='operador.username', read_only=True)
    caixa_nome = serializers.CharField(source='caixa.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    diferenca_caixa = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    # Não incluir movimentos por padrão para não pesar na listagem
    # movimentos = MovimentoCaixaSerializer(many=True, read_only=True)
    
    class Meta:
        model = SessaoCaixa
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'data_abertura', 'data_fechamento', 'saldo_final_calculado', 'status']
