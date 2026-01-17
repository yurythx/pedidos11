"""
Filtros avançados para API usando django-filter.
"""
from django_filters import rest_framework as filters
from django.db.models import Q

from sales.models import Venda, ItemVenda
from catalog.models import Produto, Categoria
from stock.models import Movimentacao, Saldo
from partners.models import Cliente, Fornecedor
from financial.models import ContaReceber, ContaPagar


class VendaFilter(filters.FilterSet):
    """
    Filtros avançados para Vendas.
    
    Exemplos de uso:
    - ?data_inicio=2026-01-01&data_fim=2026-01-31
    - ?valor_min=100&valor_max=1000
    - ?status=FINALIZADA&tipo_pagamento=PIX
    - ?cliente_nome=João
    """
    # Filtros de data
    data_inicio = filters.DateFilter(
        field_name='data_emissao',
        lookup_expr='gte',
        label='Data Início'
    )
    data_fim = filters.DateFilter(
        field_name='data_emissao',
        lookup_expr='lte',
        label='Data Fim'
    )
    
    # Filtros de valor
    valor_min = filters.NumberFilter(
        field_name='total_liquido',
        lookup_expr='gte',
        label='Valor Mínimo'
    )
    valor_max = filters.NumberFilter(
        field_name='total_liquido',
        lookup_expr='lte',
        label='Valor Máximo'
    )
    
    # Busca por cliente
    cliente_nome = filters.CharFilter(
        field_name='cliente__nome',
        lookup_expr='icontains',
        label='Nome do Cliente'
    )
    
    # Busca por vendedor
    vendedor_username = filters.CharFilter(
        field_name='vendedor__username',
        lookup_expr='icontains',
        label='Username do Vendedor'
    )
    
    class Meta:
        model = Venda
        fields = {
            'status': ['exact', 'in'],
            'tipo_pagamento': ['exact', 'in'],
            'numero': ['exact', 'gte', 'lte'],
        }


class ProdutoFilter(filters.FilterSet):
    """
    Filtros avançados para Produtos.
    
    Exemplos:
    - ?preco_min=10&preco_max=100
    - ?categoria_nome=Bebidas
    - ?destaque=true&is_active=true
    - ?search=coca
    """
    # Filtros de preço
    preco_min = filters.NumberFilter(
        field_name='preco_venda',
        lookup_expr='gte',
        label='Preço Mínimo'
    )
    preco_max = filters.NumberFilter(
        field_name='preco_venda',
        lookup_expr='lte',
        label='Preço Máximo'
    )
    
    # Busca por categoria
    categoria_nome = filters.CharFilter(
        field_name='categoria__nome',
        lookup_expr='icontains',
        label='Nome da Categoria'
    )
    
    # Busca geral (nome ou SKU)
    search = filters.CharFilter(
        method='filter_search',
        label='Busca Geral'
    )
    
    def filter_search(self, queryset, name, value):
        """Busca em nome, SKU ou código de barras."""
        return queryset.filter(
            Q(nome__icontains=value) |
            Q(sku__icontains=value) |
            Q(codigo_barras__icontains=value)
        )
    
    class Meta:
        model = Produto
        fields = {
            'tipo': ['exact', 'in'],
            'destaque': ['exact'],
            'is_active': ['exact'],
            'categoria': ['exact'],
        }


class MovimentacaoFilter(filters.FilterSet):
    """
    Filtros para movimentações de estoque.
    
    Exemplos:
    - ?tipo=ENTRADA&data_inicio=2026-01-01
    - ?produto_nome=Coca&deposito=uuid
    """
    # Filtros de data
    data_inicio = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Data Início'
    )
    data_fim = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Data Fim'
    )
    
    # Busca por produto
    produto_nome = filters.CharFilter(
        field_name='produto__nome',
        lookup_expr='icontains',
        label='Nome do Produto'
    )
    
    # Busca por documento
    documento = filters.CharFilter(
        lookup_expr='icontains',
        label='Número do Documento'
    )
    
    class Meta:
        model = Movimentacao
        fields = {
            'tipo': ['exact', 'in'],
            'deposito': ['exact'],
            'produto': ['exact'],
        }


class ClienteFilter(filters.FilterSet):
    """Filtros para clientes."""
    
    nome = filters.CharFilter(
        lookup_expr='icontains',
        label='Nome'
    )
    
    cpf_cnpj = filters.CharFilter(
        lookup_expr='icontains',
        label='CPF/CNPJ'
    )
    
    class Meta:
        model = Cliente
        fields = {
            'tipo_pessoa': ['exact'],
            'is_active': ['exact'],
        }


class FornecedorFilter(filters.FilterSet):
    """Filtros para fornecedores."""
    
    razao_social = filters.CharFilter(
        lookup_expr='icontains',
        label='Razão Social'
    )
    
    nome_fantasia = filters.CharFilter(
        lookup_expr='icontains',
        label='Nome Fantasia'
    )
    
    class Meta:
        model = Fornecedor
        fields = {
            'is_active': ['exact'],
        }


class ContaReceberFilter(filters.FilterSet):
    """
    Filtros para contas a receber.
    
    Exemplos:
    - ?status=PENDENTE&vencimento_inicio=2026-01-01
    - ?vencidas=true
    """
    vencimento_inicio = filters.DateFilter(
        field_name='data_vencimento',
        lookup_expr='gte',
        label='Vencimento Início'
    )
    vencimento_fim = filters.DateFilter(
        field_name='data_vencimento',
        lookup_expr='lte',
        label='Vencimento Fim'
    )
    
    vencidas = filters.BooleanFilter(
        method='filter_vencidas',
        label='Apenas Vencidas'
    )
    
    def filter_vencidas(self, queryset, name, value):
        """Filtra apenas contas vencidas."""
        if value:
            from django.utils import timezone
            return queryset.filter(
                data_vencimento__lt=timezone.now().date(),
                status='PENDENTE'
            )
        return queryset
    
    class Meta:
        model = ContaReceber
        fields = {
            'status': ['exact', 'in'],
            'cliente': ['exact'],
        }


class ContaPagarFilter(filters.FilterSet):
    """Filtros para contas a pagar."""
    
    vencimento_inicio = filters.DateFilter(
        field_name='data_vencimento',
        lookup_expr='gte'
    )
    vencimento_fim = filters.DateFilter(
        field_name='data_vencimento',
        lookup_expr='lte'
    )
    
    vencidas = filters.BooleanFilter(
        method='filter_vencidas',
        label='Apenas Vencidas'
    )
    
    def filter_vencidas(self, queryset, name, value):
        if value:
            from django.utils import timezone
            return queryset.filter(
                data_vencimento__lt=timezone.now().date(),
                status='PENDENTE'
            )
        return queryset
    
    class Meta:
        model = ContaPagar
        fields = {
            'status': ['exact', 'in'],
            'fornecedor': ['exact'],
        }
