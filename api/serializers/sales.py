"""
Serializers para módulo Sales (Vendas).
"""
from rest_framework import serializers
from django.db import transaction
from sales.models import Venda, ItemVenda, ItemVendaComplemento


class ItemVendaComplementoSerializer(serializers.ModelSerializer):
    """Serializer para ItemVendaComplemento."""
    
    complemento_nome = serializers.CharField(source='complemento.nome', read_only=True)
    possui_produto_vinculado = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemVendaComplemento
        fields = [
            'id', 'complemento', 'complemento_nome',
            'quantidade', 'preco_unitario', 'subtotal',
            'possui_produto_vinculado'
        ]
        read_only_fields = ['id', 'subtotal']


class ItemVendaSerializer(serializers.ModelSerializer):
    """Serializer para ItemVenda com nested write de complementos."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    total_sem_desconto = serializers.ReadOnlyField()
    percentual_desconto = serializers.ReadOnlyField()
    total_complementos = serializers.ReadOnlyField()
    
    # Nested serializer com write support
    complementos = ItemVendaComplementoSerializer(many=True, required=False)
    
    class Meta:
        model = ItemVenda
        fields = [
            'id', 'produto', 'produto_nome',
            'quantidade', 'preco_unitario', 'desconto',
            'subtotal', 'total_sem_desconto', 'percentual_desconto',
            'total_complementos', 'observacoes', 'complementos'
        ]
        read_only_fields = ['id', 'subtotal']
    
    @transaction.atomic
    def create(self, validated_data):
        """Cria item com seus complementos em uma transação atômica."""
        # Extra nested data
        complementos_data = validated_data.pop('complementos', [])
        
        # Cria item
        item = ItemVenda.objects.create(**validated_data)
        
        # Cria complementos
        for comp_data in complementos_data:
            ItemVendaComplemento.objects.create(
                item_pai=item,
                empresa=item.empresa,
                **comp_data
            )
        
        return item
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Atualiza item e seus complementos."""
        # Extra nested data
        complementos_data = validated_data.pop('complementos', None)
        
        # Atualiza item
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Se complementos foram fornecidos, substitui todos
        if complementos_data is not None:
            # Remove complementos antigos
            instance.complementos.all().delete()
            
            # Cria novos
            for comp_data in complementos_data:
                ItemVendaComplemento.objects.create(
                    item_pai=instance,
                    empresa=instance.empresa,
                    **comp_data
                )
        
        return instance


class VendaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de vendas."""
    
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, allow_null=True)
    vendedor_nome = serializers.CharField(source='vendedor.get_full_name', read_only=True)
    quantidade_itens = serializers.ReadOnlyField()
    
    class Meta:
        model = Venda
        fields = [
            'id', 'numero', 'slug', 'cliente', 'cliente_nome',
            'vendedor', 'vendedor_nome', 'status',
            'total_liquido', 'quantidade_itens',
            'data_emissao', 'data_finalizacao'
        ]


class VendaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes da venda."""
    
    itens = ItemVendaSerializer(many=True, read_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, allow_null=True)
    vendedor_nome = serializers.CharField(source='vendedor.get_full_name', read_only=True)
    pode_ser_finalizada = serializers.ReadOnlyField()
    pode_ser_cancelada = serializers.ReadOnlyField()
    quantidade_itens = serializers.ReadOnlyField()
    
    class Meta:
        model = Venda
        fields = [
            'id', 'numero', 'slug', 'cliente', 'cliente_nome',
            'vendedor', 'vendedor_nome', 'status',
            'total_bruto', 'total_desconto', 'total_liquido',
            'tipo_pagamento', 'observacoes',
            'data_emissao', 'data_finalizacao', 'data_cancelamento',
            'itens', 'quantidade_itens',
            'pode_ser_finalizada', 'pode_ser_cancelada',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'numero', 'slug', 'total_bruto', 'total_desconto', 'total_liquido',
            'data_finalizacao', 'data_cancelamento', 'created_at', 'updated_at'
        ]


class VendaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar vendas."""
    
    class Meta:
        model = Venda
        fields = ['cliente', 'vendedor', 'tipo_pagamento', 'observacoes']
