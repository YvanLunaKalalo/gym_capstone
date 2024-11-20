"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l#awhl+_(-h3z=!j1#wf=*+!%u2upmy0*(1m0x_%u0^pk58u8x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False   

ALLOWED_HOSTS = ['https://web-production-54a2b.up.railway.app/']

CSRF_COOKIE_SECURE = True  # Use only in production with HTTPS

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-54a2b.up.railway.app',
    'https://www.web-production-54a2b.up.railway.app',  # If applicable
]


if DEBUG:
     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Doing Development

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My Apps
    'personal',
    'bootstrap5',
    'account',
    'machine_learning',
]

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

ROOT_URLCONF = 'mysite.urls'

# Path to the notebooks folder
NOTEBOOKS_DIR = BASE_DIR / 'notebooks'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Templates
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

AUTH_USER_MODEL = 'account.Account'

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_ROOT = BASE_DIR / 'productionfiles' # Collect Static Files

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'  # for production

STATICFILES_DIRS = [BASE_DIR / 'personal', 'static']

STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Reset Password: Confirmation through Backend
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Doing Development

# Registration and Reset Password Confirmation through GMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER ='kalaloyvan07@gmail.com'
EMAIL_HOST_PASSWORD ='blec jarj xnwl gkrm'

#Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "Flex Appeal || Admin",
    "site_brand": "Flex Appeal",
    # "site_logo": "images/image2.png",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome to Admin of Flex Appeal",
    "copyright": "Copyright © 2024 Flex Appeal - Designed by Yvan Kalalo, Lyka Mae P. Lalog, Edward Ora-a, John Mark Manalo. Distributed by Yvan Kalalo, Lyka Mae P. Lalog, Edward Ora-a, and John Mark Manalo.",
    "show_ui_builder": True,
    "topmenu_links": [
        {"name": "User Stats", "url": "user_account_statistics", "permissions": ["auth.view_user"]},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "None",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}