from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from tenant.models import Empresa
from catalog.models import Categoria
from .serializers.public import PublicEmpresaSerializer, PublicCategoriaSerializer

class PublicMenuViewSet(viewsets.ViewSet):
    """
    API Pública para o Cardápio Digital.
    Não requer autenticação.
    Baseado no slug da empresa na URL.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = [] # Remove autenticação para garantir acesso público

    @action(detail=False, methods=['get'], url_path='(?P<slug>[^/.]+)/info')
    def info(self, request, slug=None):
        """Retorna informações da empresa pelo slug."""
        empresa = get_object_or_404(Empresa, slug=slug, is_active=True)
        serializer = PublicEmpresaSerializer(empresa)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='(?P<slug>[^/.]+)/catalogo')
    def catalogo(self, request, slug=None):
        """Retorna o catálogo completo (categorias -> produtos) da empresa."""
        empresa = get_object_or_404(Empresa, slug=slug, is_active=True)
        
        # Busca categorias ativas
        categorias = Categoria.objects.filter(
            empresa=empresa, 
            is_active=True
        ).order_by('ordem', 'nome')
        
        # Filtra categorias vazias (opcional, mas bom para UX)
        # Por performance, vamos retornar todas e o frontend esconde se vazio
        
        serializer = PublicCategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
