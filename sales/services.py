"""
Service Layer para o módulo de vendas.
Orquestra regras de negócio complexas e integração entre módulos.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import Venda, ItemVenda, StatusVenda


class VendaService:
    """
    Service responsável por orquestrar operações de vendas.
    
    Implementa o padrão Transaction Script para isolar lógica de negócio
    complexa dos controllers/views, facilitando testes e reutilização.
    
    Responsabilidades:
    - Finalizar vendas (com baixa de estoque)
    - Cancelar vendas (com devolução de estoque)
    - Validar regras de negócio antes de operações
    - Garantir consistência transacional
    """
    
    @staticmethod
    @transaction.atomic
    def finalizar_venda(venda_id, deposito_id, usuario=None):
        """
        Finaliza uma venda e baixa o estoque correspondente.
        
        REGRAS DE NEGÓCIO:
        1. Venda deve estar em status ORCAMENTO ou PENDENTE
        2. Verificar disponibilidade de estoque ANTES de baixar
        3. Criar movimentação de SAIDA para cada item
        4. Atualizar status para FINALIZADA
        5. Registrar data de finalização
        6. Tudo em uma transação atômica (rollback em caso de erro)
        
        Args:
            venda_id: UUID da venda a finalizar
            deposito_id: UUID do depósito de onde sair o estoque
            usuario: Username do usuário finalizando (para auditoria)
        
        Returns:
            Venda: Instância da venda finalizada
        
        Raises:
            ValidationError: Se venda não pode ser finalizada ou estoque insuficiente
        """
        # Import tardio para evitar circular import
        from stock.models import Saldo, Movimentacao, TipoMovimentacao, Deposito
        
        # 1. Busca venda com lock para prevenir race condition
        try:
            venda = Venda.objects.select_for_update().get(id=venda_id)
        except Venda.DoesNotExist:
            raise ValidationError(f"Venda com ID {venda_id} não encontrada")
        
        # 2. Valida se venda pode ser finalizada
        if not venda.pode_ser_finalizada:
            raise ValidationError(
                f"Venda #{venda.numero} não pode ser finalizada. "
                f"Status atual: {venda.get_status_display()}"
            )
        
        # 3. Busca depósito
        try:
            deposito = Deposito.objects.get(id=deposito_id, empresa=venda.empresa)
        except Deposito.DoesNotExist:
            raise ValidationError(f"Depósito com ID {deposito_id} não encontrado")
        
        # 4. Busca itens da venda
        itens = venda.itens.select_related('produto').all()
        
        if not itens.exists():
            raise ValidationError(
                f"Venda #{venda.numero} não possui itens. "
                "Adicione produtos antes de finalizar."
            )
        
        # 5. VALIDAÇÃO PRÉVIA: Verifica estoque disponível para TODOS os itens
        erros_estoque = []
        for item in itens:
            try:
                saldo = Saldo.objects.get(
                    empresa=venda.empresa,
                    produto=item.produto,
                    deposito=deposito
                )
                
                if saldo.quantidade < item.quantidade:
                    erros_estoque.append(
                        f"• {item.produto.nome}: Disponível {saldo.quantidade}, "
                        f"Necessário {item.quantidade}"
                    )
            except Saldo.DoesNotExist:
                erros_estoque.append(
                    f"• {item.produto.nome}: Produto sem estoque no depósito {deposito.nome}"
                )
        
        # Se houver erros de estoque, aborta com mensagem detalhada
        if erros_estoque:
            raise ValidationError(
                "Estoque insuficiente para finalizar venda:\n" + 
                "\n".join(erros_estoque)
            )
        
        # 6. Se validação passou, cria movimentações de SAIDA
        movimentacoes_criadas = []
        for item in itens:
            try:
                movimentacao = Movimentacao.objects.create(
                    empresa=venda.empresa,
                    produto=item.produto,
                    deposito=deposito,
                    tipo=TipoMovimentacao.SAIDA,
                    quantidade=item.quantidade,
                    valor_unitario=item.produto.preco_custo,
                    documento=f"VENDA-{venda.numero}",
                    observacao=f"Venda #{venda.numero} - Item: {item.produto.nome}",
                    usuario=usuario or 'Sistema'
                )
                movimentacoes_criadas.append(movimentacao)
            except Exception as e:
                # Se falhar, rollback automático pela transação
                raise ValidationError(
                    f"Erro ao criar movimentação para {item.produto.nome}: {str(e)}"
                )
        
        # 7. Atualiza status da venda
        venda.status = StatusVenda.FINALIZADA
        venda.data_finalizacao = timezone.now()
        venda.save(update_fields=['status', 'data_finalizacao', 'updated_at'])
        
        return venda
    
    @staticmethod
    @transaction.atomic
    def cancelar_venda(venda_id, motivo=None, usuario=None):
        """
        Cancela uma venda finalizada e devolve o estoque.
        
        REGRAS DE NEGÓCIO:
        1. Apenas vendas FINALIZADAS podem ser canceladas
        2. Buscar movimentações originais da venda
        3. Criar movimentações de ENTRADA para devolver estoque
        4. Atualizar status para CANCELADA
        5. Registrar data de cancelamento e motivo
        
        Args:
            venda_id: UUID da venda a cancelar
            motivo: Motivo do cancelamento (opcional)
            usuario: Username do usuário cancelando (para auditoria)
        
        Returns:
            Venda: Instância da venda cancelada
        
        Raises:
            ValidationError: Se venda não pode ser cancelada
        """
        # Import tardio para evitar circular import
        from stock.models import Movimentacao, TipoMovimentacao
        
        # 1. Busca venda com lock
        try:
            venda = Venda.objects.select_for_update().get(id=venda_id)
        except Venda.DoesNotExist:
            raise ValidationError(f"Venda com ID {venda_id} não encontrada")
        
        # 2. Valida se venda pode ser cancelada
        if not venda.pode_ser_cancelada:
            raise ValidationError(
                f"Venda #{venda.numero} não pode ser cancelada. "
                f"Status atual: {venda.get_status_display()}. "
                "Apenas vendas FINALIZADAS podem ser canceladas."
            )
        
        # 3. Busca movimentações de SAIDA da venda original
        movimentacoes_saida = Movimentacao.objects.filter(
            empresa=venda.empresa,
            documento=f"VENDA-{venda.numero}",
            tipo=TipoMovimentacao.SAIDA
        )
        
        if not movimentacoes_saida.exists():
            raise ValidationError(
                f"Nenhuma movimentação de estoque encontrada para venda #{venda.numero}"
            )
        
        # 4. Cria movimentações de ENTRADA para devolver estoque
        movimentacoes_devolucao = []
        for mov_saida in movimentacoes_saida:
            try:
                mov_entrada = Movimentacao.objects.create(
                    empresa=venda.empresa,
                    produto=mov_saida.produto,
                    deposito=mov_saida.deposito,
                    tipo=TipoMovimentacao.ENTRADA,
                    quantidade=mov_saida.quantidade,
                    valor_unitario=mov_saida.valor_unitario,
                    documento=f"CANCEL-VENDA-{venda.numero}",
                    observacao=(
                        f"Cancelamento da Venda #{venda.numero}. "
                        f"Motivo: {motivo or 'Não informado'}"
                    ),
                    usuario=usuario or 'Sistema'
                )
                movimentacoes_devolucao.append(mov_entrada)
            except Exception as e:
                # Rollback automático pela transação
                raise ValidationError(
                    f"Erro ao devolver estoque de {mov_saida.produto.nome}: {str(e)}"
                )
        
        # 5. Atualiza status da venda
        venda.status = StatusVenda.CANCELADA
        venda.data_cancelamento = timezone.now()
        
        # 6. Adiciona motivo às observações
        if motivo:
            observacao_cancelamento = (
                f"\n--- CANCELAMENTO ({timezone.now().strftime('%d/%m/%Y %H:%M')}) ---\n"
                f"Motivo: {motivo}\n"
                f"Usuário: {usuario or 'Sistema'}"
            )
            venda.observacoes = (venda.observacoes or '') + observacao_cancelamento
        
        venda.save(update_fields=['status', 'data_cancelamento', 'observacoes', 'updated_at'])
        
        return venda
    
    @staticmethod
    def validar_estoque_disponivel(venda_id, deposito_id):
        """
        Valida se há estoque disponível para todos os itens da venda.
        
        IMPORTANTE: Não cria transação. Use para validações prévias.
        
        Args:
            venda_id: UUID da venda
            deposito_id: UUID do depósito
        
        Returns:
            dict: {
                'disponivel': bool,
                'erros': list[str],
                'detalhes': list[dict]
            }
        """
        from stock.models import Saldo
        
        try:
            venda = Venda.objects.get(id=venda_id)
        except Venda.DoesNotExist:
            return {
                'disponivel': False,
                'erros': [f"Venda com ID {venda_id} não encontrada"],
                'detalhes': []
            }
        
        itens = venda.itens.select_related('produto').all()
        erros = []
        detalhes = []
        
        for item in itens:
            try:
                saldo = Saldo.objects.get(
                    empresa=venda.empresa,
                    produto=item.produto,
                    deposito_id=deposito_id
                )
                
                disponivel = saldo.quantidade >= item.quantidade
                
                detalhes.append({
                    'produto': item.produto.nome,
                    'necessario': float(item.quantidade),
                    'disponivel': float(saldo.quantidade),
                    'suficiente': disponivel
                })
                
                if not disponivel:
                    erros.append(
                        f"{item.produto.nome}: Necessário {item.quantidade}, "
                        f"Disponível {saldo.quantidade}"
                    )
            except Saldo.DoesNotExist:
                detalhes.append({
                    'produto': item.produto.nome,
                    'necessario': float(item.quantidade),
                    'disponivel': 0.0,
                    'suficiente': False
                })
                erros.append(f"{item.produto.nome}: Sem estoque no depósito")
        
        return {
            'disponivel': len(erros) == 0,
            'erros': erros,
            'detalhes': detalhes
        }
