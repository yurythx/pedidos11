"""Utilitários de Auditoria.

- log_action: registra ação com metadados;
- payload_hash: gera hash SHA256 do payload;
- ensure_idempotency: garante idempotência por chave e payload.
"""
import hashlib
from django.utils import timezone
from .models import AuditLog, IdempotencyKey


def log_action(user, action, model_name, object_id=None, details=None):
    """Cria log de auditoria com usuário, ação, modelo e detalhes."""
    AuditLog.objects.create(user=user, action=action, model=model_name, object_id=str(object_id) if object_id else None, details=details or {})


def payload_hash(data):
    """Hash estável do payload para comparação/idempotência."""
    s = str(data).encode('utf-8')
    return hashlib.sha256(s).hexdigest()


def ensure_idempotency(key, user, endpoint, data):
    """Cria/obtém chave de idempotência; retorna tupla (obj, created)."""
    if not key:
        return None, False
    h = payload_hash(data)
    obj, created = IdempotencyKey.objects.get_or_create(key=key, defaults={'user': user, 'endpoint': endpoint, 'payload_hash': h, 'created_at': timezone.now()})
    return obj, created
