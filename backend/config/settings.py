"""
Django settings para Projeto Nix.
"""
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-IN-PRODUCTION')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    
    # Projeto Nix apps
    'tenant',
    'core',
    'authentication',
    'locations',
    'catalog',
    'stock',
    'partners',
    'sales',
    'financial',
    'restaurant',  # Food Service
    'api',
    'scripts',  # Scripts e utilitários
    'nfe',  # Importação de NFe
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Configuração dinâmica para suportar PostgreSQL via variáveis de ambiente
if os.environ.get('DATABASE') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('SQL_DATABASE', 'pedidos11'),
            'USER': os.environ.get('SQL_USER', 'postgres'),
            'PASSWORD': os.environ.get('SQL_PASSWORD', 'postgres'),
            'HOST': os.environ.get('SQL_HOST', 'db'),
            'PORT': os.environ.get('SQL_PORT', '5432'),
        }
    }
else:
    # Usando SQLite para desenvolvimento local sem Docker
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'authentication.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para Django Admin
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardPagination',
    'PAGE_SIZE': 50,
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Throttling (Rate Limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'api.throttling.BurstRateThrottle',
        'api.throttling.SustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',              # Anônimos: 100 req/hora
        'anon_strict': '20/hour',        # Anônimos (endpoints sensíveis)
        'user': '10000/day',             # Autenticados: 10k req/dia
        'burst': '60/minute',            # Burst: 60 req/min
        'sustained': '1000/hour',        # Sustentado: 1k req/hora
        'vendas': '100/minute',          # Vendas: 100 req/min
        'relatorios': '10/minute',       # Relatórios: 10 req/min
    },
    
    # Renderização
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Apenas em dev
    ],
}

# drf-spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Projeto Nix API',
    'DESCRIPTION': '''ERP/PDV completo com multi-tenancy para Food Service.
    
    ## Autenticação
    Esta API usa JWT (JSON Web Tokens) para autenticação.
    
    ### Obter Token
    ```
    POST /api/auth/token/
    {
        "username": "seu_usuario",
        "password": "sua_senha"
    }
    ```
    
    ### Usar Token
    Adicione o header:
    ```
    Authorization: Bearer {seu_access_token}
    ```
    
    ## Rate Limiting
    - Usuários autenticados: 10.000 requests/dia
    - Usuários anônimos: 100 requests/hora
    - Endpoints de vendas: 100 requests/minuto
    - Relatórios: 10 requests/minuto
    
    ## Paginação
    Todas as listagens são paginadas:
    - Padrão: 50 itens por página
    - Customizar: `?page_size=100`
    - Máximo: 1000 itens
    
    ## Filtros
    Use query params para filtrar:
    - `?status=FINALIZADA`
    - `?data_inicio=2026-01-01&data_fim=2026-01-31`
    - `?valor_min=100&valor_max=1000`
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': True,
    
    # Metadata
    'CONTACT': {
        'name': 'Projeto Nix',
        'email': 'suporte@projetonix.com',
    },
    'LICENSE': {
        'name': 'Proprietary',
    },
    
    # UI
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    
    # Schema
    'SCHEMA_COERCE_METHOD_NAMES': {
        'list': 'Listar',
        'create': 'Criar',
        'retrieve': 'Detalhes',
        'update': 'Atualizar',
        'partial_update': 'Atualizar Parcial',
        'destroy': 'Deletar',
    },
}

# CORS
if os.environ.get('CORS_ALLOW_ALL', 'False') == 'True':
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001'
    ).split(',')

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# Security Settings (Production)
if not DEBUG:
    # Em ambiente Docker local/LAN sem SSL, devemos desativar o redirecionamento forçado
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Configurações de Negócio
# Desativa controle de Lotes (FIFO/FEFO) para facilitar testes.
# Se True, exige que existam Lotes criados para cada entrada de produto.
ESTOQUE_USAR_LOTES = False
