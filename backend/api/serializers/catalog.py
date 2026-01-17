"""
Serializers para módulo Catalog (Produtos e Categorias).
"""
from rest_framework import serializers
from catalog.models import Categoria, Produto, FichaTecnicaItem
from decimal import Decimal


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para Categoria."""
    
    parent_nome = serializers.CharField(source='parent.nome', read_only=True)
    caminho_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Categoria
        fields = [
            'id', 'nome', 'slug', 'parent', 'parent_nome',
            'descricao', 'ordem', 'caminho_completo',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class FichaTecnicaItemSerializer(serializers.ModelSerializer):
    """Serializer para Item da Ficha Técnica."""
    
    componente_nome = serializers.CharField(source='componente.nome', read_only=True)
    componente_sku = serializers.CharField(source='componente.sku', read_only=True)
    custo_calculado = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    percentual_composicao = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = FichaTecnicaItem
        fields = [
            'id', 'produto_pai', 'componente', 'componente_nome', 'componente_sku',
            'quantidade_liquida', 'custo_fixo', 'custo_calculado',
            'percentual_composicao', 'observacao',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validações customizadas."""
        if 'produto_pai' in data and 'componente' in data:
            if data['produto_pai'] == data['componente']:
                raise serializers.ValidationError({
                    'componente': 'Um produto não pode ser componente dele mesmo.'
                })
        return data


class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de produtos."""
    
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'sku', 'codigo_barras',
            'categoria', 'categoria_nome', 'tipo', 'tipo_display',
            'preco_venda', 'preco_custo',
            'destaque', 'is_active'
        ]


class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do produto."""
    
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    margem_lucro = serializers.ReadOnlyField()
    lucro_unitario = serializers.ReadOnlyField()
    
    # Nested ficha técnica (somente para produtos COMPOSTO)
    ficha_tecnica = FichaTecnicaItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'slug', 'sku', 'codigo_barras',
            'categoria', 'categoria_nome', 'tipo', 'tipo_display',
            'preco_venda', 'preco_custo', 
            'margem_lucro', 'lucro_unitario',
            'descricao', 'descricao_curta',
            'permite_venda_sem_estoque', 'destaque',
            'ficha_tecnica',  # Ficha técnica nested
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criar/editar produtos."""
    
    class Meta:
        model = Produto
        fields = [
            'nome', 'sku', 'codigo_barras', 'categoria', 'tipo',
            'preco_venda', 'preco_custo', 'descricao', 'descricao_curta',
            'permite_venda_sem_estoque', 'destaque'
        ]
