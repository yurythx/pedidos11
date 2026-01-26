from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD de Usuários.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_colaborador', 'role_atendente', 'role_caixa', 'is_active']
    
    def get_queryset(self):
        # Filtra por empresa do usuário logado
        return CustomUser.objects.filter(empresa=self.request.user.empresa)

    def perform_create(self, serializer):
        # Associa automaticamente à empresa do usuário logado
        serializer.save(empresa=self.request.user.empresa)
