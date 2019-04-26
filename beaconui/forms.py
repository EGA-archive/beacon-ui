from urllib.parse import urlencode
from itertools import chain

from django.http import QueryDict
from django import forms
from django.conf import settings

class SimplifiedQueryForm(forms.Form):

    # data-lpignore=true to ignore LastPass injected code

    assemblyID = forms.ChoiceField(required=True,
                                   choices=( (i,i) for i in settings.BEACON_ASSEMBLYIDS ),
                                   label='Assembly Id')

    query = forms.RegexField(required=True,
                             label='Simplified Query',
                             widget=forms.TextInput(attrs={'data-lpignore':'true',
                                                           'placeholder': '10 : 12345 A > T'}),
                             strip = True,
                             regex = r'')

    


class QueryForm(forms.Form):

    extended = forms.BooleanField(required=False, initial=True)

    # data-lpignore=true to ignore LastPass injected code

    assemblyId = forms.ChoiceField(required=True,
                                   choices=( (i,i) for i in settings.BEACON_ASSEMBLYIDS ),
                                   label='Assembly Id')

    referenceName = forms.ChoiceField(required=True,
                                      choices=( (i,i) for i in chain( range(1,22),('X','Y','MT')) ),
                                      label='Reference Name')

    start    = forms.IntegerField(required=False, label='Start')
    startMin = forms.IntegerField(required=False, label='Start Min')
    startMax = forms.IntegerField(required=False, label='Start Max')

    end    = forms.IntegerField(required=False, label='End')
    endMin = forms.IntegerField(required=False, label='End Min')
    endMax = forms.IntegerField(required=False, label='End Max')


    referenceBases = forms.CharField(required=True, label='Reference Bases',
                                     widget=forms.TextInput(attrs={'data-lpignore':'true',
                                                                   'pattern':"[ACTG]+"}))

    alternateBases = forms.CharField(required=False, label='Alternate Bases',
                                     widget=forms.TextInput(attrs={'data-lpignore':'true',
                                                                   'pattern':"[ACTG]+"}))

    variantType = forms.CharField(required=False, label='Variant Type',
                                     widget=forms.TextInput(attrs={'data-lpignore':'true'}))

    includeDatasetResponses = forms.ChoiceField(required=True,
                                                choices=( (i,i) for i in ('All','Hit','Miss','None') ),
                                                label='Included Dataset Responses')


class BeaconQueryDict():

    multiple_fields = ("datasets", "filters")

    # Translate true and false strings to boolean values.
    values = {'true': True, 'false': False, 'on': True, 'off': False}

    def __init__(self, data):
        self.data = data or QueryDict()

    def to_dict(self):
        
        d = {}
        for k in self.data:

            if k == 'csrfmiddlewaretoken':
                continue

            if k in self.multiple_fields:
                v = [v for v in self.data.getlist(k) if v] # might be an array of empty values
                if v: # if someone survived
                    d[k] = v
                continue

            value = self.data.get(k)
            if value:
                if isinstance(value, str):
                    value = self.values.get(value.lower(), value)
                d[k] = value
        return d

    def serialize(self):
        d = {}
        for k in self.data:

            if k == 'csrfmiddlewaretoken':
                continue

            if k in self.multiple_fields:
                v = [v for v in self.data.getlist(k) if v] # might be an array of empty values
                if v: # if someone survived
                    d[k] = ','.join(v)
                continue

            value = self.data.get(k)
            if value:
                d[k] = value
        return urlencode(d, safe=',')

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.serialize())



