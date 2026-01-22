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
    def finalizar_venda(venda_id, deposito_id, usuario=None, usar_lotes=True, gerar_conta_receber=True, tipo_pagamento=None):
        """
        Finaliza uma venda e baixa o estoque correspondente.
        
        REGRAS DE NEGÓCIO:
        1. Venda deve estar em status ORCAMENTO ou PENDENTE
        2. Verificar disponibilidade de estoque ANTES de baixar
        3. Usar StockService para baixa (suporta BOM explosion e FIFO)
        4. Atualizar status para FINALIZADA
        5. Registrar data de finalização
        6. Tudo em uma transação atômica (rollback em caso de erro)
        
        NOVO: Integração com funcionalidades avançadas:
        - Produtos COMPOSTO: Explode ficha técnica e baixa componentes
        - Produtos com lotes: Usa FIFO/FEFO automático
        - Produtos simples: Baixa direta (modo compatível)
        
        Args:
            venda_id: UUID da venda a finalizar
            deposito_id: UUID do depósito de onde sair o estoque
            usuario: Username do usuário finalizando (para auditoria)
            usar_lotes: Se True, usa controle FIFO. Se False, baixa sem lote (default: True)
            gerar_conta_receber: Se True, gera financeiro (default: True)
            tipo_pagamento: Forma de pagamento (opcional)
        
        Returns:
            Venda: Instância da venda finalizada
        
        Raises:
            ValidationError: Se venda não pode ser finalizada ou estoque insuficiente
        """
        # Import tardio para evitar circular import
        from stock.models import Deposito
        from stock.services import StockService
        from financial.services import CaixaService
        from financial.models import TipoMovimentoCaixa
        from authentication.models import CustomUser
        
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
        
        # 5. VALIDAÇÃO PRÉVIA: Usa StockService para validar estoque
        # (Funciona com explosão de BOM e lotes)
        erros_estoque = []
        for item in itens:
            resultado = StockService.validar_estoque_disponivel(
                produto=item.produto,
                deposito=deposito,
                quantidade_necessaria=item.quantidade,
                usar_lotes=usar_lotes
            )
            
            if not resultado['disponivel']:
                erros_estoque.append(
                    f"• {item.produto.nome}: Necessário {item.quantidade}, "
                    f"Disponível {resultado['quantidade_disponivel']}"
                )
        
        # Se houver erros de estoque, aborta com mensagem detalhada
        if erros_estoque:
            raise ValidationError(
                "Estoque insuficiente para finalizar venda:\n" + 
                "\n".join(erros_estoque)
            )
        
        # 6. Processa baixa de estoque usando StockService
        # (Automaticamente explode BOM e usa FIFO se aplicável)
        try:
            for item in itens:
                StockService.processar_baixa_venda(
                    item_venda=item,
                    deposito=deposito,
                    usar_lotes=usar_lotes
                )
        except Exception as e:
            # Rollback automático pela transação
            raise ValidationError(
                f"Erro ao processar baixa de estoque: {str(e)}"
            )
        
        # 7. Atualiza status da venda
        
        # Cálculo de Comissão
        # Prioridade: Atendente (User) > Colaborador (Legacy)
        if venda.atendente:
            percentual = venda.atendente.comissao_percentual
            if percentual > 0:
                venda.comissao_valor = (venda.total_liquido * percentual) / 100
        elif venda.colaborador:
            # Legacy: Partner model
            percentual = venda.colaborador.comissao_percentual
            venda.comissao_valor = (venda.total_liquido * percentual) / 100
        elif venda.vendedor and hasattr(venda.vendedor, 'role_atendente') and venda.vendedor.role_atendente:
            # Se vendedor é atendente e não foi definido atendente explícito
            venda.atendente = venda.vendedor
            percentual = venda.vendedor.comissao_percentual
            if percentual > 0:
                venda.comissao_valor = (venda.total_liquido * percentual) / 100
        
        venda.status = StatusVenda.FINALIZADA
        venda.data_finalizacao = timezone.now()
        venda.save(update_fields=['status', 'data_finalizacao', 'updated_at', 'colaborador', 'atendente', 'comissao_valor'])
        
        # 8. FATURAMENTO: Gera contas a receber automaticamente (à vista por padrão)
        if gerar_conta_receber:
            from financial.services import FinanceiroService
            FinanceiroService.gerar_conta_receber_venda(venda)
        
        # 9. CAIXA PDV: Validação e Registro
        # REGRA: Toda venda finalizada deve ter um caixa aberto pelo operador (turno).
        user_obj = None
        if usuario:
            if isinstance(usuario, CustomUser):
                user_obj = usuario
            elif isinstance(usuario, str):
                user_obj = CustomUser.objects.filter(username=usuario).first()
        
        if not user_obj:
            raise ValidationError("Usuário não identificado para validação de caixa.")

        sessao = CaixaService.get_sessao_aberta(user_obj)
        if not sessao:
            raise ValidationError("Operador não possui caixa aberto. Abra o caixa para finalizar a venda.")
            
        # Registra movimento apenas se for Dinheiro (outros entram na conciliação do fechamento)
        if tipo_pagamento == 'DINHEIRO':
            CaixaService.registrar_movimento(
                sessao=sessao,
                tipo=TipoMovimentoCaixa.VENDA,
                valor=venda.total_liquido,
                descricao=f"Venda #{venda.numero}",
                venda=venda
            )
        
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
