"""
Serializers para módulo Catalog (Produtos e Categorias).
"""
from rest_framework import serializers
from catalog.models import Categoria, Produto


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


class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de produtos."""
    
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'sku', 'codigo_barras',
            'categoria', 'categoria_nome', 'tipo',
            'preco_venda', 'preco_custo',
            'destaque', 'is_active'
        ]


class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do produto."""
    
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    margem_lucro = serializers.ReadOnlyField()
    lucro_unitario = serializers.ReadOnlyField()
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'slug', 'sku', 'codigo_barras',
            'categoria', 'categoria_nome', 'tipo',
            'preco_venda', 'preco_custo', 
            'margem_lucro', 'lucro_unitario',
            'descricao', 'descricao_curta',
            'permite_venda_sem_estoque', 'destaque',
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
