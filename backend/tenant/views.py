from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Empresa
from .serializers import EmpresaSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar dados da Empresa (Tenant).
    Geralmente o usuário só tem acesso à sua própria empresa.
    """
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas a empresa do usuário logado."""
        return Empresa.objects.filter(id=self.request.user.empresa.id)
        
    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        """
        Endpoint para ler/editar a própria empresa.
        GET /api/empresa/me/
        PATCH /api/empresa/me/
        """
        empresa = request.user.empresa
        
        if request.method == 'GET':
            serializer = self.get_serializer(empresa)
            return Response(serializer.data)
            
        elif request.method in ['PATCH', 'PUT']:
            serializer = self.get_serializer(empresa, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
