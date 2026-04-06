import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SECRET KEY ────────────────────────────────────────────────────────────────
# NEVER use the default in production. Generate with:
#   python -c "import secrets; print(secrets.token_urlsafe(64))"
_secret = os.getenv('DJANGO_SECRET_KEY')
if not _secret:
    if os.getenv('DJANGO_ENV') == 'production':
        raise RuntimeError("DJANGO_SECRET_KEY environment variable must be set in production")
    # Development only — generate a fresh key each restart (sessions won't persist)
    _secret = secrets.token_urlsafe(64)
SECRET_KEY = _secret

# ─── ENVIRONMENT ───────────────────────────────────────────────────────────────
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')
DEBUG      = DJANGO_ENV != 'production'

# ─── HOSTS ─────────────────────────────────────────────────────────────────────
_allowed = os.getenv('ALLOWED_HOSTS', '')
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.0.103']
else:
    raise RuntimeError("ALLOWED_HOSTS must be set in production")

# ─── APPS ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

# ─── MIDDLEWARE (order matters) ─────────────────────────────────────────────────
MIDDLEWARE = [
    'api.security.SecurityHeadersMiddleware',        # Security headers first
    'api.security.BruteForceProtectionMiddleware',   # Block bad IPs
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.RequestLoggingMiddleware',
    'api.middleware.PerformanceMonitoringMiddleware',
]

ROOT_URLCONF = 'sms_security.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'sms_security.wsgi.application'

# ─── DATABASE ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

# ─── CACHE ─────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'textguard-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 4,
        }
    }
}

# ─── PASSWORD VALIDATION ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALISATION ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── STATIC / MEDIA ────────────────────────────────────────────────────────────
STATIC_URL  = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = 'media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── CORS ──────────────────────────────────────────────────────────────────────
# Never allow all origins — always use explicit whitelist
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in
    os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://192.168.0.103:3000').split(',')
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = False  # Only enable if you add session auth
CORS_ALLOW_METHODS = ['GET', 'POST', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'content-type',
    'origin', 'x-requested-with', 'x-api-key',
]

# ─── SESSION & COOKIE SECURITY ─────────────────────────────────────────────────
SESSION_COOKIE_SECURE   = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE      = 3600  # 1 hour

CSRF_COOKIE_SECURE   = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ─── HTTPS / HSTS (production only) ───────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT          = True
    SECURE_HSTS_SECONDS          = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD          = True
    SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')

# Always set these
SECURE_BROWSER_XSS_FILTER    = True
SECURE_CONTENT_TYPE_NOSNIFF  = True
SECURE_REFERRER_POLICY       = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS              = 'DENY'

# ─── REST FRAMEWORK ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.security.ApiKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # Public by default — individual views can restrict further
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':    '100/hour',
        'user':    '1000/hour',
        'predict': '20/minute',
        'burst':   '5/second',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    # Never expose exception details in production
    'EXCEPTION_HANDLER': 'api.security_views.custom_exception_handler',
}

# ─── ADMIN SECURITY ────────────────────────────────────────────────────────────
# Change the admin URL to something non-obvious
ADMIN_URL = os.getenv('ADMIN_URL', 'secure-admin-panel/')

# ─── LOGGING ───────────────────────────────────────────────────────────────────
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'audit': {
            'format': '[AUDIT] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'app_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',
            'maxBytes': 50 * 1024 * 1024,
            'backupCount': 30,
            'formatter': 'audit',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'app_file'],
            'level': 'WARNING' if not DEBUG else 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'app_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'ml_models': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ─── ML CONFIG ─────────────────────────────────────────────────────────────────
ML_MODELS_DIR     = os.path.join(BASE_DIR, 'ml_models', 'trained_models')
ML_CACHE_TIMEOUT  = 3600
ML_BATCH_SIZE     = 32
ML_MODEL_VERSION  = os.getenv('ML_MODEL_VERSION', 'v1.0')

# ─── FEATURE FLAGS ─────────────────────────────────────────────────────────────
ENABLE_CACHING          = os.getenv('ENABLE_CACHING', 'True') == 'True'
ENABLE_DEEP_LEARNING    = os.getenv('ENABLE_DEEP_LEARNING', 'True') == 'True'
ENABLE_ENSEMBLE         = os.getenv('ENABLE_ENSEMBLE', 'True') == 'True'
ENABLE_ASYNC_PROCESSING = os.getenv('ENABLE_ASYNC_PROCESSING', 'False') == 'True'

# ─── API KEYS (hashed SHA-256) ─────────────────────────────────────────────────
# To add a key: python -c "import hashlib; print(hashlib.sha256(b'your-key').hexdigest())"
_raw_keys = os.getenv('VALID_API_KEYS', '')
VALID_API_KEYS = [k.strip() for k in _raw_keys.split(',') if k.strip()]
