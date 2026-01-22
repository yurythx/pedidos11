from rest_framework import serializers
from .models import Empresa

class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer para gestão da Empresa (Configurações)."""
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj',
            'inscricao_estadual', 'inscricao_municipal',
            'ambiente_nfe', 'regime_tributario',
            'certificado_digital', 'senha_certificado',
            'serie_nfe', 'numero_nfe_atual'
        ]
        read_only_fields = ['id', 'cnpj'] # CNPJ geralmente não muda
        extra_kwargs = {
            'senha_certificado': {'write_only': True}
        }
