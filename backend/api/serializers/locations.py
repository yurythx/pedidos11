from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from locations.models import Endereco, TipoEndereco, UF


class EnderecoSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.UUIDField()
    tipo = serializers.ChoiceField(choices=TipoEndereco.choices)
    uf = serializers.ChoiceField(choices=UF.choices)

    class Meta:
        model = Endereco
        fields = [
            'id', 'content_type', 'object_id', 'tipo',
            'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'uf',
            'latitude', 'longitude', 'referencia',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_content_type(self, value):
        try:
            app_label, model = value.split('.', 1)
            app_label = app_label.lower()
            model = model.lower()
            ct = ContentType.objects.get(app_label=app_label, model=model)
            return f'{ct.app_label}.{ct.model}'
        except Exception:
            raise serializers.ValidationError('content_type deve ser no formato app_label.model')

    def create(self, validated_data):
        ct_str = validated_data.pop('content_type')
        app_label, model = ct_str.split('.', 1)
        ct = ContentType.objects.get(app_label=app_label, model=model)
        empresa = self.context['request'].user.empresa
        return Endereco.objects.create(
            empresa=empresa,
            content_type=ct,
            **validated_data
        )

    def update(self, instance, validated_data):
        validated_data.pop('content_type', None)
        return super().update(instance, validated_data)

