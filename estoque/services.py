"""Serviços de Estoque.

Calcula saldos e registra movimentos: entrada, saída e ajuste,
garantindo validação de disponibilidade e atomicidade nas saídas.
"""
from typing import List, Dict
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from vendas.models import Produto, Pedido, ItemPedido
from .models import StockMovement, Deposito, MotivoAjuste


class EstoqueService:
    """Operações de saldo e movimentações de estoque."""
    @staticmethod
    def saldo_produto(produto: Produto, deposito: Deposito | None = None) -> int:
        """Calcula saldo do produto, opcional por depósito."""
        agg = 0
        qs = StockMovement.objects.filter(produto=produto)
        if deposito:
            qs = qs.filter(deposito=deposito)
        for mv in qs.values('tipo', 'quantidade'):
            if mv['tipo'] == StockMovement.Tipo.IN:
                agg += mv['quantidade']
            elif mv['tipo'] == StockMovement.Tipo.OUT:
                agg -= mv['quantidade']
            else:
                agg += mv['quantidade']
        return agg

    @staticmethod
    def verificar_disponibilidade(itens_payload: List[Dict]):
        """Valida se há estoque suficiente para cada item do payload."""
        slugs = [i.get('produto') for i in itens_payload]
        produtos = {p.slug: p for p in Produto.objects.filter(slug__in=slugs)}
        for item in itens_payload:
            key = item.get('produto')
            produto = produtos[key]
            required = int(item['quantidade'])
            if EstoqueService.saldo_produto(produto) < required:
                raise ValidationError(f"Estoque insuficiente para '{produto.slug}'.")

    @staticmethod
    def registrar_entrada(produto: Produto, quantidade: int, origem_slug: str | None = None, responsavel=None, observacao: str = "", deposito: Deposito | None = None):
        """Registra entrada (IN) de estoque."""
        if quantidade <= 0:
            raise ValidationError("Quantidade de entrada deve ser > 0.")
        return StockMovement.objects.create(
            produto=produto,
            tipo=StockMovement.Tipo.IN,
            quantidade=int(quantidade),
            origem_slug=origem_slug,
            responsavel=responsavel,
            observacao=observacao,
            deposito=deposito,
        )

    @staticmethod
    def registrar_saida(pedido: Pedido, itens: List[ItemPedido], deposito: Deposito | None = None):
        """Registra saídas (OUT) para itens do pedido, com validação e transação."""
        with transaction.atomic():
            for item in itens:
                if EstoqueService.saldo_produto(item.produto, deposito=deposito) < item.quantidade:
                    raise ValidationError(f"Estoque insuficiente para '{item.produto.slug}'.")
            for item in itens:
                StockMovement.objects.create(
                    produto=item.produto,
                    tipo=StockMovement.Tipo.OUT,
                    quantidade=int(item.quantidade),
                    origem_slug=pedido.slug,
                    pedido=pedido,
                    deposito=deposito,
                )

    @staticmethod
    def registrar_ajuste(produto: Produto, quantidade: int, origem_slug: str | None = None, responsavel=None, observacao: str = "", deposito: Deposito | None = None, motivo: MotivoAjuste | None = None):
        """Registra ajuste (ADJUST) positivo/negativo com motivo opcional."""
        if quantidade == 0:
            raise ValidationError("Quantidade de ajuste não pode ser zero.")
        return StockMovement.objects.create(
            produto=produto,
            tipo=StockMovement.Tipo.ADJUST,
            quantidade=int(quantidade),
            origem_slug=origem_slug,
            responsavel=responsavel,
            observacao=observacao,
            deposito=deposito,
            motivo_ajuste=motivo,
        )
