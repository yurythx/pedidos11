from rest_framework import serializers
from .models import Address, Supplier, Customer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'pais', 'referencia', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class SupplierSerializer(serializers.ModelSerializer):
    enderecos = AddressSerializer(many=True, read_only=True)
    enderecos_payload = AddressSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Supplier
        fields = ['nome', 'slug', 'email', 'telefone', 'documento', 'enderecos', 'enderecos_payload', 'criado_em']
        read_only_fields = ['slug', 'criado_em', 'enderecos']

    def create(self, validated_data):
        enderecos_payload = validated_data.pop('enderecos_payload', [])
        supplier = Supplier.objects.create(**validated_data)
        for addr in enderecos_payload:
            address = Address.objects.create(**addr)
            supplier.enderecos.add(address)
        return supplier


class CustomerSerializer(serializers.ModelSerializer):
    enderecos = AddressSerializer(many=True, read_only=True)
    enderecos_payload = AddressSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Customer
        fields = ['nome', 'slug', 'email', 'telefone', 'documento', 'user', 'enderecos', 'enderecos_payload', 'criado_em']
        read_only_fields = ['slug', 'enderecos', 'criado_em']

    def create(self, validated_data):
        enderecos_payload = validated_data.pop('enderecos_payload', [])
        cliente = Customer.objects.create(**validated_data)
        for addr in enderecos_payload:
            address = Address.objects.create(**addr)
            cliente.enderecos.add(address)
        return cliente
