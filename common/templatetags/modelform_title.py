"""Template tag to get a model's name from a ModelForm"""
from django import template
register = template.Library()


@register.filter
def modelform_title(modelform):
    """Returns a modelform's titlized Model.verbose_name"""
    return modelform._meta.model._meta.verbose_name.title()
