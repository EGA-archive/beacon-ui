import logging

from django import forms

LOG = logging.getLogger(__name__)

def chromosomes_choices():
    for i in range(1,22):
        yield (i,i)
    for i in ('X','Y','MT'):
        yield (i,i)

class QueryForm(forms.Form):

    # data-lpignore=true to ignore LastPass injected code

    # Datasets is coded by hand

    assemblyID = forms.CharField(label='Assembly Id',
                                 widget=forms.TextInput(attrs={'data-lpignore':'true', 'disabled':'true'}))

    referenceName = forms.ChoiceField(required=True,
                                      choices=chromosomes_choices,
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

    includeDatasetResponses = forms.BooleanField(label='Include Datasets in response',
                                                 required=False)
