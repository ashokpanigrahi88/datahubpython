"""Template tag to get a model's name from a ModelForm"""
from django import template
from common.models import CmnUsers
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag(takes_context=True)
def get_responsibilities(context, **kwargs):
    request = context['request']
    respmenu = None
    if request.user == 'AnonymousUser':
        return
    try:
        userid = request.user.user_id
        request.session['locationid'] = request.user.location_id
        user = CmnUsers.objects.get(user_id=userid)
        print('user',user)
        if 'RESPMENU' in request.session:
            print('in session')
            respmenu = request.session['RESPMENU']
            return mark_safe(respmenu)
        print('not in session')
        respmenu = user.get_respmenu(userid)
        request.session['RESPMENU'] = respmenu
        return mark_safe(respmenu)
    except Exception as e:
        print('user not loggedin',e)
        return