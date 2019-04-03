import logging
import os
import json

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import TemplateView
#from django.conf import settings

LOG = logging.getLogger(__name__)

class EGABeaconInfoView(TemplateView):

    def get(self, request):
        return render(request, 'index.html', {})

