"""Admin de Auditoria: logs e chaves de idempotência."""
from django.contrib import admin
from .models import AuditLog, IdempotencyKey


class AuditLogAdmin(admin.ModelAdmin):
    """Admin para AuditLog (leitura/escrita controlada)."""
    list_display = ("user", "action", "model", "object_id", "created_at")
    list_filter = ("action", "model")
    search_fields = ("user__username", "model", "object_id")
    date_hierarchy = "created_at"


class IdempotencyKeyAdmin(admin.ModelAdmin):
    """Admin para IdempotencyKey."""
    list_display = ("key", "user", "endpoint", "payload_hash", "created_at")
    search_fields = ("key", "user__username", "endpoint")
    date_hierarchy = "created_at"


admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(IdempotencyKey, IdempotencyKeyAdmin)
