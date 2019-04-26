import logging
import os
import json
import uuid
import base64
from urllib.parse import urlencode
from itertools import chain

import requests
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth import logout

from .info import with_info
from .forms import BeaconQueryDict, SimplifiedQueryForm, QueryForm

LOG = logging.getLogger(__name__)

####################################

class BeaconView(TemplateView):

    # If the user is not logged-in, the beacon_info are already cached
    @with_info
    def get(self, request, user, access_token, beacon_info):

        user = request.session.get('user')

        ctx = { 'user': user,
                'formdata': BeaconQueryDict(None),
                'form': QueryForm(),
                'simplifiedform': SimplifiedQueryForm(prefix = 'simplifiedform'),
                'beacon': beacon_info,
                'assemblyIds': settings.BEACON_ASSEMBLYIDS, # same for everyone
                'chromosomes': chain(range(1,22), ('X','Y','MT')),
        }
        return render(request, 'info.html', ctx)

    @with_info
    def post(self, request, user, access_token, beacon_info):

        user = request.session.get('user')

        simplifiedform = SimplifiedQueryForm(request.POST, prefix = 'simplifiedform')
        form = QueryForm(request.POST)

        # Form Validation here... is turned off
        form.is_valid() # ignore output
        extended = form.cleaned_data['extended']

        selected_datasets = set(request.POST.getlist("datasets", []))
        filters = set( f for f in request.POST.getlist("filters", []) if f )

        LOG.debug('selected_datasets: %s', selected_datasets )
        LOG.debug('filters: %s', filters )
        
        ctx = { 'user': user,
                'selected_datasets': selected_datasets,
                'filters': filters,
                'simplifiedform': simplifiedform,
                'form': form,
                'beacon': beacon_info,
                'assemblyIds': settings.BEACON_ASSEMBLYIDS, # same for everyone
                'chromosomes': chain(range(1,22), ('X','Y','MT')),
        }
        
        params_d = {}
        if extended:
            for field in form:
                # if field.label == 'csrfmiddlewaretoken':
                #     continue

                if field.name == 'extended':
                    continue
                
                value = field.value()
                if value:
                    params_d[field.name] = value
            
        else:
            pass

        #params_d['datasets'] = ','.join(selected_datasets) if selected_datasets else 'all'
        if selected_datasets:
            params_d['datasets'] = ','.join(selected_datasets) 
        if filters:
            params_d['filters'] = ','.join(filters)

        # Don't check anything and forward to backend
        query_url = settings.BEACON_ENDPOINT + 'query?' + urlencode(params_d, safe=',')
        LOG.debug('Forwarding to %s',query_url)

        r = requests.get(query_url)
        if not r:
            return render(request, 'error.html', {'message':'Backend not available' })

        response = None
        if r.status_code == 200:
            response = r.json()
        LOG.debug('Response: %s', response)

        ctx['response'] = response
        return render(request, 'info.html', ctx)


class BeaconAccessLevelsView(TemplateView):

    def get(self, request):

        query_url = settings.BEACON_ENDPOINT + 'access_levels'
        if request.GET:
            query_url += '?' + request.GET.urlencode()

        LOG.info('Contacting Beacon backend: %s', query_url)
        headers = { 'Accept': 'application/json',
                    'Content-type': 'application/json',
        }
        params = {}
        # if access_token: # we have a user
        #     params['auth'] = 'yes'
        #     headers['Authorization'] = 'Bearer ' + access_token

        resp = requests.get(query_url, headers=headers, params=params)
        if resp.status_code > 200:
            return render(request, 'error.html', {'message':'Backend not available' })

        ctx = resp.json()
        #LOG.debug(ctx.get('datasets'))
        ctx['includeFieldDetails'] = True if request.GET.get('includeFieldDetails', 'false') == 'true' else False
        ctx['includeDatasetDifferences'] = True if request.GET.get('includeDatasetDifferences', 'false') == 'true' else False

        # LOG.debug('GET includeFieldDetails: %s', request.GET.get('includeFieldDetails'))
        # LOG.debug('GET includeDatasetDifferences: %s', request.GET.get('includeDatasetDifferences'))
        # LOG.debug('GET includeFieldDetails ctx: %s', ctx['includeFieldDetails'])
        # LOG.debug('GET includeDatasetDifferences ctx: %s', ctx['includeDatasetDifferences'])
        return render(request, 'access_levels.html', ctx)
