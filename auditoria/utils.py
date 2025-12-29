import hashlib
from django.utils import timezone
from .models import AuditLog, IdempotencyKey


def log_action(user, action, model_name, object_id=None, details=None):
    AuditLog.objects.create(user=user, action=action, model=model_name, object_id=str(object_id) if object_id else None, details=details or {})


def payload_hash(data):
    s = str(data).encode('utf-8')
    return hashlib.sha256(s).hexdigest()


def ensure_idempotency(key, user, endpoint, data):
    if not key:
        return None, False
    h = payload_hash(data)
    obj, created = IdempotencyKey.objects.get_or_create(key=key, defaults={'user': user, 'endpoint': endpoint, 'payload_hash': h, 'created_at': timezone.now()})
    return obj, created
