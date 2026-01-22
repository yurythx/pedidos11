from rest_framework import serializers
from catalog.models import Categoria, Produto, Complemento, GrupoComplemento
from tenant.models import Empresa
from locations.models import Endereco

class PublicEnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['logradouro', 'numero', 'bairro', 'cidade', 'uf', 'cep']

class PublicEmpresaSerializer(serializers.ModelSerializer):
    """Serializer público para dados da empresa."""
    endereco_principal = PublicEnderecoSerializer(read_only=True)
    
    class Meta:
        model = Empresa
        fields = [
            'nome_fantasia', 'slug', 'logo', 
            'cor_primaria', 'cor_secundaria', 
            'telefone', 'endereco_principal', 
            'website', 'email'
        ]

class PublicComplementoSerializer(serializers.ModelSerializer):
    """Serializer público para opções de complemento."""
    class Meta:
        model = Complemento
        fields = ['id', 'nome', 'preco_adicional']

class PublicGrupoComplementoSerializer(serializers.ModelSerializer):
    """Serializer público para grupos de complementos."""
    complementos = PublicComplementoSerializer(many=True, read_only=True)
    
    class Meta:
        model = GrupoComplemento
        fields = ['id', 'nome', 'obrigatorio', 'min_qtd', 'max_qtd', 'complementos']

class PublicProdutoSerializer(serializers.ModelSerializer):
    """Serializer público para produtos."""
    grupos_complementos = PublicGrupoComplementoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'descricao_curta',
            'preco_venda', 'imagem', 'destaque',
            'grupos_complementos'
        ]

class PublicCategoriaSerializer(serializers.ModelSerializer):
    """Serializer público para categorias com seus produtos."""
    produtos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'ordem', 'produtos']

    def get_produtos(self, obj):
        # Filtra apenas produtos ativos e que não são insumos
        produtos = obj.produtos.filter(is_active=True, tipo__in=['FINAL', 'COMPOSTO']).order_by('nome')
        return PublicProdutoSerializer(produtos, many=True).data
