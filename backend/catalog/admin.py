"""
Django Admin para app Catalog.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Categoria, Produto, GrupoComplemento, Complemento, FichaTecnicaItem, TipoProduto
from catalog.services import CatalogService
from decimal import Decimal


class FichaTecnicaItemInline(admin.TabularInline):
    """Inline para gerenciar ficha técnica dentro do produto."""
    model = FichaTecnicaItem
    extra = 1
    fields = ['componente', 'quantidade_liquida', 'custo_fixo', 'custo_calculado', 'percentual_composicao', 'observacao']
    readonly_fields = ['custo_calculado', 'percentual_composicao']
    autocomplete_fields = ['componente']
    
    def get_queryset(self, request):
        """Otimiza query com select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('componente')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'parent', 'slug', 'ordem', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['nome', 'slug']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    ordering = ['ordem', 'nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'nome', 'sku', 'categoria', 'tipo_badge', 'estoque_total', 'preco_venda', 'preco_custo_display', 'margem_display', 'is_active']
    list_filter = ['tipo', 'categoria', 'destaque', 'is_active', 'imprimir_producao']
    search_fields = ['nome', 'sku', 'codigo_barras']
    readonly_fields = ['id', 'slug', 'margem_lucro', 'lucro_unitario', 'image_preview', 'created_at', 'updated_at']
    actions = ['recalcular_custo_produtos']
    inlines = []
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'categoria', 'tipo', 'imagem', 'image_preview')
        }),
        ('Códigos', {
            'fields': ('sku', 'codigo_barras')
        }),
        ('Preços', {
            'fields': ('preco_venda', 'preco_custo', 'margem_lucro', 'lucro_unitario'),
            'description': 'Para produtos COMPOSTO, o custo é calculado automaticamente pela ficha técnica.'
        }),
        ('Descrição', {
            'fields': ('descricao_curta', 'descricao')
        }),
        ('Food Service', {
            'fields': ('setor_impressao', 'imprimir_producao'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('permite_venda_sem_estoque', 'destaque', 'is_active')
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_inlines(self, request, obj=None):
        """Adiciona inlines baseado no tipo de produto."""
        from stock.admin import LoteInline, SaldoInline
        inlines = [SaldoInline]
        
        if obj:
            if obj.tipo == TipoProduto.COMPOSTO:
                inlines.append(FichaTecnicaItemInline)
            elif obj.tipo in [TipoProduto.INSUMO, TipoProduto.FINAL]:
                inlines.append(LoteInline)
            
        return inlines

    def estoque_total(self, obj):
        """Soma o saldo de todos os depósitos."""
        from stock.models import Saldo
        from django.db.models import Sum
        total = Saldo.objects.filter(produto=obj).aggregate(total=Sum('quantidade'))['total']
        return total or 0
    estoque_total.short_description = 'Estoque'

    def image_tag(self, obj):
        """Thumbnail para a listagem."""
        if obj.imagem:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.imagem.url)
        return format_html('<div style="width: 45px; height: 45px; background: #eee; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #999; font-size: 10px;">Sem foto</div>')
    image_tag.short_description = 'Foto'

    def image_preview(self, obj):
        """Preview para o formulário de edição."""
        if obj.imagem:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.imagem.url)
        return "Nenhuma imagem carregada."
    image_preview.short_description = 'Pré-visualização'
    
    def tipo_badge(self, obj):
        """Exibe tipo com badge colorido."""
        colors = {
            TipoProduto.FINAL: '#2196F3',      # Azul
            TipoProduto.INSUMO: '#FF9800',    # Laranja
            TipoProduto.COMPOSTO: '#4CAF50',  # Verde
        }
        color = colors.get(obj.tipo, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def preco_custo_display(self, obj):
        """Exibe custo com indicador se é calculado."""
        custo = obj.preco_custo or Decimal('0.00')
        if obj.tipo == TipoProduto.COMPOSTO:
            return format_html(
                'R$ {} <span style="color: #4CAF50; font-size: 10px;">●</span>',
                format(custo, ".2f")
            )
        return f'R$ {custo:.2f}'
    preco_custo_display.short_description = 'Custo'
    preco_custo_display.admin_order_field = 'preco_custo'
    
    def margem_display(self, obj):
        """Exibe margem com cor baseada no valor."""
        try:
            margem = obj.margem_lucro
        except:
            return '-'
            
        if margem < 20:
            color = '#f44336'  # Vermelho
        elif margem < 50:
            color = '#FF9800'  # Laranja
        else:
            color = '#4CAF50'  # Verde
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            format(margem, ".1f")
        )
    margem_display.short_description = 'Margem'
    margem_display.admin_order_field = None  # Não pode ordenar por property
    
    def recalcular_custo_produtos(self, request, queryset):
        """Action para recalcular custo de produtos compostos selecionados."""
        compostos = queryset.filter(tipo=TipoProduto.COMPOSTO)
        contador = 0
        
        for produto in compostos:
            try:
                CatalogService.recalcular_custo_produto(produto)
                contador += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Erro ao recalcular {produto.nome}: {str(e)}',
                    level='error'
                )
        
        if contador > 0:
            self.message_user(
                request,
                f'{contador} produto(s) tiveram o custo recalculado com sucesso.',
                level='success'
            )
        else:
            self.message_user(
                request,
                'Nenhum produto COMPOSTO foi selecionado.',
                level='warning'
            )
    
    recalcular_custo_produtos.short_description = 'Recalcular custo de produtos compostos'


@admin.register(FichaTecnicaItem)
class FichaTecnicaItemAdmin(admin.ModelAdmin):
    """Admin para gerenciar itens de ficha técnica diretamente."""
    list_display = ['produto_pai', 'componente', 'quantidade_liquida', 'custo_calculado', 'percentual_composicao']
    list_filter = ['produto_pai__categoria']
    search_fields = ['produto_pai__nome', 'componente__nome']
    autocomplete_fields = ['produto_pai', 'componente']
    readonly_fields = ['custo_calculado', 'percentual_composicao']
    
    fieldsets = (
        (None, {
            'fields': ('produto_pai', 'componente', 'quantidade_liquida')
        }),
        ('Custos', {
            'fields': ('custo_fixo', 'custo_calculado', 'percentual_composicao'),
            'description': 'O custo é calculado automaticamente. Use "Custo Fixo" apenas para sobrescrever.'
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrupoComplemento)
class GrupoComplementoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'obrigatorio', 'min_qtd', 'max_qtd', 'ordem', 'is_active']
    list_filter = ['obrigatorio', 'is_active']
    search_fields = ['nome']
    filter_horizontal = ['produtos_vinculados']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Complemento)
class ComplementoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'grupo', 'preco_adicional', 'produto_referencia', 'is_active']
    list_filter = ['grupo', 'is_active']
    search_fields = ['nome']
    readonly_fields = ['id', 'possui_produto_vinculado', 'created_at', 'updated_at']
