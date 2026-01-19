"""
Serializers para NFe - Projeto Nix.
"""
from rest_framework import serializers
from .models import ProdutoFornecedor


class UploadXMLSerializer(serializers.Serializer):
    """Serializer para upload de arquivo XML de NFe."""
    
    arquivo = serializers.FileField(
        help_text='Arquivo XML da NFe'
    )
    
    def validate_arquivo(self, value):
        """Valida arquivo XML."""
        # Validar extensão
        if not value.name.lower().endswith('.xml'):
            raise serializers.ValidationError(
                "Arquivo deve ter extensão .xml"
            )
        
        # Validar tamanho (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Arquivo muito grande. Máximo: 5MB, Recebido: {value.size / 1024 / 1024:.1f}MB"
            )
        
        # Validar que não está vazio
        if value.size == 0:
            raise serializers.ValidationError(
                "Arquivo vazio"
            )
        
        return value


class ProdutoFornecedorSerializer(serializers.ModelSerializer):
    """Serializer para vínculos produto-fornecedor."""
    
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    preco_unitario_convertido = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = ProdutoFornecedor
        fields = [
            'id', 'produto', 'produto_nome', 'cnpj_fornecedor',
            'nome_fornecedor', 'codigo_no_fornecedor', 'fator_conversao',
            'ultimo_preco', 'preco_unitario_convertido',
            'data_ultima_compra', 'observacao', 'created_at'
        ]
        read_only_fields = ['id', 'data_ultima_compra', 'created_at']


class ItemNFeSerializer(serializers.Serializer):
    """Serializer para item da NFe no payload de confirmação."""
    
    codigo_xml = serializers.CharField(max_length=50)
    produto_id = serializers.UUIDField()
    fator_conversao = serializers.DecimalField(max_digits=10, decimal_places=4, default=1)
    qtd_xml = serializers.DecimalField(max_digits=10, decimal_places=4)
    preco_custo = serializers.DecimalField(max_digits=10, decimal_places=2)
    lote = serializers.DictField(required=False, allow_null=True)


class FornecedorNFeSerializer(serializers.Serializer):
    """Serializer para dados do fornecedor."""
    
    cnpj = serializers.CharField(max_length=20)
    nome = serializers.CharField(max_length=200)


class ConfirmarImportacaoNFeSerializer(serializers.Serializer):
    """Serializer para payload de confirmação de importação."""
    
    deposito_id = serializers.UUIDField()
    numero_nfe = serializers.CharField(max_length=20, required=False, allow_null=True)
    serie_nfe = serializers.CharField(max_length=5, default='1')
    fornecedor = FornecedorNFeSerializer()
    itens = ItemNFeSerializer(many=True)
    
    def validate_itens(self, value):
        """Valida que há pelo menos 1 item."""
        if not value:
            raise serializers.ValidationError("Deve haver pelo menos 1 item para importar")
        return value
