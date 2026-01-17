"""
Models abstratos e base para o Projeto Nix.
Define a estrutura fundamental para multi-tenancy e auditing.
"""
import uuid
from django.db import models
from django.utils import timezone

from .managers import TenantManager


class TenantModel(models.Model):
    """
    Model abstrato base para todas as entidades do sistema multi-tenant.
    
    Fornece:
    - ID único global (UUID v4)
    - Isolamento de dados por empresa (multi-tenancy)
    - Timestamps automáticos (created_at, updated_at)
    - Soft delete (is_active)
    - Manager customizado com filtragem por tenant
    
    Todos os models de negócio devem herdar desta classe para garantir
    conformidade com a arquitetura multi-tenant.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
        help_text='Identificador único universal (UUID v4)'
    )
    
    empresa = models.ForeignKey(
        'tenant.Empresa',  # Referência lazy - app tenant deve ser criado separadamente
        on_delete=models.PROTECT,
        related_name='%(class)s_set',
        verbose_name='Empresa',
        help_text='Empresa à qual este registro pertence (tenant)',
        db_index=True  # Índice crítico para performance em queries multi-tenant
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
        help_text='Data e hora de criação do registro'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
        help_text='Data e hora da última atualização'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Indica se o registro está ativo (soft delete)',
        db_index=True  # Índice para melhorar performance do TenantManager
    )
    
    # Manager padrão com filtragem automática por tenant e is_active
    objects = TenantManager()
    
    # Manager sem filtros para acesso administrativo (use com cuidado!)
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        get_latest_by = 'created_at'
    
    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Sobrescreve delete para implementar soft delete por padrão.
        
        Args:
            using: Database a ser usado
            keep_parents: Manter registros pais
            hard: Se True, executa delete físico. Se False (padrão), apenas marca is_active=False
        """
        if hard:
            # Delete físico - use apenas quando absolutamente necessário
            super().delete(using=using, keep_parents=keep_parents)
        else:
            # Soft delete - método padrão recomendado
            self.is_active = False
            self.save(update_fields=['is_active', 'updated_at'])
    
    def __str__(self):
        """
        Implementação padrão do __str__.
        Models filhos devem sobrescrever para fornecer representação mais específica.
        """
        return f"{self.__class__.__name__} {self.id}"
