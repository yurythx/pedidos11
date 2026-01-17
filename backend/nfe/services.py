"""
Service Layer para importação de NFe - Projeto Nix.
"""
import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

from catalog.models import Produto, TipoProduto
from partners.models import Fornecedor
from stock.models import Deposito, Movimentacao, TipoMovimentacao
from stock.services import StockService
from .models import ProdutoFornecedor


class NFeService:
    """
    Service responsável por processar importação de NFe.
    
    Implementa lógica robusta de:
    - Validação de dados
    - Criação de vínculos produto-fornecedor
    - Integração com StockService (lotes + FIFO)
    - Idempotência (evita duplicação)
    - Tratamento de erros parciais
    """
    
    @staticmethod
    @transaction.atomic
    def efetivar_importacao_nfe(empresa, payload, usuario):
        """
        Efetiva importação de NFe criando vínculos, lotes e movimentações.
        
        Args:
            empresa: Empresa do usuário
            payload: Dict com estrutura da NFe
            usuario: Username para auditoria
            
        Returns:
            Dict com resumo da importação
            
        Raises:
            ValidationError: Se dados inválidos
            
        Payload Format:
            {
                "deposito_id": "uuid",
                "numero_nfe": "12345",
                "serie_nfe": "1",
                "fornecedor": {"cnpj": "...", "nome": "..."},
                "itens": [
                    {
                        "codigo_xml": "7891000",
                        "produto_id": "uuid",
                        "fator_conversao": 12,
                        "qtd_xml": 2,
                        "preco_custo": 50.00,
                        "lote": {"codigo": "LOT2026", "validade": "2026-12-31"}
                    }
                ]
            }
        """
        # 1. Validar e buscar depósito
        deposito_id = payload.get('deposito_id')
        if not deposito_id:
            raise ValidationError("deposito_id é obrigatório")
        
        try:
            deposito = Deposito.objects.get(
                id=deposito_id,
                empresa=empresa
            )
        except Deposito.DoesNotExist:
            raise ValidationError(f"Depósito {deposito_id} não encontrado")
        
        # 2. Dados do fornecedor
        fornecedor_data = payload.get('fornecedor', {})
        cnpj_fornecedor = fornecedor_data.get('cnpj')
        nome_fornecedor = fornecedor_data.get('nome', 'Não informado')
        
        if not cnpj_fornecedor:
            raise ValidationError("CNPJ do fornecedor é obrigatório")
        
        # 3. Criar/Atualizar Fornecedor
        fornecedor, _ = Fornecedor.objects.get_or_create(
            empresa=empresa,
            cpf_cnpj=cnpj_fornecedor,
            defaults={
                'razao_social': nome_fornecedor,
                'tipo': 'JURIDICA'
            }
        )
        
        # 4. Metadados da NF
        numero_nfe = payload.get('numero_nfe')
        serie_nfe = payload.get('serie_nfe', '1')
        documento = f"NFE-{serie_nfe}-{numero_nfe}" if numero_nfe else f"NFE-{uuid.uuid4()}"
        
        # 5. Verificar idempotência
        if numero_nfe:
            movs_existentes = Movimentacao.objects.filter(
                empresa=empresa,
                documento=documento,
                tipo=TipoMovimentacao.ENTRADA
            )
            if movs_existentes.exists():
                raise ValidationError(
                    f"NFe {documento} já foi importada. "
                    f"Total de {movs_existentes.count()} itens já processados."
                )
        
        # 6. Processar itens
        itens = payload.get('itens', [])
        if not itens:
            raise ValidationError("Nenhum item para importar")
        
        resultado = {
            'documento': documento,
            'itens_processados': [],
            'vinculos_criados': 0,
            'lotes_criados': 0,
            'erros': []
        }
        
        for idx, item in enumerate(itens, 1):
            try:
                item_resultado = NFeService._processar_item_nfe(
                    empresa=empresa,
                    deposito=deposito,
                    fornecedor=fornecedor,
                    cnpj_fornecedor=cnpj_fornecedor,
                    nome_fornecedor=nome_fornecedor,
                    item_data=item,
                    documento=documento,
                    usuario=usuario
                )
                resultado['itens_processados'].append(item_resultado)
                
                if item_resultado.get('vinculo_criado'):
                    resultado['vinculos_criados'] += 1
                if item_resultado.get('lote_criado'):
                    resultado['lotes_criados'] += 1
                    
            except Exception as e:
                erro = {
                    'item_numero': idx,
                    'codigo_xml': item.get('codigo_xml'),
                    'erro': str(e)
                }
                resultado['erros'].append(erro)
                # Continua processando outros itens
        
        return resultado
    
    @staticmethod
    def _processar_item_nfe(empresa, deposito, fornecedor, cnpj_fornecedor, 
                           nome_fornecedor, item_data, documento, usuario):
        """Processa um item individual da NFe."""
        
        # Extrair dados
        produto_id = item_data.get('produto_id')
        codigo_xml = item_data.get('codigo_xml')
        fator_conversao = Decimal(str(item_data.get('fator_conversao', 1)))
        qtd_xml = Decimal(str(item_data.get('qtd_xml', 0)))
        preco_custo = Decimal(str(item_data.get('preco_custo', 0)))
        lote_data = item_data.get('lote', {})
        
        # Validações
        if not produto_id:
            raise ValidationError(
                f"Item {codigo_xml}: produto_id não informado"
            )
        
        if fator_conversao <= 0:
            raise ValidationError(
                f"Item {codigo_xml}: fator_conversao deve ser > 0"
            )
        
        if qtd_xml <= 0:
            raise ValidationError(
                f"Item {codigo_xml}: qtd_xml deve ser > 0"
            )
        
        # Buscar produto
        try:
            produto = Produto.objects.get(
                id=produto_id,
                empresa=empresa
            )
        except Produto.DoesNotExist:
            raise ValidationError(
                f"Produto {produto_id} não encontrado ou não pertence à empresa"
            )
        
        if not produto.is_active:
            raise ValidationError(
                f"Produto {produto.nome} está inativo"
            )
        
        # Atualizar custo se for INSUMO e propagar para fichas técnicas
        if produto.tipo == TipoProduto.INSUMO and preco_custo > 0 and preco_custo != produto.preco_custo:
            produto.preco_custo = preco_custo
            produto.save(update_fields=['preco_custo', 'updated_at'])
            
            # Gatilho: Recalcular custo de todos os produtos que utilizam este insumo
            from catalog.services import CatalogService
            CatalogService.propagar_custo_insumo(produto)
        
        # Salvar vínculo ProdutoFornecedor
        vinculo, criado = ProdutoFornecedor.objects.update_or_create(
            empresa=empresa,
            produto=produto,
            cnpj_fornecedor=cnpj_fornecedor,
            codigo_no_fornecedor=codigo_xml,
            defaults={
                'nome_fornecedor': nome_fornecedor,
                'fator_conversao': fator_conversao,
                'ultimo_preco': preco_custo
            }
        )
        
        # Calcular quantidade real
        quantidade_real = qtd_xml * fator_conversao
        
        # Processar entrada com lote
        lote, movimentacao = StockService.dar_entrada_com_lote(
            produto=produto,
            deposito=deposito,
            quantidade=quantidade_real,
            codigo_lote=lote_data.get('codigo', f'LOTE-{uuid.uuid4().hex[:8].upper()}'),
            data_validade=lote_data.get('validade'),
            data_fabricacao=lote_data.get('fabricacao'),
            valor_unitario=preco_custo,
            documento=documento,
            observacao=f"NFe - {codigo_xml} - Fator: {fator_conversao}x"
        )
        
        return {
            'produto_id': str(produto.id),
            'produto_nome': produto.nome,
            'quantidade_xml': float(qtd_xml),
            'fator_conversao': float(fator_conversao),
            'quantidade_real': float(quantidade_real),
            'lote_id': str(lote.id),
            'lote_codigo': lote.codigo_lote,
            'lote_criado': movimentacao.id is not None,
            'vinculo_criado': criado,
            'movimentacao_id': str(movimentacao.id)
        }
