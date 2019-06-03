import logging
import os
import json
import uuid
import base64
from urllib.parse import urlencode

import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth import logout

from . import info  # will prefetch the beacon info
from . import forms


LOG = logging.getLogger(__name__)

####################################

def clean_empty_strings(iterable):
    for item in iterable:
        item = item.strip()
        if item:
            yield item

####################################

class BaseView(TemplateView):

    # If the user is not logged-in, the beacon_info is already cached
    @info.fetch
    def get(self, request, beacon_info):

        form = getattr(forms, self.formbase)()

        ctx = { 'form': form,
                'beacon': beacon_info,
                'assemblyIds': info.BEACON_ASSEMBLYIDS, # same for everyone
                'selected_datasets': set(),
                'filters': set(),
        }
        return render(request, 'index.html', ctx)

    @info.fetch
    def post(self, request, beacon_info):
 
        form = getattr(forms, self.formbase)(request.POST)

        selected_datasets = set(request.POST.getlist("datasetIds", []))
        LOG.debug('selected_datasets: %s', selected_datasets )
        filters = set( clean_empty_strings( request.POST.getlist("filters", []) ) )
        LOG.debug('filters: %s', filters )

        ctx = { 'form': form,
                'beacon': beacon_info,
                'assemblyIds': info.BEACON_ASSEMBLYIDS, # same for everyone
                'selected_datasets': selected_datasets,
                'filters': filters,
        }

        # Form validation... for the regex
        if not form.is_valid():
            return render(request, 'index.html', ctx)

        # Valid Form 
        params_d = form.query_deconstructed_data
        LOG.debug('Deconstructed Data: %s', params_d)

        #params_d['datasets'] = ','.join(selected_datasets) if selected_datasets else 'all'
        if selected_datasets:
            params_d['datasetIds'] = ','.join(selected_datasets) 
        if filters:
            params_d['filters'] = ','.join(filters)

        # Don't check anything and forward to backend        
        query_url = self.api_endpoint
        if not query_url:
            return render(request, 'error.html', { 'message': self.api_endpoint_error })
 
        query_url += urlencode(params_d, safe=',')
        LOG.debug('Forwarding to %s',query_url)

        # Access token
        headers = {}
        access_token = request.session.get('access_token')
        if access_token:
            headers['Authorization'] = 'Bearer ' + access_token
        else:
            LOG.debug('No Access token supplied')
        
        # Forwarding the request to the Beacon API
        r = requests.get(query_url,headers)
        if not r:
            return render(request, 'error.html', {'message':'Beacon backend API not available' })

        response = None
        if r.status_code == 200:
            response = r.json()

        #LOG.debug('Response: %s', response)

        ctx['response'] = response
        ctx['query_url'] = query_url
        ctx['beacon_query'] = { 'params': params_d, 
                                'exists': 'Y' if response.get('exists', False) else 'N'
        }

        return render(request, 'index.html', ctx)



class BeaconQueryView(BaseView):
    formbase = 'QueryForm'
    api_endpoint = settings.CONF.get('beacon-api', 'query')
    api_endpoint_error = '[beacon-api] query endpoint misconfigured'
    # cheat_data = {
    #     'query': "1 : 13272 G > C",
    #     'assemblyId': 'grch37',
    #     'includeDatasetResponses': 'ALL',
    #     #'filters': ['ICD-10:XVI'],
    #     'filters': ['PATO:0000383', 'HP:0011007>=49', 'EFO:0009656'],
    # }

class BeaconSNPView(BaseView):
    formbase = 'QueryForm'
    api_endpoint = settings.CONF.get('beacon-api', 'genomic_snp')
    api_endpoint_error = '[beacon-api] genomic_snp endpoint misconfigured'
    # cheat_data = {
    #     'query': "1 : 13272 G > C",
    #     'assemblyId': 'GRCh37',
    #     'includeDatasetResponses': 'HIT',
    #     'filters': ['csvs.tech:1','csvs.tech:3'],
    # }

class BeaconRegionView(BaseView):
    formbase = 'QueryRegionForm'
    api_endpoint = settings.CONF.get('beacon-api', 'genomic_region')
    api_endpoint_error = '[beacon-api] genomic_region endpoint misconfigured'
    # cheat_data = {
    #     'query': "1 : 14900 - 15000",
    #     'assemblyId': 'grch37',
    #     'includeDatasetResponses': 'ALL',
    # }


class BeaconAccessLevelsView(TemplateView):

    @info.fetch
    def get(self, request, beacon_info):

        query_url = settings.CONF.get('beacon-api', 'access_levels', default=None)
        if not query_url:
            return render(request, 'error.html', {'message':'[beacon-api] access_levels is misconfigured' })

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

        ctx['beacon'] = beacon_info

        ctx['fieldsParam'] = True if request.GET.get('includeFieldDetails', 'false') == 'true' else False
        ctx['datasetsParam'] = True if request.GET.get('displayDatasetDifferences', 'false') == 'true' else False

        return render(request, 'access_levels.html', ctx)
