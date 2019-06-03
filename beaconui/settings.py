"""
Django settings for Beacon Frontend.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '45@$0dth)d(pi*s6ejaay8xd@s0scjqgl_nj0ezyuon*2xxz@p'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ['tf.crg.eu','ega-archive.org','130.239.81.195','localhost']

ADMINS = (
    ('Sabela', 'sabela.delatorre@crg.eu'),
    ('Fred', 'frederic.haziza@crg.eu'),
)
SERVER_EMAIL = 'all.ega@crg.eu'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_URL = '/login/'

# Application definition

INSTALLED_APPS = [
    'beaconui',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.forms',
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600 # seconds
CACHE_MIDDLEWARE_KEY_PREFIX = '' # don't care

ROOT_URLCONF = 'beaconui.urls'

DATABASES = {
    'default': {
        # SQLite
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite'),
        'OPTIONS': { 'timeout': 300, }
    }
}

#SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

import django 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), django.__path__[0] + '/forms/templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'beaconui.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('es', _('Español')),
    ('cat', _('Catalan')),
    ('en', _('English')),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '_build')
STATICFILES_DIRS = [ # additional
    os.path.join(BASE_DIR, 'static'), # so we don't need collectstatic
]


########################################################################
## Beacon settings
########################################################################
import sys
import os
import configparser
from logging.config import fileConfig, dictConfig
import yaml

# Conf in INI format
BEACON_UI_CONF = os.getenv('BEACON_UI_CONF')
if not BEACON_UI_CONF:
    print('BEACON_UI_CONF environment variable is empty', file=sys.stderr)
    sys.exit(1)

CONF = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
if not BEACON_UI_CONF.startswith('/'): # relative path
    BEACON_UI_CONF = os.path.join(BASE_DIR, BEACON_UI_CONF)
CONF.read(BEACON_UI_CONF)

# Log inside CONF in INI format
fileConfig(BEACON_UI_CONF)

