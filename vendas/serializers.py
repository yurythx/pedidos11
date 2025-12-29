from decimal import Decimal
from typing import List, Dict
from django.db import transaction
from rest_framework import serializers
from .models import Categoria, Produto, Pedido, ItemPedido
from .models import ProdutoImagem
from .models import ProdutoAtributo, ProdutoAtributoValor, ProdutoVariacao
from .services import PedidoService, ProdutoService
from estoque.services import EstoqueService
from financeiro.services import FinanceiroService
from financeiro.models import CostCenter, UserDefaultCostCenter
from auditoria.utils import log_action, ensure_idempotency, payload_hash
from django.utils import timezone


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nome', 'slug']
        read_only_fields = ['slug']


class ProdutoSerializer(serializers.ModelSerializer):
    categoria = serializers.SlugRelatedField(slug_field='slug', queryset=Categoria.objects.all())
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    sku = serializers.CharField(required=False, allow_blank=True)
    ean = serializers.CharField(required=False, allow_blank=True)
    unidade = serializers.ChoiceField(choices=[('UN','Unidade'),('CX','Caixa'),('KG','Kilograma'),('LT','Litro')], required=False)
    marca = serializers.CharField(required=False, allow_blank=True)
    ncm = serializers.CharField(required=False, allow_blank=True)
    cfop = serializers.CharField(required=False, allow_blank=True)
    atributos = serializers.JSONField(required=False)

    class Meta:
        model = Produto
        fields = ['nome', 'slug', 'sku', 'ean', 'unidade', 'marca', 'ncm', 'cfop', 'atributos', 'categoria', 'categoria_nome', 'preco', 'custo', 'descricao', 'imagem', 'disponivel']
        read_only_fields = ['slug']

    def validate_preco(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("Preço não pode ser negativo.")
        return value

    def validate_custo(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("Custo não pode ser negativo.")
        return value

    def validate_ean(self, value: str) -> str:
        if value and not value.isdigit():
            raise serializers.ValidationError("EAN deve conter apenas dígitos.")
        if value and not (8 <= len(value) <= 14):
            raise serializers.ValidationError("EAN deve ter entre 8 e 14 dígitos.")
        return value

    def validate_ncm(self, value: str) -> str:
        if value and (not value.isdigit() or len(value) != 8):
            raise serializers.ValidationError("NCM deve ter 8 dígitos numéricos.")
        return value

    def validate_cfop(self, value: str) -> str:
        if value and (not value.isdigit() or len(value) != 4):
            raise serializers.ValidationError("CFOP deve ter 4 dígitos numéricos.")
        return value


class ItemPedidoReadSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_slug = serializers.CharField(source='produto.slug', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['produto_nome', 'produto_slug', 'quantidade', 'preco_unitario']


class ProdutoImagemSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())

    class Meta:
        model = ProdutoImagem
        fields = ['id', 'produto', 'imagem', 'alt', 'pos', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class ProdutoAtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoAtributo
        fields = ['id', 'codigo', 'nome', 'tipo', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class ProdutoAtributoValorSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())
    atributo = serializers.SlugRelatedField(slug_field='codigo', queryset=ProdutoAtributo.objects.all())

    class Meta:
        model = ProdutoAtributoValor
        fields = ['id', 'produto', 'atributo', 'valor_texto', 'valor_numero', 'valor_bool', 'criado_em']
        read_only_fields = ['id', 'criado_em']

    def validate(self, attrs):
        atributo = attrs.get('atributo')
        vt, vn, vb = attrs.get('valor_texto'), attrs.get('valor_numero'), attrs.get('valor_bool')
        if atributo.tipo == ProdutoAtributo.Tipo.TEXTO and not vt:
            raise serializers.ValidationError("Valor texto é obrigatório para atributo de texto.")
        if atributo.tipo == ProdutoAtributo.Tipo.NUMERO and vn is None:
            raise serializers.ValidationError("Valor numérico é obrigatório para atributo numérico.")
        if atributo.tipo == ProdutoAtributo.Tipo.BOOLEANO and vb is None:
            raise serializers.ValidationError("Valor booleano é obrigatório para atributo booleano.")
        return attrs


class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    produto = serializers.SlugRelatedField(slug_field='slug', queryset=Produto.objects.all())

    class Meta:
        model = ProdutoVariacao
        fields = ['id', 'produto', 'sku', 'nome', 'preco', 'custo', 'disponivel', 'atributos', 'imagem', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoReadSerializer(many=True, read_only=True)
    cost_center = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cost_center_codigo = serializers.CharField(source='cost_center.codigo', read_only=True)
    cost_center_nome = serializers.CharField(source='cost_center.nome', read_only=True)

    # payload de criação: [{"produto": <slug>, "quantidade": <int>}, ...]
    itens_payload = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Pedido
        fields = ['slug', 'usuario', 'status', 'total', 'data_criacao', 'itens', 'itens_payload', 'cost_center', 'cost_center_codigo', 'cost_center_nome']
        read_only_fields = ['slug', 'usuario', 'total', 'data_criacao', 'status']

    def validate_itens_payload(self, value: List[Dict]) -> List[Dict]:
        if not value:
            raise serializers.ValidationError("Itens do pedido são obrigatórios.")
        normalized = []
        seen = set()
        for item in value:
            produto_slug = item.get('produto')
            quantidade = item.get('quantidade')
            if not produto_slug or not isinstance(quantidade, int) or quantidade <= 0:
                raise serializers.ValidationError("Cada item deve conter 'produto' (slug) e 'quantidade' (>0).")
            if produto_slug in seen:
                raise serializers.ValidationError("Itens duplicados para o mesmo produto não são permitidos.")
            seen.add(produto_slug)
            normalized.append({'produto': produto_slug, 'quantidade': quantidade})
        PedidoService.validate_disponibilidade(normalized)
        return normalized

    def create(self, validated_data):
        request = self.context.get('request')
        usuario = request.user if request and request.user and request.user.is_authenticated else None
        if not usuario:
            raise serializers.ValidationError("Usuário não autenticado.")

        itens_payload = validated_data.pop('itens_payload')
        cost_center_code = validated_data.pop('cost_center', None)
        key = request.headers.get('Idempotency-Key') if request else None
        idem, created = ensure_idempotency(key, usuario, 'pedido/create', {'itens': itens_payload, 'cost_center': cost_center_code})
        if idem and not created:
            since = timezone.now() - timezone.timedelta(minutes=10)
            last = Pedido.objects.filter(usuario=usuario, data_criacao__gte=since).order_by('-data_criacao').first()
            if last:
                items = list(ItemPedido.objects.filter(pedido=last).values_list('produto__slug', 'quantidade'))
                expected = sorted([(i['produto'], i['quantidade']) for i in itens_payload])
                if sorted(items) == expected:
                    return last

        with transaction.atomic():
            EstoqueService.verificar_disponibilidade(itens_payload)
            pedido = Pedido.objects.create(usuario=usuario)
            itens_objs: List[ItemPedido] = PedidoService.criar_itens(pedido, itens_payload)
            total = PedidoService.calcular_total(itens_objs)
            pedido.total = total
            if cost_center_code:
                cc = CostCenter.objects.filter(codigo=cost_center_code).first()
                if not cc:
                    raise serializers.ValidationError("Centro de custo inválido.")
                pedido.cost_center = cc
            else:
                mapping = UserDefaultCostCenter.objects.filter(user=usuario).first()
                if mapping:
                    pedido.cost_center = mapping.cost_center
            pedido.save(update_fields=['total', 'cost_center'] if cost_center_code else ['total'])
            EstoqueService.registrar_saida(pedido, itens_objs)
            FinanceiroService.registrar_receita_venda(pedido, cost_center_code=cost_center_code)
            FinanceiroService.registrar_custo_venda(pedido, cost_center_code=cost_center_code)
            log_action(usuario, 'create', 'Pedido', pedido.slug, {'total': str(total), 'itens_count': len(itens_objs), 'cost_center': pedido.cost_center.codigo if pedido.cost_center else None})
        return pedido
