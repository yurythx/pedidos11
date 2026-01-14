"""
Exporta todos os serializers.
"""
from .catalog import CategoriaSerializer, ProdutoListSerializer, ProdutoDetailSerializer, ProdutoCreateUpdateSerializer
from .stock import DepositoSerializer, SaldoSerializer, MovimentacaoSerializer
from .sales import VendaListSerializer, VendaDetailSerializer, VendaCreateSerializer, ItemVendaSerializer, ItemVendaComplementoSerializer
from .partners import ClienteSerializer, FornecedorSerializer
from .financial import ContaReceberSerializer, ContaPagarSerializer
from .restaurant import SetorImpressaoSerializer, MesaSerializer, ComandaSerializer

__all__ = [
    # Catalog
    'CategoriaSerializer',
    'ProdutoListSerializer',
    'ProdutoDetailSerializer',
    'ProdutoCreateUpdateSerializer',
    
    # Stock
    'DepositoSerializer',
    'SaldoSerializer',
    'MovimentacaoSerializer',
    
    # Sales
    'VendaListSerializer',
    'VendaDetailSerializer',
    'VendaCreateSerializer',
    'ItemVendaSerializer',
    'ItemVendaComplementoSerializer',
    
    # Partners
    'ClienteSerializer',
    'FornecedorSerializer',
    
    # Financial
    'ContaReceberSerializer',
    'ContaPagarSerializer',
    
    # Restaurant
    'SetorImpressaoSerializer',
    'MesaSerializer',
    'ComandaSerializer',
]
