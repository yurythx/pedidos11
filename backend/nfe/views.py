"""
Views/ViewSets para NFe - Projeto Nix.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import ProdutoFornecedor
from .serializers import (
    ProdutoFornecedorSerializer,
    ConfirmarImportacaoNFeSerializer,
    UploadXMLSerializer
)
from .services import NFeService
from .parsers.nfe_parser import NFeParser, NFeParseError
from .matching.product_matcher import ProductMatcher


class ProdutoFornecedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar vínculos produto-fornecedor.
    
    Permite consultar, criar e editar vínculos manualmente.
    """
    serializer_class = ProdutoFornecedorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra por empresa do usuário."""
        return ProdutoFornecedor.objects.filter(
            empresa=self.request.user.empresa
        ).select_related('produto')
    
    def perform_create(self, serializer):
        """Adiciona empresa automaticamente."""
        serializer.save(empresa=self.request.user.empresa)


class ImportacaoNFeViewSet(viewsets.GenericViewSet):
    """
    ViewSet para importação de NFe.
    
    Endpoints:
    - POST /api/nfe/upload-xml/ - Upload e parse de XML
    - POST /api/nfe/confirmar/ - Confirma e efetiva importação
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='upload-xml')
    def upload_xml(self, request):
        """
        Upload e parse de arquivo XML de NFe.
        
        Extrai dados e sugere produtos automaticamente.
        
        Request:
            Content-Type: multipart/form-data
            arquivo: <arquivo.xml>
        
        Response: {
            "success": true,
            "preview": {
                "fornecedor": {"cnpj": "...", "nome": "..."},
                "numero_nfe": "12345",
                "serie_nfe": "1",
                "itens": [
                    {
                        "codigo_xml": "...",
                        "descricao_xml": "...",
                        "sugestoes_produtos": [...],
                        "produto_sugerido_id": "uuid",
                        "fator_conversao_sugerido": 12
                    }
                ]
            }
        }
        """
        # Validar arquivo
        serializer = UploadXMLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        arquivo = serializer.validated_data['arquivo']
        
        try:
            # Ler conteúdo do arquivo
            xml_content = arquivo.read()
            
            # 1. Validar XML
            validacao = NFeParser.validar_xml(xml_content)
            if not validacao['valid']:
                return Response({
                    'success': False,
                    'errors': validacao['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Parse do XML
            dados = NFeParser.parse_file(xml_content)
            
            # 3. Match produtos para cada item
            cnpj_fornecedor = dados['fornecedor']['cnpj']
            
            for item in dados['itens']:
                # Encontra sugestões
                sugestoes = ProductMatcher.find_matches(
                    empresa=request.user.empresa,
                    codigo_xml=item['codigo_xml'],
                    ean=item.get('ean'),
                    descricao=item['descricao_xml'],
                    cnpj_fornecedor=cnpj_fornecedor
                )
                
                item['sugestoes_produtos'] = sugestoes
                
                # Define sugestão principal
                if sugestoes:
                    melhor = sugestoes[0]
                    item['produto_sugerido_id'] = melhor['produto_id']
                    
                    # Usa fator do vínculo se disponível
                    if 'fator_conversao' in melhor:
                        item['fator_conversao_sugerido'] = melhor['fator_conversao']
                    else:
                        # Tenta sugerir baseado na descrição
                        fator = ProductMatcher.suggest_conversion_factor(
                            produto=None,  # Não precisa do objeto
                            unidade_xml=item['unidade_xml'],
                            descricao_xml=item['descricao_xml']
                        )
                        if fator:
                            item['fator_conversao_sugerido'] = fator
                else:
                    item['produto_sugerido_id'] = None
                    item['fator_conversao_sugerido'] = 1
            
            # 4. Retorna preview
            return Response({
                'success': True,
                'preview': {
                    'fornecedor': dados['fornecedor'],
                    **dados['identificacao'],
                    'itens': dados['itens']
                }
            }, status=status.HTTP_200_OK)
            
        except NFeParseError as e:
            return Response({
                'success': False,
                'errors': [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'errors': [f'Erro ao processar XML: {str(e)}']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='confirmar')

    def confirmar(self, request):
        """
        Confirma e efetiva a importação de uma NFe.
        
        Body: {
            "deposito_id": "uuid",
            "numero_nfe": "12345",
            "serie_nfe": "1",
            "fornecedor": {"cnpj": "12345678000199", "nome": "Fornecedor XYZ"},
            "itens": [
                {
                    "codigo_xml": "7891000",
                    "produto_id": "uuid-produto",
                    "fator_conversao": 12,
                    "qtd_xml": 2,
                    "preco_custo": 50.00,
                    "lote": {
                        "codigo": "LOTE2026",
                        "validade": "2026-12-31",
                        "fabricacao": "2026-01-15"
                    }
                }
            ]
        }
        
        Response: {
            "status": "sucesso" | "parcial" | "erro",
            "message": "...",
            "resultado": {
                "documento": "NFE-1-12345",
                "itens_processados": [...],
                "vinculos_criados": 2,
                "lotes_criados": 2,
                "erros": []
            }
        }
        """
        # Validar payload
        serializer = ConfirmarImportacaoNFeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'erro',
                'message': 'Dados inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            resultado = NFeService.efetivar_importacao_nfe(
                empresa=request.user.empresa,
                payload=serializer.validated_data,
                usuario=request.user.username
            )
            
            # Verificar se houve erros
            if resultado['erros']:
                return Response({
                    'status': 'parcial',
                    'message': (
                        f"{len(resultado['itens_processados'])} itens processados com "
                        f"{len(resultado['erros'])} erros"
                    ),
                    'resultado': resultado
                }, status=status.HTTP_207_MULTI_STATUS)
            
            return Response({
                'status': 'sucesso',
                'message': f"NFe {resultado['documento']} importada com sucesso",
                'resultado': resultado
            }, status=status.HTTP_201_CREATED)
            
        except DjangoValidationError as e:
            return Response({
                'status': 'erro',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'status': 'erro',
                'message': f"Erro interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
