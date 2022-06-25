from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from decouple import config
import os


BASE_DIR = Path(__file__).resolve().parent.parent

# env_file = os.path.join(BASE_DIR, '.env')

load_dotenv(find_dotenv())
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'swap.User'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_email_verification',
    'swap.apps.SwapConfig',
    'chatroom',
    'security',
    'channels'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'weblate.accounts.AuthenticationMiddleware',
    # 'swap.middleware.IncludesBlackList'
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "swap/static"),
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

LOGOUT_REDIRECT_URL='/home/'
LOGIN_REDIRECT_URL = '/profile/'
# FORCE_SCRIPT_NAME = '/home'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"  

STATIC_URL = 'static/'

#SMTP-configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')


CHANNEL_LAYERS = {
    'default' : {
        'BACKEND' : 'channels.layers.InMemoryChannelLayers'
    }
}

API_KEY = "0Q128gomlU0IWRS7gU8XKKpMO"
API_SECRET_KEY = "7BXPWKTxH6mInjDjY5SCOAe8v7Ueujgu4msdodee9rAgTmAYWM"
BEARER = "AAAAAAAAAAAAAAAAAAAAAHFreAEAAAAAIVCvposrjwGpLvMgF6rrA7McNeA%3DjvwcUe0HFktp0FsJKjShiYEWtKe5RmUSiNrk5kqgCznGsdgOtI"
ACCESS_TOKEN = "1378945133073334272-n4bp6iaUv1GlTywau6aRnzYdbR4LEF"
ACCESS_SECRET_TOKEN = "uy1WjfHzbabn3jg2qxXKs097x7rLWAi7TjGKuYzsqs2AA"