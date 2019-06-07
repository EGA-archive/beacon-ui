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

ALLOWED_HOSTS = ['tf.crg.eu',
                 'ega-archive.org',
                 'xfer13.local',
                 '130.239.81.195',
                 '84.88.52.84',
                 'localhost']

ROOT_URLCONF = 'beaconui.urls'

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
    #'django.contrib.sessions',
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
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 3600 # seconds
CACHE_MIDDLEWARE_KEY_PREFIX = '' # don't care


# DATABASES = {
#     'default': {
#         # SQLite
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite'),
#         'OPTIONS': { 'timeout': 300, }
#     }
# }

#SESSION_ENGINE = 'django.contrib.sessions.backends.db'
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
#SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_ENGINE = 'encrypted_cookies' # signed and encrypted
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = 'beacon-session'


ENCRYPTED_COOKIE_KEYS = ['gYeI6rjUhpLOSMDHxFFh9dONUA9auiKiLTrzZQz4nfg=']
SESSION_COOKIE_SECURE = False
ENCRYPTED_COOKIE_SERIALIZER = 'json'
COMPRESS_ENCRYPTED_COOKIE = True
#ENCRYPTED_COOKIE_COMPRESSION_LEVEL = 6

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
from logging.config import dictConfig
import yaml

# Conf in INI format
conf_file = os.getenv('BEACON_UI_CONF')
if not conf_file:
    print('BEACON_UI_CONF environment variable is empty', file=sys.stderr)
    sys.exit(1)

CONF = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
if not conf_file.startswith('/'): # relative path
    conf_file = os.path.join(BASE_DIR, conf_file)
CONF.read(conf_file)

# Logger in YML format
log_file = os.getenv('BEACON_UI_LOG')
if log_file and os.path.exists(log_file):
    with open(log_file, 'r') as stream:
        dictConfig(yaml.safe_load(stream))

