from pathlib import Path
import os
from decouple import config  # Move this to the top

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gx_!+o%_@jo9+%(1f+4uiyh24$wj50ghwiz5=l(jpv9=&ah+=*'

DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'businesses',
    'reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quickrate.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

# Login settings
LOGIN_REDIRECT_URL = '/businesses/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/businesses/login/'

# API Configuration - Remove the duplicate OPENAI_API_KEY line
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
USE_OPENAI_API = config('USE_OPENAI_API', default=False, cast=bool)

# Google Places API key
GOOGLE_PLACES_API_KEY = config('GOOGLE_PLACES_API_KEY', default='AIzaSyBFSrkWWpUl3sqktRtqBEOFNE6lxhoWkdU')