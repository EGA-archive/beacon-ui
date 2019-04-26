"""
WSGI config for EGA Beacon Frontend.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import logging
import yaml

from django.core.wsgi import get_wsgi_application

# Logging
LOG_YML = os.getenv('LOG_YML', os.path.join(os.path.dirname(os.path.dirname(__file__)),'logger.yaml'))
if os.path.exists(LOG_YML):
    with open(LOG_YML, 'rt') as stream:
        #print('Using logger',LOG_YML)
        logging.config.dictConfig(yaml.safe_load(stream))

# The App
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beaconui.settings")
application = get_wsgi_application()
