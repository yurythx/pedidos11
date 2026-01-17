"""
Serviços de negócio para controle de estoque (Projeto Nix).

Responsabilidades:
- Explosão de Ficha Técnica (Bill of Materials)  
- Controle de lotes com FIFO/FEFO
- Baixa de estoque em vendas
- Validações de estoque
"""
from decimal import Decimal
from django.db import transaction, models
from django.core.exceptions import ValidationError


class StockService:
    """
    Serviços de controle de estoque com suporte a:
    - Explosão de ficha técnica (BOM)
    - Controle de lotes FIFO/FEFO
    - Integração com vendas
    """
    
    @staticmethod
    @transaction.atomic
    def processar_baixa_venda(item_venda, deposito, usar_lotes=True):
        """
        Processa baixa de estoque para um item de venda.
        
        Suporta:
        - Produtos FINAL/INSUMO: Baixa direta
        - Produtos COMPOSTO: Explosão de ficha técnica (baixa os componentes)
        - Lotes: Consumo FIFO/FEFO automático
        
        Args:
            item_venda: Instância de ItemVenda
            deposito: Depósito de onde baixar o estoque
            usar_lotes: Se True, usa controle de lotes FIFO (default: True)
        
        Raises:
            ValidationError: Se estoque insuficiente
        
        Exemplo:
            >>> item = ItemVenda.objects.get(...)
            >>> deposito = Deposito.objects.get(is_padrao=True)
            >>> StockService.processar_baixa_venda(item, deposito)
        """
        from catalog.models import TipoProduto
        
        produto = item_venda.produto
        
        if produto.tipo == TipoProduto.COMPOSTO:
            # Explosão de Materiais (Bill of Materials - BOM)
            StockService._baixar_produto_composto(
                produto=produto,
                quantidade=item_venda.quantidade,
                deposito=deposito,
                origem=f"VENDA-{item_venda.venda.numero if hasattr(item_venda.venda, 'numero') else item_venda.venda.id}",
                usar_lotes=usar_lotes
            )
        else:
            # Produto final ou insumo vendido diretamente
            StockService._baixar_produto_simples(
                produto=produto,
                quantidade=item_venda.quantidade,
                deposito=deposito,
                origem=f"VENDA-{item_venda.venda.numero if hasattr(item_venda.venda, 'numero') else item_venda.venda.id}",
                usar_lotes=usar_lotes
            )
    
    @staticmethod
    def _baixar_produto_composto(produto, quantidade, deposito, origem, usar_lotes):
        """
        Explosão recursiva da ficha técnica.
        
        Args:
            produto: Produto COMPOSTO
            quantidade: Quantidade do produto composto a ser produzido
            deposito: Depósito de onde baixar componentes
            origem: Descrição da origem (para auditoria)
            usar_lotes: Se usa controle de lotes
        """
        from catalog.models import TipoProduto
        
        for item_ficha in produto.ficha_tecnica.select_related('componente').all():
            qtd_a_baixar = quantidade * item_ficha.quantidade_liquida
            componente = item_ficha.componente
            
            # Recursividade: Se o componente também for composto, explode novamente
            if componente.tipo == TipoProduto.COMPOSTO:
                StockService._baixar_produto_composto(
                    produto=componente,
                    quantidade=qtd_a_baixar,
                    deposito=deposito,
                    origem=origem,
                    usar_lotes=usar_lotes
                )
            else:
                # Componente é FINAL ou INSUMO, baixa direto
                StockService._baixar_produto_simples(
                    produto=componente,
                    quantidade=qtd_a_baixar,
                    deposito=deposito,
                    origem=origem,
                    usar_lotes=usar_lotes
                )
    
    @staticmethod
    @transaction.atomic
    def _baixar_produto_simples(produto, quantidade, deposito, origem, usar_lotes):
        """
        Baixa de produto simples (FINAL ou INSUMO).
        
        Args:
            produto: Produto a baixar
            quantidade: Quantidade a baixar
            deposito: Depósito
            origem: Origem da movimentação
            usar_lotes: Se True, usa FIFO. Se False, baixa sem lote
        """
        if usar_lotes:
            StockService._baixar_com_fifo(produto, quantidade, deposito, origem)
        else:
            StockService._baixar_sem_lote(produto, quantidade, deposito, origem)
    
    @staticmethod
    def _baixar_com_fifo(produto, quantidade_total, deposito, origem):
        """
        Algoritmo FIFO/FEFO: Consome lotes por ordem de validade.
        
        Itera sobre lotes ordenados por data de validade (ascendente),
        consumindo do mais próximo ao vencimento até completar a quantidade.
        
        Args:
            produto: Produto a baixar
            quantidade_total: Quantidade total a baixar
            deposito: Depósito
            origem: Descrição da origem
        
        Raises:
            ValidationError: Se estoque insuficiente nos lotes
        """
        from stock.models import Lote, Movimentacao, TipoMovimentacao
        
        # Busca lotes disponíveis ordenados por validade (FEFO - First Expired, First Out)
        lotes_disponiveis = Lote.objects.filter(
            empresa=deposito.empresa,
            produto=produto,
            deposito=deposito,
            quantidade_atual__gt=0
        ).order_by('data_validade', 'data_fabricacao').select_for_update()
        
        qtd_restante = quantidade_total
        movimentacoes_criadas = []
        
        for lote in lotes_disponiveis:
            if qtd_restante <= 0:
                break
            
            # Quanto posso tirar deste lote?
            qtd_a_retirar = min(qtd_restante, lote.quantidade_atual)
            
            # 1. Cria movimentação linkada ao lote
            mov = Movimentacao.objects.create(
                empresa=deposito.empresa,
                produto=produto,
                deposito=deposito,
                lote=lote,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=qtd_a_retirar,
                valor_unitario=produto.preco_custo or Decimal('0'),
                documento=origem,
                observacao=f"FIFO - Lote {lote.codigo_lote}"
            )
            movimentacoes_criadas.append(mov)
            
            # 2. Atualiza saldo do lote
            lote.quantidade_atual -= qtd_a_retirar
            lote.save(update_fields=['quantidade_atual', 'updated_at'])
            
            qtd_restante -= qtd_a_retirar
        
        # Fallback: Estoque insuficiente?
        if qtd_restante > 0:
            # Rollback: Remove movimentações criadas
            for mov in movimentacoes_criadas:
                mov.delete()
            
            raise ValidationError(
                f"Estoque insuficiente de '{produto.nome}' no depósito '{deposito.nome}'. "
                f"Necessário: {quantidade_total}, Disponível em lotes: {quantidade_total - qtd_restante}"
            )
    
    @staticmethod
    def _baixar_sem_lote(produto, quantidade, deposito, origem):
        """
        Baixa de estoque SEM controle de lote (modo legado).
        
        Args:
            produto: Produto a baixar
            quantidade: Quantidade a baixar
            deposito: Depósito
            origem: Descrição da origem
        """
        from stock.models import Movimentacao, TipoMovimentacao
        
        # Cria movimentação simples sem lote
        Movimentacao.objects.create(
            empresa=deposito.empresa,
            produto=produto,
            deposito=deposito,
            lote=None,
            tipo=TipoMovimentacao.SAIDA,
            quantidade=quantidade,
            valor_unitario=produto.preco_custo or Decimal('0'),
            documento=origem,
            observacao="Baixa sem controle de lote"
        )
    
    @staticmethod
    @transaction.atomic
    def dar_entrada_com_lote(produto, deposito, quantidade, codigo_lote, 
                            data_validade, data_fabricacao=None, 
                            valor_unitario=None, documento='', observacao=''):
        """
        Dá entrada de produto com criação/atualização de lote.
        
        Se o lote já existir, incrementa a quantidade.
        Se não existir, cria um novo lote.
        
        Args:
            produto: Produto
            deposito: Depósito
            quantidade: Quantidade a dar entrada
            codigo_lote: Código do lote
            data_validade: Data de validade do lote
            data_fabricacao: Data de fabricação (opcional)
            valor_unitario: Valor unitário (opcional, usa preco_custo se não informado)
            documento: Número do documento (NF, etc)
            observacao: Observações
        
        Returns:
            tuple: (lote, movimentacao)
        """
        from stock.models import Lote, Movimentacao, TipoMovimentacao
        
        # Normaliza datas se vierem como string
        from datetime import date
        def _to_date(d):
            if d is None:
                return None
            if isinstance(d, date):
                return d
            try:
                return date.fromisoformat(str(d))
            except Exception:
                return None
        
        data_validade = _to_date(data_validade)
        data_fabricacao = _to_date(data_fabricacao)
        
        # Busca ou cria o lote
        lote, created = Lote.objects.get_or_create(
            empresa=deposito.empresa,
            produto=produto,
            deposito=deposito,
            codigo_lote=codigo_lote,
            defaults={
                'data_validade': data_validade,
                'data_fabricacao': data_fabricacao,
                'quantidade_atual': Decimal('0')
            }
        )
        
        if not created:
            # Lote existente - valida se validade é a mesma
            if lote.data_validade != data_validade:
                raise ValidationError(
                    f"Lote {codigo_lote} já existe com validade diferente. "
                    f"Existente: {lote.data_validade}, Informado: {data_validade}"
                )
        
        # Cria movimentação de entrada
        mov = Movimentacao.objects.create(
            empresa=deposito.empresa,
            produto=produto,
            deposito=deposito,
            lote=lote,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            valor_unitario=valor_unitario or produto.preco_custo or Decimal('0'),
            documento=documento,
            observacao=observacao or f"Entrada de lote {codigo_lote}"
        )
        
        # Atualiza quantidade do lote
        lote.quantidade_atual += quantidade
        lote.save(update_fields=['quantidade_atual', 'updated_at'])
        
        return lote, mov
    
    @staticmethod
    def validar_estoque_disponivel(produto, deposito, quantidade_necessaria, usar_lotes=True):
        """
        Valida se há estoque suficiente para a operação.
        
        Args:
            produto: Produto a verificar
            deposito: Depósito
            quantidade_necessaria: Quantidade requerida  
            usar_lotes: Se True, verifica em lotes. Se False, verifica saldo geral
        
        Returns:
            dict: {
                'disponivel': bool,
                'quantidade_disponivel': Decimal,
                'quantidade_necessaria': Decimal,
                'deficit': Decimal (se insuficiente)
            }
        """
        from stock.models import Saldo, Lote
        from catalog.models import TipoProduto
        
        # Se for produto composto, valida os componentes
        if produto.tipo == TipoProduto.COMPOSTO:
            for item in produto.ficha_tecnica.select_related('componente').all():
                qtd_componente = item.quantidade_liquida * quantidade_necessaria
                resultado = StockService.validar_estoque_disponivel(
                    item.componente,
                    deposito,
                    qtd_componente,
                    usar_lotes
                )
                if not resultado['disponivel']:
                    return resultado
            
            return {'disponivel': True, 'quantidade_disponivel': quantidade_necessaria}
        
        # Produto simples
        if usar_lotes:
            # Soma saldo em lotes
            qtd_total = Lote.objects.filter(
                empresa=deposito.empresa,
                produto=produto,
                deposito=deposito,
                quantidade_atual__gt=0
            ).aggregate(
                total=models.Sum('quantidade_atual')
            )['total'] or Decimal('0')
        else:
            # Verifica saldo geral
            try:
                saldo = Saldo.objects.get(
                    empresa=deposito.empresa,
                    produto=produto,
                    deposito=deposito
                )
                qtd_total = saldo.quantidade
            except Saldo.DoesNotExist:
                qtd_total = Decimal('0')
        
        disponivel = qtd_total >= quantidade_necessaria
        deficit = max(Decimal('0'), quantidade_necessaria - qtd_total)
        
        return {
            'disponivel': disponivel,
            'quantidade_disponivel': qtd_total,
            'quantidade_necessaria': quantidade_necessaria,
            'deficit': deficit
        }
