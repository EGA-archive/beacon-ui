import sys
import logging
from hashlib import sha256
import os

import requests
from django.http import Http404, HttpResponse
from django.core.cache import cache
from django.conf import settings

LOG = logging.getLogger(__name__)

####################################

def make_cache_key(*args):
    #LOG.debug('Making Cache Key for: %s', args)
    m = sha256()
    for a in args:
        if a:
            m.update(str(a).encode())
    return m.hexdigest().lower()

def _fetch(user, access_token = None):
    
    query_url = settings.CONF.get('beacon-api', 'info_url')

    if not query_url:
        raise Http404('[beacon-api] info misconfigured')

    cache_key = make_cache_key(user,access_token)
    cached_data = cache.get(cache_key)
    if cached_data:
        LOG.info('Rendering using cache | key: %s', cache_key)
        return cached_data
    else:
        LOG.info('Contacting Beacon backend: %s', query_url)
        headers = { 'Accept': 'application/json',
                    'Content-type': 'application/json',
        }
        params = {}
        if access_token: # we have a user
            LOG.info('With a token: %s', access_token)
            headers['Authorization'] = 'Bearer ' + access_token

        resp = requests.get(query_url, headers=headers, params=params)
        if resp.status_code > 200:

            beacon_info = resp.json()
            message = beacon_info.get('header',{}).get('userMessage')
            raise Exception(f'Error {resp.status_code}: {message}')

            #raise Http404('Backend not available')

        beacon_info = resp.json()

        LOG.info('Caching results with key: %s', cache_key)
        cache.set(cache_key, beacon_info)
        return beacon_info

# Decorator
def fetch(func):
    def wrapper(self, request, *args, **kwargs):
        user = request.session.get('user')
        LOG.debug('User: %s', user )
        LOG.info('User id: %s', user.get('sub') if user else 'Anonymous' )
        access_token = request.session.get('access_token')
        beacon_info = _fetch(user, access_token = access_token)
        return func(self, request, beacon_info, *args, **kwargs)
    return wrapper


#########################################################################
# Fetch info, datasets and assemblyIds
#########################################################################
try:
    BEACON_INFO = _fetch(None, access_token=None)
except Exception as e:
    print(e, file=sys.stderr)
    sys.exit(2)

# This beacon datasets is for the non logged-in users
BEACON_DATASETS = BEACON_INFO.get('datasets',[])
BEACON_ASSEMBLYIDS = set( (d['assemblyId'] for d in BEACON_DATASETS) )

