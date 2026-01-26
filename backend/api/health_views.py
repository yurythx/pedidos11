from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.utils import timezone
try:
    import psutil
except ImportError:
    psutil = None
import os

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de monitoramento de saúde do sistema.
    Verifica Banco de Dados, Uso de Memória e Status da API.
    """
    health_status = {
        "status": "healthy",
        "timestamp": timezone.now(),
        "services": {
            "database": "up",
            "api": "up"
        },
        "system": {
            "memory_usage_percent": psutil.virtual_memory().percent if psutil else "N/A",
            "cpu_usage_percent": psutil.cpu_percent() if psutil else "N/A",
        }
    }

    # Teste de Conexão com DB
    try:
        connection.ensure_connection()
    except Exception:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = "down"

    return Response(health_status)
