import logging
import uuid
import base64
from urllib.parse import urlencode

import requests
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import TemplateView
from django.urls import reverse
from django.contrib.auth import logout

LOG = logging.getLogger(__name__)

class EGABeaconLoginView(TemplateView):

    def get(self, request):

        access_token = request.session.get('access_token')
        if access_token:
            LOG.debug('Token: %s', access_token)
            return HttpResponseRedirect(reverse('info'))

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

        LOG.debug('All good, we got an access token: %s...', access_token[:30])
        request.session['access_token'] = access_token
        id_token = data.get('id_token')
        if id_token:
            LOG.debug('And an ID token? %s...', id_token[:30])
            request.session['id_token'] = id_token

        # Fetch more info about the user
        res = requests.post(USER_INFO_URL, headers=headers, data=urlencode({'access_token': access_token}))
        user = None
        if res.status_code == 200:
            user = res.json()

        LOG.info('The user is: %r', user)
        request.session['user'] = user

        return HttpResponseRedirect(reverse('info'))

class EGABeaconLogoutView(TemplateView):

    def get(self, request):
        LOG.info('Logging out: %s', request.session.get('user'))
        request.session['user']=None
        request.session['access_token']=None
        request.session['id_token']=None
        # None or del ?
        logout(request)
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
        
