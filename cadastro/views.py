from rest_framework import viewsets, permissions
from .models import Address, Supplier, Customer
from .serializers import AddressSerializer, SupplierSerializer, CustomerSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by('-criado_em')
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAdminUser]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-criado_em')
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-criado_em')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
