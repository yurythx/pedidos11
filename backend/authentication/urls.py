"""
URLs para autenticação (JWT).
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer
from .views import UserViewSet

class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para obter token com payload enriquecido."""
    serializer_class = CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Obter par de tokens (access + refresh)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Renovar access token usando refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Verificar se token é válido
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
