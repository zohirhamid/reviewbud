from pathlib import Path
import os
from decouple import config 


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gx_!+o%_@jo9+%(1f+4uiyh24$wj50ghwiz5=l(jpv9=&ah+=*'

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    import logging
    logging.warning("OPENAI_API_KEY is not configured. AI review generation will use fallback templates.")

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    'quickratedb.railway.internal',
]

# Application definition
SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'businesses',
    'reviews',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google'
]

# Add this near your other security settings
CSRF_TRUSTED_ORIGINS = [
    'https://quickrate.up.railway.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quickrate.urls'

WSGI_APPLICATION = 'quickrate.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production database (Railway) - parse DATABASE_URL manually
    import urllib.parse as urlparse
    
    url = urlparse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],  # Remove leading slash
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
        }
    }
else:
    # Local development database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'quickratedb',
            'USER': 'quickrateuser',
            'PASSWORD': '011936',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


# Custom User Model (IMPORTANT!)
AUTH_USER_MODEL = 'businesses.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',  # ✅ Correct
]

SOCIALACCOUNT_LOGIN_ON_GET = True

# Login settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# API Configuration - Remove the duplicate OPENAI_API_KEY line
#OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
#USE_OPENAI_API = config('USE_OPENAI_API', default=False, cast=bool)

# Google Places API key
GOOGLE_PLACES_API_KEY = config('GOOGLE_PLACES_API_KEY', default='AIzaSyBFSrkWWpUl3sqktRtqBEOFNE6lxhoWkdU')

# Static files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

