from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuração do painel administrativo para o usuário customizado.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'empresa', 'cargo', 'is_staff', 'is_active')
    list_filter = ('empresa', 'cargo', 'is_staff', 'is_superuser', 'is_active', 'is_colaborador', 'role_atendente', 'role_caixa')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'empresa__nome_fantasia')
    ordering = ('username',)
    
    # Adicionando campos customizados ao formulário do Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Informações de Empresa (Nix Food)', {
            'fields': ('empresa', 'cargo', 'telefone', 'foto_perfil')
        }),
        ('Permissões e Funções (Operacional)', {
            'fields': ('is_colaborador', 'role_atendente', 'role_caixa', 'comissao_percentual')
        }),
        ('Notificações', {
            'fields': ('receber_notificacoes_email',)
        }),
    )
    
    # Adicionando campos ao formulário de criação de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações de Empresa (Nix Food)', {
            'fields': ('empresa', 'cargo', 'is_colaborador', 'role_atendente', 'role_caixa')
        }),
    )
