"""
Serializers para módulo Partners (Clientes e Fornecedores).
"""
from rest_framework import serializers
from partners.models import Cliente, Fornecedor, Colaborador


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para Cliente."""
    
    documento_numerico = serializers.ReadOnlyField()
    is_pessoa_fisica = serializers.ReadOnlyField()
    is_pessoa_juridica = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_pessoa', 'nome', 'nome_fantasia', 'slug',
            'cpf_cnpj', 'documento_numerico',
            'rg_ie', 'email', 'telefone', 'celular',
            'observacoes',
            'is_pessoa_fisica', 'is_pessoa_juridica',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tipo_pessoa', 'slug', 'created_at', 'updated_at']


class FornecedorSerializer(serializers.ModelSerializer):
    """Serializer para Fornecedor."""
    
    documento_numerico = serializers.ReadOnlyField()
    nome_exibicao = serializers.ReadOnlyField()
    
    class Meta:
        model = Fornecedor
        fields = [
            'id', 'tipo_pessoa', 'razao_social', 'nome_fantasia', 'slug',
            'cpf_cnpj', 'documento_numerico', 'inscricao_estadual',
            'email', 'telefone', 'contato_nome',
            'prazo_entrega_dias', 'condicao_pagamento',
            'observacoes', 'nome_exibicao',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tipo_pessoa', 'slug', 'created_at', 'updated_at']


class ColaboradorSerializer(serializers.ModelSerializer):
    """Serializer para Colaborador (Garçom, Caixa, etc)."""
    
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    
    class Meta:
        model = Colaborador
        fields = [
            'id', 'usuario', 'nome', 'cpf', 'cargo', 'cargo_display',
            'comissao_percentual', 'ativo', 'data_admissao',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
