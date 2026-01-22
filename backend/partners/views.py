from rest_framework import viewsets, permissions
from .models import Cliente, Fornecedor, Colaborador
from api.serializers.partners import ClienteSerializer, FornecedorSerializer, ColaboradorSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cliente.objects.filter(empresa=self.request.user.empresa)

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Fornecedor.objects.filter(empresa=self.request.user.empresa)

class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Colaborador.objects.filter(empresa=self.request.user.empresa)
