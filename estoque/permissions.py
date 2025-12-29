from rest_framework.permissions import BasePermission


class IsOperacaoOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return user.groups.filter(name__in=['operacao', 'estoque']).exists()
