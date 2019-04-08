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
    m = sha256()
    for a in args:
        if a:
            m.update(str(a).encode())
    return m.hexdigest().lower()

####################################

class EGABeaconInfoView(TemplateView):

    def get(self, request):

        access_token = request.session.get('access_token')
        if access_token:
            LOG.debug('Token: %s...', access_token[:30])
        else:
            LOG.debug('No Token')

        cache_key = make_cache_key(request.session.get('user'), request.session.get('access_token'))
        cached_data = cache.get(cache_key)
        if cached_data:
            LOG.info('Rendering using cache: %s', cache_key)
            datasets, all_ds = cached_data
        else:
            # Contacting Beacon backend
            query_url = BEACON_INTERNAL_ENDPOINT + 'info'
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
                return render(request, 'error.html', {'message':'Backend not available' })

            data = r.json()
            datasets = data.get('datasets')
            all_ds = 0
            if datasets:
                all_ds = sum(d['variantCount'] for d in datasets \
                             if any(i['key'] == 'accessType' and i['value'] == 'PUBLIC' for i in d['info']))

            LOG.info('Caching results with key: %s', cache_key)
            cache.set(cache_key, (datasets,all_ds) )

        #LOG.debug(data)
        form = QueryForm(label_suffix="")

        ctx = { 'user': request.session.get('user'), 'form':form, 'datasets':datasets, 'all_ds': all_ds }
        return render(request, 'index.html', ctx)


class EGABeaconResultsView(TemplateView):

    def post(self, request):

        form = QueryForm(request.POST, label_suffix="")

        if not form.is_valid():
            return render(request, 'index.html', {"form": form}) # with errors


        # Otherwise, forward to backend
        query_url = settings.BEACON_ENDPOINT + 'query?'
        LOG.debug('Forwarding to %s',query_url)

        LOG.debug('Request %s', request)

        # r = requests.get(query_url)
        # if not r:
        #     return render(request, 'error.html', {'message':'Backend not available' })

        # data = r.json()
        data = None
        return render(request, 'results.html', {'form':form, 'data': data })


class EGABeaconLoginView(TemplateView):

    def get(self, request):

        access_token = request.session.get('access_token')
        if access_token:
            LOG.debug('Token: %s', access_token)
            return HttpResponseRedirect(reverse('index'))

        code = request.GET.get('code')
        if code is None:
            LOG.debug('We must have a code')
            redirect_uri = 'http://localhost:8000' + reverse('login')
            params = urlencode({ 'response_type': 'code',
                                 'client_id': CLIENT_ID,
                                 'scope': 'openid profile email',
                                 'state': uuid.uuid4(),
                                 'redirect_uri': redirect_uri })
            url = AUTHORIZE_URL + params
            LOG.debug('No code: Redirecting to URL: %s', url)
            return HttpResponseRedirect(url)

        state = request.GET.get('state')
        if not state:
            LOG.debug('We must have a state')
            raise HttpResponseBadRequest("Should have a state")

        headers = { 'Accept': 'application/json',
                    #'Content-type': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }

        redirect_uri = request.GET.get('next', '/')

        # We have a code and a state
        LOG.debug('Code: %s', code)

        basic = base64.b64encode('{}:{}'.format(CLIENT_ID, CLIENT_SECRET).encode())
        headers['Authorization'] = b'Basic '+basic

        params = { 'grant_type': 'authorization_code',
                   #'client_id': CLIENT_ID,
                   #'client_secret': CLIENT_SECRET,
                   'code': code,
                   'redirect_uri': 'http://localhost:8000/login' #'http://localhost:8000' + redirect_uri
        }
        LOG.debug( 'Post Request %r', params)
        res = requests.post(ACCESS_TOKEN_URL, headers=headers, data=urlencode(params))
        if res.status_code > 200:
            LOG.error( 'Error when getting the access token: %r', res)
            return HttpResponseBadRequest('Invalid response for access token.')
        data = res.json()
        access_token = data.get('access_token')
        if not access_token: 
            LOG.error( 'Error when getting the access token: %r', res)
            return HttpResponseBadRequest('Failed to obtain OAuth access token.')

        LOG.debug('All good, we got an access token: %s', access_token)
        request.session['access_token'] = access_token
        id_token = data.get('id_token')
        if id_token:
            LOG.debug('And an ID token? %s', id_token)
            request.session['id_token'] = id_token

        # Fetch more info about the user
        res = requests.post(USER_INFO_URL, headers=headers, data=urlencode({'access_token': access_token}))
        user = None
        if res.status_code == 200:
            user = res.json()

        LOG.info('The user is: %r', user)
        request.session['user'] = user

        return HttpResponseRedirect(reverse('index'))

class EGABeaconLogoutView(TemplateView):

    def get(self, request):
        LOG.info('Logging out: %s', request.session.get('user'))
        request.session['user']=None
        request.session['access_token']=None
        request.session['id_token']=None
        # None or del ?
        logout(request)
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
        
