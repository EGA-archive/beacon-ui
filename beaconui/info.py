import sys
import logging
from hashlib import sha256
import os

from django.http import Http404
from django.core.cache import cache
import requests

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
    
    query_url = os.getenv('BEACON_INFO_ENDPOINT')

    if not query_url:
        raise Http404('BEACON_INFO_ENDPOINT environment variable is empty')

    cache_key = make_cache_key(user,access_token)
    cached_data = cache.get(cache_key)
    if cached_data:
        LOG.info('Rendering using cache | key: %s', cache_key)
        return cached_data
    else:
        LOG.info('Contacting Beacon backend: %s', query_url)
        headers = { 'Accept': 'application/json',
                    'Content-type': 'application/json',
                    #'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        params = {}
        if access_token: # we have a user
            params['auth'] = 'yes'
            headers['Authorization'] = 'Bearer ' + access_token

        # resp = requests.get(query_url, headers=headers, params=params)
        # if resp.status_code > 200:
        #     raise Http404('Backend not available')

        # beacon_info = resp.json()
        import json
        with open('/Users/daz/_beacon/frontend/beacon.info.txt') as f:
            beacon_info = json.load(f)

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
# Beacon Endpoints
#########################################################################

# Beacon endpoint are now in environment variables
# Check the Makefile for BEACON_INFO_ENDPOINT and BEACON_QUERY_ENDPOINT

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
