"""
Serializers customizados para autenticação JWT.
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from authentication.models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para adicionar informações extras ao token JWT.
    
    Adiciona ao payload:
    - nome_empresa
    - empresa_id
    - cargo
    - permissions
    - is_superuser
    
    Isso permite que o frontend saiba quem está logado sem fazer request extra.
    """
    
    @classmethod
    def get_token(cls, user):
        """Adiciona claims customizados ao token."""
        token = super().get_token(user)
        
        # Adiciona informações do usuário
        token['username'] = user.username
        token['email'] = user.email
        token['nome_completo'] = user.get_full_name()
        
        # Informações da empresa (multi-tenancy)
        if user.empresa:
            token['empresa_id'] = str(user.empresa.id)
            token['nome_empresa'] = user.empresa.nome_fantasia
        else:
            token['empresa_id'] = None
            token['nome_empresa'] = None
        
        # Cargo e permissões
        token['cargo'] = user.cargo
        token['cargo_display'] = user.get_cargo_display()
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        
        # Permissões (lista de strings)
        token['permissions'] = list(user.get_all_permissions())
        
        # Flags úteis para frontend
        token['is_admin'] = user.is_admin
        token['is_gerente'] = user.is_gerente
        token['is_vendedor'] = user.is_vendedor
        
        return token
    
    def validate(self, attrs):
        """Validação customizada."""
        data = super().validate(attrs)
        
        # Adiciona informações do usuário na resposta
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'nome_completo': self.user.get_full_name(),
            'cargo': self.user.cargo,
            'cargo_display': self.user.get_cargo_display(),
            'empresa': {
                'id': str(self.user.empresa.id) if self.user.empresa else None,
                'nome': self.user.empresa.nome_fantasia if self.user.empresa else None
            }
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer para informações do usuário logado."""
    
    empresa_nome = serializers.CharField(source='empresa.nome_fantasia', read_only=True)
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    is_admin = serializers.ReadOnlyField()
    is_gerente = serializers.ReadOnlyField()
    is_vendedor = serializers.ReadOnlyField()
    foto_perfil = serializers.ImageField(required=False, allow_null=True)
    telefone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'telefone', 'foto_perfil',
            'empresa', 'empresa_nome', 'cargo', 'cargo_display',
            'is_admin', 'is_gerente', 'is_vendedor',
            'is_active', 'is_staff', 'is_superuser',
            'password'
        ]
        read_only_fields = ['id', 'empresa', 'is_active', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
