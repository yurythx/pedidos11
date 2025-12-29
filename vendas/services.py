from decimal import Decimal
from typing import List, Dict
from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from .models import Produto, ItemPedido, Pedido


class ProdutoService:
    @staticmethod
    def disponiveis() -> QuerySet[Produto]:
        return Produto.objects.filter(disponivel=True)

    @staticmethod
    def buscar_por_slug(slug: str) -> Produto:
        return Produto.objects.get(slug=slug, disponivel=True)

    @staticmethod
    def filtrar(categoria_slug: str | None = None, texto: str | None = None) -> QuerySet[Produto]:
        qs = ProdutoService.disponiveis()
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
        if texto:
            qs = qs.filter(models.Q(nome__icontains=texto) | models.Q(sku__icontains=texto) | models.Q(ean__icontains=texto))
        return qs


class PedidoService:
    @staticmethod
    def validate_disponibilidade(itens_payload: List[Dict]):
        slugs = [i.get('produto') for i in itens_payload]
        produtos = Produto.objects.filter(slug__in=slugs, disponivel=True)
        if produtos.count() != len(slugs):
            raise ValidationError("Um ou mais produtos não estão disponíveis.")

    @staticmethod
    def criar_itens(pedido: Pedido, itens_payload: List[Dict]) -> List[ItemPedido]:
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
        return sum((i.subtotal() for i in itens), Decimal('0.00'))
