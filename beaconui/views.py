import logging
import os
import json
import uuid
import base64
from urllib.parse import urlencode
from hashlib import sha256

import requests
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout
from django.core.cache import caches, cache


from .forms import QueryForm

LOG = logging.getLogger(__name__)

####################################


IDP_URL = 'https://egatest.crg.eu/idp/'
CLIENT_ID='beaconUI'
CLIENT_SECRET='NWjr_uGUafUt7KVyn-kZDvSIN9EzRC0bW9OzBur7KYuhpMzuImDRDwdfsTqj6ldjGb3ZlZ2n4RXJJNim-KepWA'
SCOPE='profile email openid'
AUTHORIZE_URL = IDP_URL + 'authorize?'
ACCESS_TOKEN_URL = IDP_URL + 'token'
USER_INFO_URL = IDP_URL + 'userinfo'

# Beacon Endpoints
BEACON_INTERNAL_ENDPOINT='https://egatest.crg.eu/requesterportal/v1/beacon/'

####################################

def make_cache_key(*args):
    LOG.debug('Making Cache Key for: %s', args)
    m = sha256()
    for a in args:
        if a:
            m.update(str(a).encode())
    return m.hexdigest().lower()

# Probably stupid here, but will be enhanced later.
def user_has_access(user, accessType):
    return accessType == 'PUBLIC' or user

def get_info(user, access_token):
    
    cache_key = make_cache_key(user,access_token)
    cached_data = cache.get(cache_key)
    if cached_data:
        LOG.info('Rendering using cache: %s', cache_key)
        return cached_data
    else:
        LOG.info('Contacting Beacon backend: %s', BEACON_INTERNAL_ENDPOINT)
        query_url = BEACON_INTERNAL_ENDPOINT + '?limit=0'
        headers = { 'Accept': 'application/json',
                    'Content-type': 'application/json',
                    #'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        params = {}
        if access_token: # we have a user
            params['auth'] = 'yes'
            headers['Authorization'] = 'Bearer '+access_token

        r = requests.get(query_url, headers=headers, params=params)
        if r.status_code > 200:
            return None

        data = r.json()
        datasets = data.get('datasets')
        all_ds = 0
        if datasets:
            all_ds = sum(d['variantCount'] for d in datasets \
                         if any(i['key'] == 'accessType' and user_has_access(user, i['value']) \
                                for i in d['info']))

        LOG.info('Caching results with key: %s', cache_key)
        res = (data, all_ds)
        cache.set(cache_key, res )
        return res


####################################

class EGABeaconInfoView(TemplateView):

    def get(self, request):
        LOG.debug('INFO start %s', '-'*30)
        user = request.session.get('user')
        access_token = request.session.get('access_token')

        info = get_info(user, access_token)

        if not info:
            return render(request, 'error.html', {'message':'Backend not available' })

        data, all_ds = info
        datasets = data.get('datasets')

        #LOG.debug(data)
        form = QueryForm(label_suffix="")

        ctx = { 'user': user, 'form':form, 'datasets':datasets, 'all_ds': all_ds, 'error': data.error }
        LOG.debug('INFO  end %s', '-'*30)
        return render(request, 'info.html', ctx)


class EGABeaconResultsView(TemplateView):

    def post(self, request):
        LOG.debug('RESULTS start %s', '-'*30)

        form = QueryForm(request.POST, label_suffix="")

        # if not form.is_valid():
        #     return render(request, 'info.html', {"form": form}) # with errors
        
        LOG.debug('POST data: %s', request.POST)


        # Otherwise, forward to backend
        query_url = BEACON_INTERNAL_ENDPOINT + 'query'
        LOG.debug('Forwarding to %s',query_url)

        r = requests.get(query_url, data=request.POST)
        if not r:
            return render(request, 'error.html', {'message':'Backend not available' })

        user = request.session.get('user')
        access_token = request.session.get('access_token')
        info = get_info(user, access_token)
        data, all_ds = info
        datasets = data.get('datasets')

        results = None
        if r.status_code == 200:
            results = r.json()
        LOG.debug('Results: %s', results)

        LOG.debug('RESULTS  end %s', '-'*30)
        ctx = { 'user': user, 'form':form, 'datasets':datasets, 'all_ds': all_ds, 'error': data.get('error'), 'results': results }
        return render(request, 'results.html', ctx)


