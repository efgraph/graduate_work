import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# load_dotenv(Path(f'{str(BASE_DIR.parent)}/docker/variables.env'))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", 'django-insecure-bcwg-&mr!q7f@9nnho=m%=rj2*l@lxk!qtrb58*zimtxg)!-_e')

DEBUG = True

ALLOWED_HOSTS = ['*']

DOMAIN_URL = os.getenv("DOMAIN_URL", "http://localhost:8000")
BASE_API_URL = f"{DOMAIN_URL}/api/v1/"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'billing_app',
    'djstripe'
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB_BILLING', ''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST_BILLING', ''),
        'PORT': os.environ.get('POSTGRES_PORT_BILLING', 5432),
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_ROOT = '/var/www/'
STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STRIPE_TEST_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

DJSTRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET', '')

DJSTRIPE_FOREIGN_KEY_TO_FIELD='id'

JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', '')

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv("KAFKA_BROKER_URL", "0.0.0.0:9092"),
}