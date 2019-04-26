import logging
from hashlib import sha256

from django.conf import settings
from django.shortcuts import render
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

def fetch(user, access_token = None):
    
    cache_key = make_cache_key(user,access_token)
    cached_data = cache.get(cache_key)
    if cached_data:
        LOG.info('Rendering using cache key: %s', cache_key)
        return cached_data
    else:
        query_url = settings.BEACON_ENDPOINT + '?limit=0'
        LOG.info('Contacting Beacon backend: %s', query_url)
        headers = { 'Accept': 'application/json',
                    'Content-type': 'application/json',
                    #'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        params = {}
        if access_token: # we have a user
            params['auth'] = 'yes'
            headers['Authorization'] = 'Bearer ' + access_token

        resp = requests.get(query_url, headers=headers, params=params)
        if resp.status_code > 200:
            return None

        beacon_info = resp.json()
        LOG.info('Caching results with key: %s', cache_key)
        cache.set(cache_key, beacon_info)
        return beacon_info

# Decorator
def with_info(func):
    def wrapper(self, request):
        user = request.session.get('user')
        access_token = request.session.get('access_token')
        beacon_info = fetch(user, access_token = access_token)
        if not beacon_info:
            return render(request, 'error.html', {'message':'Backend not available' })
        return func(self, request, user, access_token, beacon_info)
    return wrapper
