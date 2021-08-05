from django.db import connection
from django.conf import settings
import cx_Oracle


def get_location_id(request = None, defval:int = 0):
    if not request:
        return defval
    try:
        if 'locationid' not in request.session:
            request.session['locationid'] = request.user.location_id

        return int(request.session['locationid'])
    except:
        return defval

def getset_sessionval(request, p_key, p_val = None, p_default = None):
    if p_key in request.session:
        if not p_val:
            return request.session[p_key]
        else:
            request.session[p_key] = p_val
            return p_val
    else:
        request.session[p_key] = p_default
    return p_default
