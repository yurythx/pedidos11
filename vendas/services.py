"""Serviços de Vendas.

Fornecem utilitários para consulta de produtos e construção de pedidos:
- filtro e busca de produtos disponíveis;
- validação de disponibilidade no payload;
- criação de itens e cálculo de total.
"""
from decimal import Decimal
from typing import List, Dict
from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from catalogo.models import Produto
from .models import ItemPedido, Pedido


class ProdutoService:
    """Consultas e filtros de produtos disponíveis."""
    @staticmethod
    def disponiveis() -> QuerySet[Produto]:
        return Produto.objects.filter(disponivel=True)

    @staticmethod
    def buscar_por_slug(slug: str) -> Produto:
        return Produto.objects.get(slug=slug, disponivel=True)

    @staticmethod
    def filtrar(categoria_slug: str | None = None, texto: str | None = None) -> QuerySet[Produto]:
        """Filtra produtos por categoria e texto (nome/SKU/EAN)."""
        qs = ProdutoService.disponiveis()
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
        if texto:
            qs = qs.filter(models.Q(nome__icontains=texto) | models.Q(sku__icontains=texto) | models.Q(ean__icontains=texto))
        return qs


class PedidoService:
    """Construção e validação de pedidos."""
    @staticmethod
    def validate_disponibilidade(itens_payload: List[Dict]):
        """Garante que todos os produtos do payload estão disponíveis."""
        slugs = [i.get('produto') for i in itens_payload]
        produtos = Produto.objects.filter(slug__in=slugs, disponivel=True)
        if produtos.count() != len(slugs):
            raise ValidationError("Um ou mais produtos não estão disponíveis.")

    @staticmethod
    def criar_itens(pedido: Pedido, itens_payload: List[Dict]) -> List[ItemPedido]:
        """Cria itens do pedido com preço atual do produto."""
        itens: List[ItemPedido] = []
        produtos_map = {p.slug: p for p in Produto.objects.filter(slug__in=[i.get('produto') for i in itens_payload])}
        for item in itens_payload:
            key = item.get('produto')
            produto = produtos_map[key]
            quantidade = int(item['quantidade'])
            ip = ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco,
            )
            itens.append(ip)
        return itens

    @staticmethod
    def calcular_total(itens: List[ItemPedido]) -> Decimal:
        """Soma subtotais de itens para total do pedido."""
        return sum((i.subtotal() for i in itens), Decimal('0.00'))
