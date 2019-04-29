import logging
from urllib.parse import urlencode
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
#from django.utils.safestring import mark_safe

from .info import BEACON_ASSEMBLYIDS  # same for everyone
LOG = logging.getLogger(__name__)


variantTypes = ('DEL:ME','INS:ME','DUP:TANDEM','DUP','DEL','INS','INV','CNV','SNP','MNP')
regex = re.compile(r'^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s+\:\s+(\d+)\s+([ATCGN]+)\s+\>\s+(DEL:ME|INS:ME|DUP:TANDEM|DUP|DEL|INS|INV|CNV|SNP|MNP|[ATCGN]+)$', re.I)
region_regex = re.compile(r'^(X|Y|MT|[1-9]|1[0-9]|2[0-2])\s+\:\s+(\d+)-(\d+)$', re.I)


def deconstruct_region_query(query):
    m = region_regex.match(query)
    if m:
        return { 'referenceName': m.group(1),
                 'start': m.group(2),
                 'end': m.group(3),
                 'referenceBases': 'N',
                 'alternateBases': 'N',
        }
    return None

def deconstruct_query(query):
    m = regex.match(query)
    if m:
        d = { 'referenceName': m.group(1),
              'start': m.group(2),
              'referenceBases': m.group(3),
        }
        v = m.group(4)
        k = 'variantType' if v in variantTypes else 'alternateBases'
        d[k] = v
        return d
    return None

class IncludeDatasetResponsesWidget(forms.RadioSelect):
    template_name='include_dataset_responses.html'
    
    
class QueryForm(forms.Form):

    assemblyId = forms.ChoiceField(required=True,
                                   choices=( (i,i) for i in BEACON_ASSEMBLYIDS ),
                                   error_messages = { 'invalid_choice': ('<p>Select a valid choice.</p>'
                                                                         '<p>%(value)s is not one of the available choices.</p>')},
                                   label='Assembly Id')

    query = forms.CharField(
        strip=True,
        required=True,
        label='Simplified Query',
        error_messages = { 'required': "<p>Eh? ... what was the query again?</p>"},
        widget=forms.TextInput(attrs={'data-lpignore':'true', # data-lpignore=true to ignore LastPass injected code
                                      'placeholder': 'For example  10 : 12345 A > T'}),
    )

    includeDatasetResponses = forms.ChoiceField(required=True,
                                                choices=( (i.upper(),i) for i in ('All','Hit','Miss','None') ),
                                                label='Included Dataset Responses',
                                                widget=IncludeDatasetResponsesWidget,
                                                initial='NONE')
    

    def is_valid(self):
        self.full_clean() # Populate fields (or read self.errors)

        # Short circuit already 
        if not super().is_valid():
            return False

        query = self.cleaned_data.get('query')
        LOG.debug('Query: %s', query)

        # So far so good
        self.query_deconstructed_data = None

        # Testing for Region Query
        res = deconstruct_region_query(query)
        if res: # Correct Region Query
            self.query_deconstructed_data = res
            return True

        # Testing the regular Query
        res = deconstruct_query(query)
        if res:
            self.query_deconstructed_data = res
            return True

        # Invalid query
        self.add_error('query', ValidationError(_('<p><code>%(value)s</code> must be of the form</p>'
                                                  '<ul>'
                                                  '<li><span class="query-form">Regular Query</span>Chromosome : Position ReferenceBase &gt; (AlternateBase|VariantType)</li>'
                                                  '<li><span class="query-form">Region Query</span>Chromosome : Start-End</li>'
                                                  '</ul>'
                                                  '<p>where</p>'
                                                  '<ul>'
                                                  '<li>Chromosome := 1-22, X, Y, or MT</li>'
                                                  '<li>Position := a positive integer</li>'
                                                  '<li>VariantType := either DEL:ME, INS:ME, DUP:TANDEM, DUP, DEL, INS, INV, CNV, SNP, or MNP</li>'
                                                  '<li>ReferenceBase or AlternateBase := A combination of one or more A, T, C, G, or N</li>'
                                                  '</ul>'),
                                                params={'value':query}))

        return False
