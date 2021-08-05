"""Template tag to get a model's name from a ModelForm"""
from django.template import Context, Template
from django import template
from common.translation import (VN_C,VN_T)
register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_instance_field_value(instance, field):
    try:
        return getattr(instance,field)
    except:
        print(field,'not found in', instance)
        return ''


@register.simple_tag(name='getverbose', takes_context=True)
def getverbose(context, val):
    return VN_C(val)


@register.filter(name='verbosename')
def verbosename(val):
    return VN_C(val)


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()