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

ALLOWED_HOSTS = ['*']

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
    'rest_framework_simplejwt.token_blacklist',
    
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
# Usa DATABASE_URL se fornecida, caso contrário usa SQLite para desenvolvimento
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
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
        'anon': '1000/hour',             # Aumentado para não travar
        'anon_strict': '100/hour',
        'user': '100000/day',            # Aumentado significativamente
        'burst': '200/minute',
        'sustained': '5000/hour',
        'vendas': '500/minute',
        'relatorios': '100/minute',
    },
    
    # Renderização
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Apenas em dev
    ],
}

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
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
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins - Liberado para os domínios principais e localhost
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3002',
    'https://projetohavoc.shop',
    'https://api.projetohavoc.shop',
]

# Whitenoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Settings (Production)
if not DEBUG:
    # Em ambiente Docker local/LAN sem SSL, devemos desativar o redirecionamento forçado
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# Configuração de Email (SMTP)
# Descomente e preencha para habilitar envio de emails
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Nix Food <noreply@nixfood.com>')

# Sentry (Observabilidade)
# Descomente para habilitar monitoramento de erros em produção
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# if not DEBUG:
#     sentry_sdk.init(
#         dsn=os.environ.get('SENTRY_DSN', ''),
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=True
#     )

# Configurações de Negócio
# Desativa controle de Lotes (FIFO/FEFO) para facilitar testes.
# Se True, exige que existam Lotes criados para cada entrada de produto.
ESTOQUE_USAR_LOTES = False
