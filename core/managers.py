"""
Managers customizados para ProjetoRavenna.
Implementa segurança multi-tenant através de filtragem automática por empresa.
"""
from django.db import models


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
    
    def get_queryset(self):
        """
        Sobrescreve o queryset padrão para filtrar apenas registros ativos.
        
        Returns:
            QuerySet com is_active=True
        """
        return super().get_queryset().filter(is_active=True)
