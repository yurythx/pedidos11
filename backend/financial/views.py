from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal

from .models import ContaReceber, ContaPagar, Caixa, SessaoCaixa, MovimentoCaixa
from api.serializers.financial import (
    ContaReceberSerializer, ContaPagarSerializer,
    CaixaSerializer, SessaoCaixaSerializer, MovimentoCaixaSerializer
)
from .services import CaixaService

class ContaReceberViewSet(viewsets.ModelViewSet):
    queryset = ContaReceber.objects.all()
    serializer_class = ContaReceberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContaReceber.objects.filter(empresa=self.request.user.empresa)

class ContaPagarViewSet(viewsets.ModelViewSet):
    queryset = ContaPagar.objects.all()
    serializer_class = ContaPagarSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContaPagar.objects.filter(empresa=self.request.user.empresa)

class CaixaViewSet(viewsets.ModelViewSet):
    queryset = Caixa.objects.all()
    serializer_class = CaixaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self):
        return Caixa.objects.filter(empresa=self.request.user.empresa)

class SessaoCaixaViewSet(viewsets.ModelViewSet):
    queryset = SessaoCaixa.objects.all()
    serializer_class = SessaoCaixaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SessaoCaixa.objects.filter(empresa=self.request.user.empresa)

    @action(detail=True, methods=['get'])
    def resumo(self, request, pk=None):
        """Retorna resumo financeiro da sessão."""
        sessao = self.get_object()
        try:
            dados = CaixaService.obter_resumo(sessao)
            return Response(dados)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def aberta(self, request):
        """Retorna a sessão aberta do usuário atual."""
        sessao = CaixaService.get_sessao_aberta(request.user)
        if not sessao:
            return Response(None, status=status.HTTP_200_OK)
        return Response(self.get_serializer(sessao).data)

    @action(detail=False, methods=['post'])
    def abrir(self, request):
        """Abre uma nova sessão."""
        caixa_id = request.data.get('caixa_id')
        saldo_inicial = request.data.get('saldo_inicial', 0)
        
        try:
            sessao = CaixaService.abrir_caixa(
                caixa_id=caixa_id,
                usuario=request.user,
                saldo_inicial=Decimal(str(saldo_inicial))
            )
            return Response(self.get_serializer(sessao).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        """Fecha a sessão."""
        saldo_final = request.data.get('saldo_final')
        if saldo_final is None:
             return Response({'error': 'saldo_final é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sessao = CaixaService.fechar_caixa(
                sessao_id=pk,
                saldo_informado=Decimal(str(saldo_final))
            )
            return Response(self.get_serializer(sessao).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def movimentar(self, request, pk=None):
        """Registra suprimento ou sangria."""
        tipo = request.data.get('tipo') # SUPRIMENTO ou SANGRIA
        valor = request.data.get('valor')
        descricao = request.data.get('descricao', '')
        
        if not tipo or not valor:
            return Response({'error': 'tipo e valor são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sessao = self.get_object()
            CaixaService.registrar_movimento(
                sessao=sessao,
                tipo=tipo,
                valor=Decimal(str(valor)),
                descricao=descricao
            )
            return Response({'status': 'ok', 'message': 'Movimento registrado'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
