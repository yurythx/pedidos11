"""
Service Layer para operações de restaurante.
Orquestra lógica de negócio de mesas, comandas e pedidos.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from restaurant.models import Mesa, Comanda, StatusMesa, StatusComanda
from sales.models import Venda, ItemVenda, ItemVendaComplemento, StatusVenda
from catalog.models import Produto, Complemento, GrupoComplemento


class RestaurantService:
    """
    Service para operações de mesas no restaurante.
    
    Responsabilidades:
    - Abrir/fechar mesas
    - Adicionar pedidos
    - Transferir mesas
    - Fechar contas
    """
    
    @staticmethod
    @transaction.atomic
    def abrir_mesa(mesa_id, garcom_user, atendente_user=None):
        """
        Abre uma mesa criando uma venda vinculada.
        
        Args:
            mesa_id: UUID da mesa
            garcom_user: Instância de CustomUser (quem abriu - logado)
            atendente_user: Instância de CustomUser (garçom responsável - opcional)
        
        Returns:
            Venda: Venda criada e vinculada à mesa
        
        Raises:
            ValidationError: Se mesa já estiver ocupada ou inválida
        """
        try:
            mesa = Mesa.objects.select_for_update().get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        # Validação: mesa deve estar livre
        if mesa.status != StatusMesa.LIVRE:
            raise ValidationError(
                f"Mesa {mesa.numero} não está livre (status: {mesa.get_status_display()})"
            )
        
        # Validação: garçom deve ser da mesma empresa
        if garcom_user.empresa != mesa.empresa:
            raise ValidationError("Garçom não pertence à mesma empresa da mesa")
        
        # Define atendente
        atendente = atendente_user
        if not atendente and hasattr(garcom_user, 'role_atendente') and garcom_user.role_atendente:
            atendente = garcom_user

        # Cria venda com status ORCAMENTO (não PENDENTE)
        venda = Venda.objects.create(
            empresa=mesa.empresa,
            vendedor=garcom_user,
            atendente=atendente,
            status=StatusVenda.ORCAMENTO,
            observacoes=f"Mesa {mesa.numero}"
        )
        
        # Vincula mesa à venda e ocupa
        mesa.ocupar(venda)
        
        return venda
    
    @staticmethod
    def _adicionar_item_venda(venda, empresa, produto_id, quantidade, complementos_list=None, observacao=''):
        """Helper para adicionar item a uma venda (usado por Mesa e Comanda)."""
        # Validação: venda não pode estar finalizada
        if venda.status not in [StatusVenda.ORCAMENTO, StatusVenda.PENDENTE]:
            raise ValidationError(
                f"Venda #{venda.numero} já está {venda.get_status_display()}. "
                "Não é possível adicionar itens."
            )
        
        # Busca produto
        try:
            produto = Produto.objects.get(
                id=produto_id,
                empresa=empresa,
                is_active=True
            )
        except Produto.DoesNotExist:
            raise ValidationError(f"Produto com ID {produto_id} não encontrado ou inativo")
        
        # Valida grupos de complementos obrigatórios
        if complementos_list:
            RestaurantService._validar_complementos_obrigatorios(
                produto, complementos_list
            )
        
        # Cria item
        item = ItemVenda.objects.create(
            empresa=empresa,
            venda=venda,
            produto=produto,
            quantidade=Decimal(str(quantidade)),
            preco_unitario=produto.preco_venda,
            observacoes=observacao
        )
        
        # Adiciona complementos
        if complementos_list:
            for comp_data in complementos_list:
                complemento_id = comp_data.get('complemento_id')
                comp_quantidade = Decimal(str(comp_data.get('quantidade', 1)))
                
                try:
                    complemento = Complemento.objects.get(
                        id=complemento_id,
                        empresa=empresa,
                        is_active=True
                    )
                except Complemento.DoesNotExist:
                    raise ValidationError(
                        f"Complemento com ID {complemento_id} não encontrado"
                    )
                
                ItemVendaComplemento.objects.create(
                    empresa=empresa,
                    item_pai=item,
                    complemento=complemento,
                    quantidade=comp_quantidade,
                    preco_unitario=complemento.preco_adicional
                )
        
        return item

    @staticmethod
    @transaction.atomic
    def adicionar_item_mesa(mesa_id, produto_id, quantidade, 
                           complementos_list=None, observacao=''):
        """
        Adiciona item ao pedido da mesa.
        """
        try:
            mesa = Mesa.objects.select_for_update().get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        # Validação: mesa deve ter venda aberta
        if not mesa.venda_atual:
            raise ValidationError(
                f"Mesa {mesa.numero} não tem venda aberta. Use 'abrir_mesa' primeiro."
            )
        
        return RestaurantService._adicionar_item_venda(
            venda=mesa.venda_atual,
            empresa=mesa.empresa,
            produto_id=produto_id,
            quantidade=quantidade,
            complementos_list=complementos_list,
            observacao=observacao
        )
    
    @staticmethod
    def _validar_complementos_obrigatorios(produto, complementos_list):
        """
        Valida se todos os grupos obrigatórios foram preenchidos.
        
        Args:
            produto: Instância de Produto
            complementos_list: Lista de complementos escolhidos
        
        Raises:
            ValidationError: Se falta complemento obrigatório
        """
        grupos_obrigatorios = produto.grupos_complementos.filter(
            obrigatorio=True,
            is_active=True
        )
        
        complementos_ids = [c.get('complemento_id') for c in complementos_list]
        complementos_escolhidos = Complemento.objects.filter(
            id__in=complementos_ids
        ).values_list('grupo_id', flat=True)
        
        for grupo in grupos_obrigatorios:
            if grupo.id not in complementos_escolhidos:
                raise ValidationError(
                    f"Grupo '{grupo.nome}' é obrigatório para o produto '{produto.nome}'"
                )
    
    @staticmethod
    @transaction.atomic
    def fechar_mesa(mesa_id, deposito_id, tipo_pagamento=None, usuario=None, valor_pago=None, colaborador_id=None, cpf_cliente=None):
        """
        Finaliza venda da mesa e baixa estoque.
        
        Args:
            mesa_id: UUID da mesa
            deposito_id: UUID do depósito para baixa de estoque
            tipo_pagamento: Tipo de pagamento (opcional, atualiza venda)
            usuario: Usuário que está fechando (para caixa)
            valor_pago: Valor pago (opcional)
            colaborador_id: ID do colaborador (garçom/atendente)
            cpf_cliente: CPF do cliente para nota
        
        Returns:
            Venda: Venda finalizada
        """
        try:
            mesa = Mesa.objects.select_for_update().get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        # ... (código existente de verificação de venda)
        
        if not mesa.venda_atual:
            raise ValidationError(f"Mesa {mesa.numero} não tem venda aberta")
        
        venda = mesa.venda_atual

        # Atualiza cliente se CPF informado
        if cpf_cliente:
            from partners.models import Cliente
            # Remove pontuação
            cpf_limpo = ''.join(filter(str.isdigit, cpf_cliente))
            
            if cpf_limpo:
                cliente = Cliente.objects.filter(cpf_cnpj=cpf_limpo, empresa=mesa.empresa).first()
                if not cliente:
                    cliente = Cliente.objects.create(
                        empresa=mesa.empresa,
                        nome=f"Consumidor {cpf_limpo}",
                        cpf_cnpj=cpf_limpo,
                        tipo_pessoa='FISICA'
                    )
                venda.cliente = cliente
                venda.save(update_fields=['cliente'])
        
        # Define colaborador se informado (sobreescreve ou define atendente)
        if colaborador_id:
            try:
                from authentication.models import CustomUser
                colaborador = CustomUser.objects.get(id=colaborador_id, empresa=mesa.empresa)
                venda.atendente = colaborador
                venda.save(update_fields=['atendente'])
            except CustomUser.DoesNotExist:
                pass # Ignora se não achar
        
        # Atualiza tipo de pagamento se fornecido
        if tipo_pagamento:
            venda.tipo_pagamento = tipo_pagamento
            venda.save(update_fields=['tipo_pagamento'])
        
        # Validação: venda deve ter itens
        if not venda.itens.exists():
            # Se não tem itens, cancela a ocupação e libera a mesa
            venda.status = StatusVenda.CANCELADA
            venda.observacoes = (venda.observacoes or "") + " | Cancelada: Sem consumo"
            venda.save()
            
            mesa.status = StatusMesa.LIVRE
            mesa.venda_atual = None
            mesa.save()
            
            return venda
        
        # Usa VendaService para finalizar (baixa estoque, atualiza status)
        from sales.services import VendaService
        from django.conf import settings
        
        # Lê configuração de lotes (padrão True se não definido)
        usar_lotes = getattr(settings, 'ESTOQUE_USAR_LOTES', True)
        
        venda_finalizada = VendaService.finalizar_venda(
            venda_id=venda.id,
            deposito_id=deposito_id,
            usuario=usuario or 'sistema', # Passa usuário
            usar_lotes=usar_lotes,
            tipo_pagamento=tipo_pagamento,
            valor_pago=valor_pago
        )
        
        # Libera mesa (suja para limpeza)
        mesa.status = StatusMesa.SUJA
        mesa.venda_atual = None
        mesa.save()
        
        return venda_finalizada
    
    @staticmethod
    @transaction.atomic
    def liberar_mesa(mesa_id):
        """
        Libera mesa após limpeza.
        
        Args:
            mesa_id: UUID da mesa
        """
        try:
            mesa = Mesa.objects.get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        if mesa.status != StatusMesa.SUJA:
            # Permite liberar mesa OCUPADA se não tiver itens (cancelamento implícito)
            eh_cancelamento = (
                mesa.status == StatusMesa.OCUPADA and 
                mesa.venda_atual and 
                not mesa.venda_atual.itens.exists()
            )
            
            if not eh_cancelamento:
                raise ValidationError(
                    f"Apenas mesas SUJAS podem ser liberadas (status atual: {mesa.get_status_display()})"
                )
        
        # Se for cancelamento de mesa ocupada, cancela a venda também
        if mesa.status == StatusMesa.OCUPADA and mesa.venda_atual:
            venda = mesa.venda_atual
            venda.status = StatusVenda.CANCELADA
            venda.observacoes = (venda.observacoes or "") + " | Liberada manualmente sem consumo"
            venda.save()
            mesa.venda_atual = None
        
        mesa.liberar()
    
    @staticmethod
    @transaction.atomic
    def transferir_mesa(mesa_origem_id, mesa_destino_id):
        """
        Transfere venda de uma mesa para outra.
        
        Args:
            mesa_origem_id: UUID da mesa de origem
            mesa_destino_id: UUID da mesa de destino
        
        Returns:
            tuple: (mesa_origem, mesa_destino)
        
        Raises:
            ValidationError: Se mesas inválidas
        """
        try:
            mesa_origem = Mesa.objects.select_for_update().get(id=mesa_origem_id)
            mesa_destino = Mesa.objects.select_for_update().get(id=mesa_destino_id)
        except Mesa.DoesNotExist:
            raise ValidationError("Uma das mesas não foi encontrada")
        
        # Validações
        if not mesa_origem.venda_atual:
            raise ValidationError(f"Mesa {mesa_origem.numero} não tem venda aberta")
        
        if not mesa_destino.esta_livre:
            raise ValidationError(
                f"Mesa {mesa_destino.numero} não está livre ({mesa_destino.get_status_display()})"
            )
        
        # Transfere
        venda = mesa_origem.venda_atual
        mesa_origem.liberar()
        mesa_destino.ocupar(venda)
        
        # Atualiza observações
        venda.observacoes = f"Mesa {mesa_destino.numero} (transferida da {mesa_origem.numero})"
        venda.save(update_fields=['observacoes'])
        
        return (mesa_origem, mesa_destino)
    
    @staticmethod
    @transaction.atomic
    def remover_item_mesa(mesa_id, item_id):
        """
        Remove item da venda da mesa (cancelamento).
        
        Args:
            mesa_id: UUID da mesa
            item_id: UUID do item a remover
        """
        try:
            mesa = Mesa.objects.get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
            
        if not mesa.venda_atual:
            raise ValidationError("Mesa não tem venda aberta")
            
        try:
            item = ItemVenda.objects.get(id=item_id, venda=mesa.venda_atual)
        except ItemVenda.DoesNotExist:
             raise ValidationError("Item não encontrado nesta venda")
             
        # Só permite remover se venda estiver aberta (ORCAMENTO)
        if mesa.venda_atual.status != StatusVenda.ORCAMENTO:
            raise ValidationError("Não é possível remover itens de uma venda fechada/finalizada")

        item.delete()

    @staticmethod
    def obter_resumo_conta(mesa_id):
        """
        Retorna resumo da conta da mesa.
        
        Args:
            mesa_id: UUID da mesa
        
        Returns:
            dict: Resumo com total, itens, etc.
        """
        try:
            mesa = Mesa.objects.get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        if not mesa.venda_atual:
            return {
                'mesa': mesa.numero,
                'status': 'sem_venda',
                'total': Decimal('0.00'),
                'itens': []
            }
        
        venda = mesa.venda_atual
        
        return {
            'mesa': mesa.numero,
            'venda_numero': venda.numero,
            'status': venda.status,
            'total_bruto': venda.total_bruto,
            'total_desconto': venda.total_desconto,
            'total_liquido': venda.total_liquido,
            'quantidade_itens': venda.quantidade_itens,
            'itens': [
                {
                    'id': str(item.id),
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'preco_unitario': item.preco_unitario,
                    'complementos': [
                        {
                            'nome': comp.complemento.nome,
                            'quantidade': comp.quantidade,
                            'preco': comp.preco_unitario
                        }
                        for comp in item.complementos.all()
                    ],
                    'subtotal': item.subtotal
                }
                for item in venda.itens.all()
            ]
        }


class ComandaService:
    """
    Service para operações com comandas.
    Similar ao MesaService mas para comandas individuais.
    """
    
    @staticmethod
    @transaction.atomic
    def abrir_comanda(comanda_id, garcom_user, atendente_user=None):
        """Abre comanda (mesmo padrão de abrir_mesa)."""
        try:
            comanda = Comanda.objects.select_for_update().get(id=comanda_id)
        except Comanda.DoesNotExist:
            raise ValidationError(f"Comanda com ID {comanda_id} não encontrada")
        
        if comanda.status != StatusComanda.LIVRE:
            raise ValidationError(
                f"Comanda {comanda.codigo} não está livre ({comanda.get_status_display()})"
            )
        
        if garcom_user.empresa != comanda.empresa:
            raise ValidationError("Garçom não pertence à mesma empresa")
        
        # Define atendente
        atendente = atendente_user
        if not atendente and hasattr(garcom_user, 'role_atendente') and garcom_user.role_atendente:
            atendente = garcom_user

        venda = Venda.objects.create(
            empresa=comanda.empresa,
            vendedor=garcom_user,
            atendente=atendente,
            status=StatusVenda.ORCAMENTO,
            observacoes=f"Comanda {comanda.codigo}"
        )
        
        comanda.usar(venda)
        
        return venda
    
    @staticmethod
    @transaction.atomic
    def adicionar_item_comanda(comanda_id, produto_id, quantidade,
                              complementos_list=None, observacao=''):
        """Adiciona item à comanda (reutiliza lógica de mesa)."""
        try:
            comanda = Comanda.objects.select_for_update().get(id=comanda_id)
        except Comanda.DoesNotExist:
            raise ValidationError(f"Comanda com ID {comanda_id} não encontrada")
        
        if not comanda.venda_atual:
            raise ValidationError(
                f"Comanda {comanda.codigo} não tem venda aberta"
            )
        
        # Reutiliza lógica similar (adaptar para comanda)
        # Por simplicidade, vou criar um método auxiliar comum
        return RestaurantService._adicionar_item_venda(
            venda=comanda.venda_atual,
            empresa=comanda.empresa,
            produto_id=produto_id,
            quantidade=quantidade,
            complementos_list=complementos_list,
            observacao=observacao
        )
    
    @staticmethod
    @transaction.atomic
    def fechar_comanda(comanda_id, deposito_id, tipo_pagamento=None, usuario=None, valor_pago=None, colaborador_id=None, cpf_cliente=None):
        """Fecha comanda e finaliza venda."""
        try:
            comanda = Comanda.objects.select_for_update().get(id=comanda_id)
        except Comanda.DoesNotExist:
            raise ValidationError(f"Comanda com ID {comanda_id} não encontrada")
        
        if not comanda.venda_atual:
            raise ValidationError(f"Comanda {comanda.codigo} não tem venda aberta")
        
        venda = comanda.venda_atual
        
        # Atualiza cliente se CPF informado
        if cpf_cliente:
            from partners.models import Cliente
            cpf_limpo = ''.join(filter(str.isdigit, cpf_cliente))
            if cpf_limpo:
                cliente = Cliente.objects.filter(cpf_cnpj=cpf_limpo, empresa=comanda.empresa).first()
                if not cliente:
                    cliente = Cliente.objects.create(
                        empresa=comanda.empresa,
                        nome=f"Consumidor {cpf_limpo}",
                        cpf_cnpj=cpf_limpo,
                        tipo_pessoa='FISICA'
                    )
                venda.cliente = cliente
                venda.save(update_fields=['cliente'])
        
        # Define colaborador
        if colaborador_id:
            try:
                from authentication.models import CustomUser
                colaborador = CustomUser.objects.get(id=colaborador_id, empresa=comanda.empresa)
                venda.atendente = colaborador
                venda.save(update_fields=['atendente'])
            except CustomUser.DoesNotExist:
                pass

        if not venda.itens.exists():
            raise ValidationError("Venda não tem itens")
        
        from sales.services import VendaService
        venda_finalizada = VendaService.finalizar_venda(
            venda_id=venda.id,
            deposito_id=deposito_id,
            usuario=usuario or 'sistema',
            tipo_pagamento=tipo_pagamento,
            valor_pago=valor_pago
        )
        
        comanda.liberar()
        
        return venda_finalizada

    @staticmethod
    @transaction.atomic
    def remover_item_comanda(comanda_id, item_id):
        """Remove item da comanda."""
        try:
            comanda = Comanda.objects.get(id=comanda_id)
        except Comanda.DoesNotExist:
            raise ValidationError(f"Comanda {comanda_id} não encontrada")
            
        if not comanda.venda_atual:
            raise ValidationError("Comanda não tem venda aberta")
            
        try:
            item = ItemVenda.objects.get(id=item_id, venda=comanda.venda_atual)
        except ItemVenda.DoesNotExist:
             raise ValidationError("Item não encontrado")
             
        if comanda.venda_atual.status != StatusVenda.ORCAMENTO:
            raise ValidationError("Venda fechada")

        item.delete()
