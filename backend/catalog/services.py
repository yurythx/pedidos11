"""
Serviços de negócio para o módulo de catálogo (Projeto Nix).

Responsabilidades:
- Cálculo de custo de produtos compostos
- Propagação de alterações de custo
- Validações de ficha técnica
"""
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError


class CatalogService:
    """
    Serviços de negócio para gestão de catálogo e fichas técnicas.
    
    Implementa lógica de cálculo de custo baseado em Bill of Materials (BOM).
    """
    
    @staticmethod
    @transaction.atomic
    def recalcular_custo_produto(produto):
        """
        Recalcula o custo de um produto composto baseado na sua ficha técnica.
        
        O custo final é a soma dos custos de todos os componentes.
        Se um item tiver custo_fixo, usa esse valor ao invés do calculado.
        
        Args:
            produto: Instância de Produto (tipo COMPOSTO)
        
        Returns:
            Decimal: Custo total calculado
        
        Raises:
            ValidationError: Se o produto não for do tipo COMPOSTO
        
        Exemplo:
            >>> produto = Produto.objects.get(nome='X-Burger')
            >>> CatalogService.recalcular_custo_produto(produto)
            Decimal('12.50')
        """
        from catalog.models import TipoProduto
        
        if produto.tipo != TipoProduto.COMPOSTO:
            raise ValidationError(
                f"Produto '{produto.nome}' não é do tipo COMPOSTO. "
                f"Tipo atual: {produto.get_tipo_display()}"
            )
        
        custo_total = Decimal('0')
        
        for item in produto.ficha_tecnica.select_related('componente').all():
            custo_total += item.custo_calculado
        
        # Atualiza o custo do produto
        produto.preco_custo = custo_total
        produto.save(update_fields=['preco_custo', 'updated_at'])
        
        return custo_total
    
    @staticmethod
    @transaction.atomic
    def propagar_custo_insumo(insumo):
        """
        Quando o custo de um insumo muda, recalcula todos os produtos que o utilizam.
        
        Propagação em cascata:
        1. Busca todos os produtos COMPOSTO que usam este insumo
        2. Recalcula o custo de cada um
        3. Se algum desses produtos também for usado em outro, propaga novamente
        
        Args:
            insumo: Instância de Produto (geralmente tipo INSUMO ou FINAL)
        
        Returns:
            list: Lista de produtos que tiveram o custo recalculado
        
        Exemplo:
            >>> bacon = Produto.objects.get(nome='Bacon')
            >>> bacon.preco_custo = Decimal('45.00')
            >>> bacon.save()
            >>> afetados = CatalogService.propagar_custo_insumo(bacon)
            >>> # X-Burger, X-Bacon, etc serão recalculados
        """
        from catalog.models import Produto, TipoProduto
        
        produtos_recalculados = []
        
        # Busca todos os produtos COMPOSTO que usam este insumo
        produtos_afetados = Produto.objects.filter(
            ficha_tecnica__componente=insumo,
            tipo=TipoProduto.COMPOSTO,
            is_active=True
        ).distinct().select_for_update()
        
        for produto in produtos_afetados:
            CatalogService.recalcular_custo_produto(produto)
            produtos_recalculados.append(produto)
            
            # Recursão: Se este produto também é usado em outros, propaga novamente
            CatalogService.propagar_custo_insumo(produto)
        
        return produtos_recalculados
    
    @staticmethod
    def validar_ciclo_ficha_tecnica(produto_pai, componente, nivel=0, max_nivel=10):
        """
        Valida se adicionar um componente criaria um ciclo na ficha técnica.
        
        Previne situações como:
        - A compõe B que compõe A (ciclo direto)
        - A compõe B que compõe C que compõe A (ciclo indireto)
        
        Args:
            produto_pai: Produto que receberá o componente
            componente: Produto que será adicionado como componente
            nivel: Nível atual de recursão (para prevenir stack overflow)
            max_nivel: Profundidade máxima permitida
        
        Returns:
            bool: True se válido (sem ciclo), False se há ciclo
        
        Raises:
            ValidationError: Se detectar ciclo ou profundidade excessiva
        """
        from catalog.models import TipoProduto
        
        # Proteção contra recursão infinita
        if nivel > max_nivel:
            raise ValidationError(
                f"Ficha técnica muito profunda (máximo {max_nivel} níveis). "
                "Verifique se não há ciclos."
            )
        
        # Caso base: se componente não é COMPOSTO, não há risco de ciclo
        if componente.tipo != TipoProduto.COMPOSTO:
            return True
        
        # Verifica se o componente usa o produto_pai em sua ficha técnica
        for item in componente.ficha_tecnica.select_related('componente').all():
            if item.componente_id == produto_pai.id:
                raise ValidationError(
                    f"Ciclo detectado: '{produto_pai.nome}' não pode compor '{componente.nome}' "
                    f"pois '{componente.nome}' já usa '{produto_pai.nome}' como componente."
                )
            
            # Recursão: Verifica os componentes dos componentes
            CatalogService.validar_ciclo_ficha_tecnica(
                produto_pai, 
                item.componente, 
                nivel + 1,
                max_nivel
            )
        
        return True
    
    @staticmethod
    def calcular_custo_producao_estimado(produto, quantidade):
        """
        Calcula o custo estimado para produzir uma quantidade de produtos compostos.
        
        Útil para:
        - Previsão de custos
        - Planejamento de compras
        - Cálculo de margem por pedido
        
        Args:
            produto: Produto composto
            quantidade: Quantidade a produzir
        
        Returns:
            dict: {
                'custo_unitario': Decimal,
                'custo_total': Decimal,
                'detalhamento': list[dict] com cada componente
            }
        """
        from catalog.models import TipoProduto
        
        if produto.tipo != TipoProduto.COMPOSTO:
            return {
                'custo_unitario': produto.preco_custo,
                'custo_total': produto.preco_custo * Decimal(str(quantidade)),
                'detalhamento': []
            }
        
        detalhamento = []
        custo_unitario = Decimal('0')
        
        for item in produto.ficha_tecnica.select_related('componente').all():
            custo_item = item.custo_calculado
            qtd_total_componente = item.quantidade_liquida * Decimal(str(quantidade))
            
            detalhamento.append({
                'componente': item.componente.nome,
                'quantidade_unitaria': item.quantidade_liquida,
                'quantidade_total': qtd_total_componente,
                'custo_unitario_componente': item.componente.preco_custo,
                'custo_total_componente': custo_item * Decimal(str(quantidade))
            })
            
            custo_unitario += custo_item
        
        return {
            'custo_unitario': custo_unitario,
            'custo_total': custo_unitario * Decimal(str(quantidade)),
            'detalhamento': detalhamento
        }
    
    @staticmethod
    def obter_lista_insumos_necessarios(produto, quantidade=1):
        """
        Retorna lista completa de insumos necessários para produzir um produto.
        
        Faz explosão completa da ficha técnica (recursiva).
        
        Args:
            produto: Produto composto
            quantidade: Quantidade a produzir
        
        Returns:
            dict: {produto_id: {'produto': Produto, 'quantidade': Decimal}}
        """
        from catalog.models import TipoProduto
        
        insumos = {}
        
        if produto.tipo != TipoProduto.COMPOSTO:
            # Produto final/insumo direto
            insumos[produto.id] = {
                'produto': produto,
                'quantidade': Decimal(str(quantidade))
            }
            return insumos
        
        # Explosão recursiva
        for item in produto.ficha_tecnica.select_related('componente').all():
            qtd_componente = item.quantidade_liquida * Decimal(str(quantidade))
            
            if item.componente.tipo == TipoProduto.COMPOSTO:
                # Recursão: Explode o componente também
                sub_insumos = CatalogService.obter_lista_insumos_necessarios(
                    item.componente, 
                    qtd_componente
                )
                
                # Acumula as quantidades
                for insumo_id, dados in sub_insumos.items():
                    if insumo_id in insumos:
                        insumos[insumo_id]['quantidade'] += dados['quantidade']
                    else:
                        insumos[insumo_id] = dados
            else:
                # Insumo final
                if item.componente.id in insumos:
                    insumos[item.componente.id]['quantidade'] += qtd_componente
                else:
                    insumos[item.componente.id] = {
                        'produto': item.componente,
                        'quantidade': qtd_componente
                    }
        
        return insumos
