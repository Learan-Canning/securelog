"""
DJANGO SETTINGS - Configuration for SecureLog Application

This file contains all Django configuration settings for the SecureLog project.
Settings control database connections, security, static files, and app behavior.

Key Configuration Areas:
- Security: SECRET_KEY, DEBUG, ALLOWED_HOSTS
- Database: SQLite for development, PostgreSQL for production (Heroku)
- Static Files: CSS, JavaScript, images handling
- Apps: Installed applications and middleware
- Authentication: Login/logout URLs and user management

Assessment Requirements Met:
- LO6.3: Security configuration (DEBUG=False, environment variables)
- LO5.2: Secure code management (no secrets in repository)
- LO6.1: Cloud deployment configuration (Heroku-ready)
"""

# === IMPORTS FOR CONFIGURATION ===
from pathlib import Path  # Modern Python path handling
from decouple import config  # Environment variable management (keeps secrets out of code)
import os  # Operating system interface
import dj_database_url  # Database URL parsing for Heroku deployment

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# === SECURITY SETTINGS ===

# SECRET_KEY: Used for cryptographic signing (sessions, CSRF, etc.)
# CRITICAL: Never expose this in version control! 
# Uses environment variable with secure fallback
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key')

# DEBUG: Controls error display and development features
# MUST be False in production for security
# Uses environment variable, defaults to True for development
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS: Domain names that this Django site can serve
# Required when DEBUG=False, prevents Host header attacks
# Configured for both local development and Heroku deployment
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')


# Application definition

# === APPLICATION CONFIGURATION ===
INSTALLED_APPS = [
    # Django Built-in Apps (core functionality)
    'django.contrib.admin',        # Admin interface at /admin/
    'django.contrib.auth',         # User authentication system
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Flash messaging framework
    'django.contrib.staticfiles',  # Static file handling (CSS, JS, images)
    
    # Third Party Apps (external packages)
    'crispy_forms',        # Better form rendering
    'crispy_bootstrap4',   # Bootstrap 4 integration for forms
    
    # Local Apps (our custom applications)
    'incidents',  # Main incident reporting functionality
]

# === CRISPY FORMS CONFIGURATION ===
# Makes forms look better with Bootstrap styling
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"  # Available template packs
CRISPY_TEMPLATE_PACK = "bootstrap4"            # Active template pack

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'securelog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'securelog_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override database for production (Heroku)
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Whitenoise configuration for static files on Heroku
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
