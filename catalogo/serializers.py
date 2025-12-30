from decimal import Decimal
from rest_framework import serializers
from .models import Categoria, Produto, ProdutoImagem, ProdutoAtributo, ProdutoAtributoValor, ProdutoVariacao


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nome', 'slug']
        read_only_fields = ['slug']


class ProdutoSerializer(serializers.ModelSerializer):
    categoria = serializers.SlugRelatedField(slug_field='slug', queryset=Categoria.objects.all())
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    sku = serializers.CharField(required=False, allow_blank=True)
    ean = serializers.CharField(required=False, allow_blank=True)
    unidade = serializers.ChoiceField(choices=[('UN','Unidade'),('CX','Caixa'),('KG','Kilograma'),('LT','Litro')], required=False)
    marca = serializers.CharField(required=False, allow_blank=True)
    ncm = serializers.CharField(required=False, allow_blank=True)
    cfop = serializers.CharField(required=False, allow_blank=True)
    atributos = serializers.JSONField(required=False)

    class Meta:
        model = Produto
        fields = ['nome', 'slug', 'sku', 'ean', 'unidade', 'marca', 'ncm', 'cfop', 'atributos', 'categoria', 'categoria_nome', 'preco', 'custo', 'descricao', 'imagem', 'disponivel']
        read_only_fields = ['slug']

    def validate_preco(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("Preço não pode ser negativo.")
        return value

    def validate_custo(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("Custo não pode ser negativo.")
        return value

    def validate_ean(self, value: str) -> str:
        if value and not value.isdigit():
            raise serializers.ValidationError("EAN deve conter apenas dígitos.")
        if value and not (8 <= len(value) <= 14):
            raise serializers.ValidationError("EAN deve ter entre 8 e 14 dígitos.")
        return value

    def validate_ncm(self, value: str) -> str:
        if value and (not value.isdigit() or len(value) != 8):
            raise serializers.ValidationError("NCM deve ter 8 dígitos numéricos.")
        return value

    def validate_cfop(self, value: str) -> str:
        if value and (not value.isdigit() or len(value) != 4):
            raise serializers.ValidationError("CFOP deve ter 4 dígitos numéricos.")
        return value


class ProdutoImagemSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    class Meta:
        model = ProdutoImagem
        fields = ['id', 'produto', 'imagem', 'alt', 'pos', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class ProdutoAtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoAtributo
        fields = ['id', 'codigo', 'nome', 'tipo', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class ProdutoAtributoValorSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    atributo = serializers.SlugRelatedField(slug_field='codigo', queryset=ProdutoAtributo.objects.all())
    class Meta:
        model = ProdutoAtributoValor
        fields = ['id', 'produto', 'atributo', 'valor_texto', 'valor_numero', 'valor_bool', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    class Meta:
        model = ProdutoVariacao
        fields = ['id', 'produto', 'sku', 'nome', 'preco', 'custo', 'disponivel', 'atributos', 'imagem', 'criado_em']
        read_only_fields = ['id', 'criado_em']
