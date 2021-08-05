"""Template tag to get a model's name from a ModelForm"""
from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    query = query.urlencode()
    return '&'.join([x for x in query.split('&') if not 'page' in x])
