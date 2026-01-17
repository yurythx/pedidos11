"""
Managers customizados para Projeto Nix.
Implementa segurança multi-tenant através de filtragem automática por empresa.
"""
from django.db import models


class TenantQuerySet(models.QuerySet):
    """
    QuerySet customizado que mantém o método for_tenant encadeável.
    """
    
    def for_tenant(self, user):
        """
        Retorna um queryset filtrado pela empresa do usuário.
        
        Args:
            user: Instância de User com atributo 'empresa'
            
        Returns:
            QuerySet filtrado pela empresa do usuário
            
        Raises:
            AttributeError: Se o user não possuir atributo 'empresa'
        """
        if not hasattr(user, 'empresa'):
            raise AttributeError(
                f"O usuário {user} não possui atributo 'empresa'. "
                "Verifique se o modelo User está configurado corretamente."
            )
        
        return self.filter(empresa=user.empresa)


class TenantManager(models.Manager):
    """
    Manager que implementa filtragem automática por tenant (empresa).
    
    Este manager garante que todas as queries sejam automaticamente filtradas
    pela empresa do usuário autenticado, prevenindo vazamento de dados entre
    diferentes tenants no modelo Shared Database, Shared Schema.
    
    Exemplo de uso:
        >>> produtos = Produto.objects.for_tenant(request.user)
        >>> # Retorna apenas produtos da empresa do usuário
    """
    
    def get_queryset(self):
        """
        Retorna o QuerySet customizado com for_tenant.
        """
        return TenantQuerySet(self.model, using=self._db).filter(is_active=True)
    
    def for_tenant(self, user):
        """
        Atalho para o método for_tenant do queryset.
        
        Args:
            user: Instância de User com atributo 'empresa'
            
        Returns:
            QuerySet filtrado pela empresa do usuário
        """
        return self.get_queryset().for_tenant(user)

