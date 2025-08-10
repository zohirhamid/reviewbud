from pathlib import Path
import os
from decouple import config  # Move this to the top

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-gx_!+o%_@jo9+%(1f+4uiyh24$wj50ghwiz5=l(jpv9=&ah+=*'

STRIPE_PUBLISHABLE_KEY = 'pk_test_51RuLGJJTzdfCaExUPqgVSTYqWS1vsRO1VtUEB7Yvrn80zY1K3TZ5i5dIg46BS31qRCXlVetKGDnLPDZNSAhyvByb00Dzpp9RrS'
STRIPE_SECRET_KEY = 'sk_test_51RuLGJJTzdfCaExUC8Skhd0gwFBMmfOwz7i5A2y7oObLXmvzQxMv69arahl0yBm8CyuW2MeDBIAHVsJYqh3MzHtu00AUk649ct'

DEBUG = True
ALLOWED_HOSTS = []

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

SOCIALACCOUNTS_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
USE_OPENAI_API = config('USE_OPENAI_API', default=False, cast=bool)

# Google Places API key
GOOGLE_PLACES_API_KEY = config('GOOGLE_PLACES_API_KEY', default='AIzaSyBFSrkWWpUl3sqktRtqBEOFNE6lxhoWkdU')

# Stripe integration
STRIPE_PUBLISHABLE_KEY = 'pk_test_51RuLGJJTzdfCaExUPqgVSTYqWS1vsRO1VtUEB7Yvrn80zY1K3TZ5i5dIg46BS31qRCXlVetKGDnLPDZNSAhyvByb00Dzpp9RrS'
STRIPE_SECRET_KEY = 'sk_test_51RuLGJJTzdfCaExUC8Skhd0gwFBMmfOwz7i5A2y7oObLXmvzQxMv69arahl0yBm8CyuW2MeDBIAHVsJYqh3MzHtu00AUk649ct'

STRIPE_PRICE_IDS = {
    'pro': 'price_1RuZIUJTzdfCaExUmp5PNK8y',
    'enterprise': 'price_1RuZJcJTzdfCaExUfrUTzMcp',
}