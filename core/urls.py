"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from django.db import connection

class ApiRoot(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'api_index.html'
    def get(self, request):
        data = {
            'vendas': request.build_absolute_uri('/api/v1/vendas/'),
            'estoque': request.build_absolute_uri('/api/v1/estoque/'),
            'financeiro': request.build_absolute_uri('/api/v1/financeiro/'),
            'relatorios': request.build_absolute_uri('/api/v1/relatorios/'),
            'auditoria': request.build_absolute_uri('/api/v1/auditoria/'),
        }
        return Response(data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', ApiRoot.as_view(), name='api-root'),
    path('api/schema/', get_schema_view(title='Pedidos11 API', version='v1'), name='api-schema'),
    path('api/docs/', TemplateView.as_view(template_name='api_docs.html'), name='api-docs'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/health/', TemplateView.as_view(template_name='api_health.html'), name='api-health'),
    path('api/v1/vendas/', include('vendas.urls_api')),
    path('api/v1/cadastro/', include('cadastro.urls_api')),
    path('api/v1/estoque/', include('estoque.urls_api')),
    path('api/v1/financeiro/', include('financeiro.urls_api')),
    path('api/v1/', include('relatorios.urls_api')),
    path('api/v1/', include('auditoria.urls_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
