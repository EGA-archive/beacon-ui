from io import StringIO
import pprint as pretty_print

from django import template

register = template.Library()

@register.filter
def pprint(d):
    s = StringIO()
    pretty_print.pprint(d, s, indent=4)
    return s.getvalue()
