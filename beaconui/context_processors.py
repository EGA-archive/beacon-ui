import logging
from hashlib import sha256
import os


import requests
from django.http import HttpResponse
from django.core.cache import cache
from django.contrib import messages

from . import conf
from .auth import do_logout

LOG = logging.getLogger(__name__)

####################################

def make_cache_key(*args):
    #LOG.debug('Making Cache Key for: %s', args)
    m = sha256()
    for a in args:
        if a:
            m.update(str(a).encode())
    return m.hexdigest().lower()

def cached(func):
    def wrapper(*args, **kwargs): 
        cache_key = make_cache_key(*args) # ignoring kwargs
        cached_data = cache.get(cache_key)
        if cached_data:
            LOG.info('Rendering using cache | key: %s', cache_key)
            return cached_data
        else:
            data = func(*args, **kwargs)
            LOG.info('Caching results with key: %s', cache_key)
            cache.set(cache_key, data)
            return data
    return wrapper

# Backend General Error
class BeaconError(Exception):
    pass

# Backend answers with 401
class AuthError(BeaconError):
    pass


@cached
def get_info(user, access_token = None):

    query_url = conf.CONF.get('beacon-api', 'info_url')
    if not query_url:
        raise BeaconError('[beacon-api] info misconfigured')
    LOG.info('Beacon backend URL: %s', query_url)
    
    headers = { 'Accept': 'application/json',
                'Content-type': 'application/json',
    }
    if access_token: # we have a user
        headers['Authorization'] = 'Bearer ' + access_token

    resp = requests.get(query_url, headers=headers)
    beacon_info = resp.json()

    if resp.status_code == 401:
        # Auth error (like Invalid token)
        message = beacon_info.get('header',{}).get('userMessage')
        raise AuthError(message)

    if resp.status_code == 200:
        return beacon_info

    # In other cases
    raise Exception(f'Error {resp.status_code}: {message}')


# Context Processor
def info(request):
    try:
        user = request.session.get('user')
        LOG.debug('User: %s', user )
        user_id = user.get('sub') if user else None
        LOG.info('User id: %s', user_id )
        access_token = request.session.get('access_token')
        da_info = get_info(user_id, access_token = None)
        #messages.info(request, f'Info for {user_id}')
    except AuthError as ae:
        LOG.debug('Retrying without the token')
        do_logout(request)
        # retry without the token
        da_info = get_info(None)
        messages.info(request, 'Session expired, you are logged out.')

    return {
        'BEACON': da_info,
        'ASSEMBLYIDS': conf.BEACON_ASSEMBLYIDS, # same for everyone
    }



