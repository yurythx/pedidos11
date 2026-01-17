"""
Paginação customizada para API.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardPagination(PageNumberPagination):
    """
    Paginação padrão do Projeto Nix.
    
    Features:
    - Tamanho padrão: 50 itens
    - Customizável via query param: page_size
    - Máximo: 1000 itens
    - Metadata rico na resposta
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    def get_paginated_response(self, data):
        """
        Retorna resposta paginada com metadata enriquecida.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.page_size),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('results', data)
        ]))


class SmallPagination(PageNumberPagination):
    """Paginação para listas pequenas (ex: categorias)."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """Paginação para relatórios grandes."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000
