import logging
import os
import json
import uuid
import base64
from urllib.parse import urlencode

import requests
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect, QueryDict
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth import logout
from django.core.cache import cache

from . import info  # will prefetch the beacon info
from .forms import QueryForm


LOG = logging.getLogger(__name__)

####################################

def clean_empty_strings(iterable):
    for item in iterable:
        item = item.strip()
        if item:
            yield item
    

class BeaconView(TemplateView):

    # If the user is not logged-in, the beacon_info is already cached
    @info.fetch
    def get(self, request, beacon_info):

        form = QueryForm()
        if settings.DEBUG:
            q = QueryDict(mutable=True)
            q['query'] = "1 : 23 A > T"
            q['assemblyId'] = 'GRCh37'
            q['includeDatasetResponses'] = 'ALL'
            form = QueryForm(q)

        ctx = { 'form': form,
                'beacon': beacon_info,
                'assemblyIds': info.BEACON_ASSEMBLYIDS, # same for everyone
                'selected_datasets': [],
                'filters': [] if not settings.DEBUG else ["HP:0011007>=49", "PATO:0000383", "EFO:0009656"],
        }
        return render(request, 'info.html', ctx)

    @info.fetch
    def post(self, request, beacon_info):

        form = QueryForm(request.POST)

        selected_datasets = set(request.POST.getlist("datasets", []))
        filters = set( clean_empty_strings( request.POST.getlist("filters", []) ) )

        LOG.debug('selected_datasets: %s', selected_datasets )
        LOG.debug('filters: %s', filters )

        ctx_base = { 'assemblyIds': info.BEACON_ASSEMBLYIDS, # same for everyone
                     'beacon': beacon_info,
        }
        
        ctx = ctx_base.copy()
        ctx['form'] = form
        ctx['selected_datasets'] = selected_datasets
        ctx['filters'] = filters

        # Form validation... for the regex
        if not form.is_valid():
            return render(request, 'info.html', ctx)

        # Valid Form 
        params_d = form.query_deconstructed_data
        LOG.debug('Deconstructed Data: %s', params_d)

        # These are required
        params_d['includeDatasetResponses'] = form.cleaned_data.get('includeDatasetResponses')
        params_d['assemblyId'] = form.cleaned_data.get('assemblyId') 

        #params_d['datasets'] = ','.join(selected_datasets) if selected_datasets else 'all'
        if selected_datasets:
            params_d['datasets'] = ','.join(selected_datasets) 
        if filters:
            params_d['filters'] = ','.join(filters)

        # Don't check anything and forward to backend
        
        query_url = os.getenv('BEACON_QUERY_ENDPOINT')
        if not query_url:
            return render(request, 'error.html', {'message':'BEACON_QUERY_ENDPOINT environment variable missing' })
 
        query_url += urlencode(params_d, safe=',')
        LOG.debug('Forwarding to %s',query_url)

        r = requests.get(query_url)
        if not r:
            return render(request, 'error.html', {'message':'Backend not available' })

        response = None
        if r.status_code == 200:
            response = r.json()
        LOG.debug('Response: %s', response)

        ctx['response'] = response
        ctx['query_url'] = query_url

        # key = make_cache_key(chain([user_id], params_d.keys(), params_d.value()))
        # cache.set(key, ctx)
        oldResults = request.session.get('oldResults', [])
        ctx_base['query_url'] = query_url
        ctx_base['response'] = response
        oldResults.append({
            'ctx': ctx_base,
            'formdata': request.POST,
        })
        request.session['oldResults'] = oldResults
        LOG.debug('Adding history to session [%d items]', len(request.session['oldResults']))
        return render(request, 'info.html', ctx)


class BeaconHistoryView(TemplateView):

    def get(self, request, index):

        LOG.debug('Replay %d', index)
        oldResults = request.session.get('oldResults', [])

        try:
            item = oldResults[index-1] # 1-based (cuz of url patterns) => 0-based
            #LOG.debug('History item: %s', item)
            formdata = item['formdata']
            LOG.debug('History form data: %s', formdata)
            selected_datasets = set(formdata.getlist("datasets", []))
            filters = set( f for f in formdata.getlist("filters", []) if f )

            ctx = item['ctx']
            ctx['form'] = QueryForm(formdata)
            ctx['selected_datasets'] = selected_datasets
            ctx['filters'] = filters

            return render(request, 'info.html', ctx)
        except IndexError as e:
            return render(request, 'error.html', { 'message': 'Nice try... you do not have history item number {}'.format(index)})
            
            
        
class BeaconAccessLevelsView(TemplateView):

    def get(self, request):

        query_url = os.getenv('BEACON_ACCESS_LEVELS_ENDPOINT')
        if not query_url:
            return render(request, 'error.html', {'message':'BEACON_ACCESS_LEVELS_ENDPOINT environment variable missing' })

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
