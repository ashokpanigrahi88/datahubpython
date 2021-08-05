"""Template tag to get a model's name from a ModelForm"""
from django.template import Context, Template
from django import template
register = template.Library()


@register.simple_tag(name='variableinvariable', takes_context=True)
def variableinvariable(context, val):
    template = Template(val)
    context = Context(context)
    final_val = template.render(context)
    return final_val
