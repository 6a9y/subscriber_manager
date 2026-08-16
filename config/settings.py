"""
Django settings for config project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# الأمان
# =========================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-@23v81sb!c%xj!v_0ip!e-)kd!85-r6e--vh99th8nf0&y((s!'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]


# =========================================================
# التطبيقات
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'subscribers',
]


# =========================================================
# Middleware
# =========================================================

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


# =========================================================
# Templates
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
# قاعدة البيانات
# =========================================================
#
# على الحاسبة:
# يستخدم db.sqlite3
#
# على Render:
# إذا DATABASE_URL موجودة، يستخدم PostgreSQL
# =========================================================

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =========================================================
# Password validation
# =========================================================

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


# =========================================================
# اللغة والوقت
# =========================================================

LANGUAGE_CODE = 'ar'

TIME_ZONE = 'Asia/Baghdad'

USE_I18N = True

USE_TZ = True

DATE_FORMAT = 'Y-m-d'

SHORT_DATE_FORMAT = 'Y-m-d'


# =========================================================
# Static Files
# =========================================================

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================================================
# Email
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# =========================================================
# Default primary key
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'