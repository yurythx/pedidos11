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
    def abrir_mesa(mesa_id, garcom_user):
        """
        Abre uma mesa criando uma venda vinculada.
        
        Args:
            mesa_id: UUID da mesa
            garcom_user: Instância de CustomUser (garçom)
        
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
        
        # Cria venda com status ORCAMENTO (não PENDENTE)
        venda = Venda.objects.create(
            empresa=mesa.empresa,
            vendedor=garcom_user,
            status=StatusVenda.ORCAMENTO,
            observacoes=f"Mesa {mesa.numero}"
        )
        
        # Vincula mesa à venda e ocupa
        mesa.ocupar(venda)
        
        return venda
    
    @staticmethod
    @transaction.atomic
    def adicionar_item_mesa(mesa_id, produto_id, quantidade, 
                           complementos_list=None, observacao=''):
        """
        Adiciona item ao pedido da mesa.
        
        Args:
            mesa_id: UUID da mesa
            produto_id: UUID do produto
            quantidade: Quantidade (Decimal)
            complementos_list: Lista de dicts [{'complemento_id': uuid, 'quantidade': 1}, ...]
            observacao: Observações do item (ex: "sem cebola")
        
        Returns:
            ItemVenda: Item criado com complementos
        
        Raises:
            ValidationError: Se mesa não tiver venda aberta, produto inválido, etc.
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
        
        venda = mesa.venda_atual
        
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
                empresa=mesa.empresa,
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
            empresa=mesa.empresa,
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
                        empresa=mesa.empresa,
                        is_active=True
                    )
                except Complemento.DoesNotExist:
                    # Rollback automático por @transaction.atomic
                    raise ValidationError(
                        f"Complemento com ID {complemento_id} não encontrado"
                    )
                
                ItemVendaComplemento.objects.create(
                    empresa=mesa.empresa,
                    item_pai=item,
                    complemento=complemento,
                    quantidade=comp_quantidade,
                    preco_unitario=complemento.preco_adicional
                )
        
        return item
    
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
    def fechar_mesa(mesa_id, deposito_id):
        """
        Finaliza venda da mesa e baixa estoque.
        
        Args:
            mesa_id: UUID da mesa
            deposito_id: UUID do depósito para baixa de estoque
        
        Returns:
            Venda: Venda finalizada
        
        Raises:
            ValidationError: Se mesa não tiver venda ou venda vazia
        """
        try:
            mesa = Mesa.objects.select_for_update().get(id=mesa_id)
        except Mesa.DoesNotExist:
            raise ValidationError(f"Mesa com ID {mesa_id} não encontrada")
        
        if not mesa.venda_atual:
            raise ValidationError(f"Mesa {mesa.numero} não tem venda aberta")
        
        venda = mesa.venda_atual
        
        # Validação: venda deve ter itens
        if not venda.itens.exists():
            raise ValidationError(
                f"Venda #{venda.numero} não tem itens. Não é possível finalizar."
            )
        
        # Usa VendaService para finalizar (baixa estoque, atualiza status)
        from sales.services import VendaService
        venda_finalizada = VendaService.finalizar_venda(
            venda_id=venda.id,
            deposito_id=deposito_id,
            usuario='sistema'
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
            raise ValidationError(
                f"Apenas mesas SUJAS podem ser liberadas (status atual: {mesa.get_status_display()})"
            )
        
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
    def abrir_comanda(comanda_id, garcom_user):
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
        
        venda = Venda.objects.create(
            empresa=comanda.empresa,
            vendedor=garcom_user,
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
    def fechar_comanda(comanda_id, deposito_id):
        """Fecha comanda e finaliza venda."""
        try:
            comanda = Comanda.objects.select_for_update().get(id=comanda_id)
        except Comanda.DoesNotExist:
            raise ValidationError(f"Comanda com ID {comanda_id} não encontrada")
        
        if not comanda.venda_atual:
            raise ValidationError(f"Comanda {comanda.codigo} não tem venda aberta")
        
        venda = comanda.venda_atual
        
        if not venda.itens.exists():
            raise ValidationError("Venda não tem itens")
        
        from sales.services import VendaService
        venda_finalizada = VendaService.finalizar_venda(
            venda_id=venda.id,
            deposito_id=deposito_id,
            usuario='sistema'
        )
        
        comanda.liberar()
        
        return venda_finalizada
