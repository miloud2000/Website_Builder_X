from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring_without_sort(request):
    query = request.GET.copy()
    query.pop('sort_by', None)
    return urlencode(query)
