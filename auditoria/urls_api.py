"""Rotas da API de Auditoria."""
from rest_framework.routers import SimpleRouter
from .views import AuditLogViewSet

router = SimpleRouter()
router.register('auditoria', AuditLogViewSet, basename='auditoria')

urlpatterns = router.urls
