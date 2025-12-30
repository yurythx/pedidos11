import logging

logger = logging.getLogger('app')

class AuditRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        payload = None
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            try:
                # attempt to parse JSON
                import json
                body = request.body.decode('utf-8') if request.body else ''
                payload = json.loads(body) if body else None
            except Exception:
                payload = None
        response = self.get_response(request)
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            user_id = getattr(request.user, 'id', None)
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
            path = request.path
            logger.info(f"audit request method={request.method} path={path} user_id={user_id} ip={ip}")
            try:
                from auditoria.models import AuditLog
                AuditLog.objects.create(
                    user=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
                    action=request.method.lower(),
                    model='request',
                    object_id=None,
                    details={'ip': ip, 'path': path, 'method': request.method, 'payload': payload},
                )
            except Exception:
                pass
        return response
