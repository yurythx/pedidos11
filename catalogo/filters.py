import django_filters
from .models import Produto


class ProdutoFilterSet(django_filters.FilterSet):
    categoria = django_filters.CharFilter(field_name='categoria__slug')
    marca = django_filters.CharFilter(field_name='marca', lookup_expr='icontains')
    unidade = django_filters.CharFilter(field_name='unidade')
    sku = django_filters.CharFilter(field_name='sku', lookup_expr='icontains')
    ean = django_filters.CharFilter(field_name='ean', lookup_expr='icontains')
    preco_min = django_filters.NumberFilter(field_name='preco', lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name='preco', lookup_expr='lte')

    class Meta:
        model = Produto
        fields = ['categoria', 'marca', 'unidade', 'sku', 'ean', 'preco_min', 'preco_max', 'disponivel']
