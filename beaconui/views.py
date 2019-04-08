import logging
import os
import json
import requests

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import TemplateView
from django.conf import settings

from .forms import QueryForm

LOG = logging.getLogger(__name__)

class EGABeaconInfoView(TemplateView):

    def get(self, request):

        query_url = settings.BEACON_INFO_ENDPOINT
        LOG.debug('Forwarding to %s',query_url)

        r = requests.get(query_url)
        if not r:
            return render(request, 'error.html', {'message':'Backend not available' })

        data = r.json()
        # LOG.debug(data)

        form = QueryForm(label_suffix="")

        all_ds = 0
        datasets = data.get('datasets')
        if datasets:
            all_ds = sum( (d['variantCount'] for d in datasets if d['info']['accessType'] == 'PUBLIC') )
        return render(request, 'index.html', {'form':form, 'datasets':datasets, 'all_ds': all_ds })

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

