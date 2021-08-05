from common.models import (CmnSysOptions,ArOptions, ApOptions,InvOptions,CmnUsers,
                              CmnCompanies,CmnBusinessUnits,
                              InvLocations)
from common import commonutil
import logging


def get_sessionvars(p_model , p_filterby:{} = {},p_rettype = 'selectdict'):
    try:
        model = p_model
        data = model.objects.all()
        if p_filterby != {}:
            data = data.filter(**p_filterby)
        if len(data) > 0:
            return data.values[0]
    except Exception as ex:
        print(ex)
        logging.error('SESSION VAR-{}-{}'.format(p_model,ex))
        return {}

def get_defaultlocation(p_userdict={}):
    try:
        locationid = commonutil.get_key_value(p_userdict, 'location_id')
        if not commonutil.hasstrvalue(locationid):
            locationid = commonutil.get_key_value(SESSION_SYS_OPTIONS, 'location_id')
        if not commonutil.hasstrvalue(locationid):
            location = get_sessionvars(InvLocations)
            locationid = commonutil.get_key_value(location, 'location_id')
        else:
            location = get_sessionvars(InvLocations, p_filterby={'location_id': locationid})
        return locationid, location
    except Exception as ex:
        logging.error('session location id-'+ex)
        return -1, {}

def get_lookupcodes(p_lookuptype:str = None):
    if p_lookuptype is None:
        return {}
    try:
        result = {}
        with db.connection as connection:
            results = connection.execute(""" Select lookup_code,lookup_meaning,description,
                                    attribute1,attribute2,attribute3,attribute4
                                    From cmn_lookup_codes Where clt_lookup_type ='{}' """.format(p_lookuptype))
            for row in results:
                result[row.lookup_code.lower()] = dict(zip(row.keys(),row.values()))
        return result
    except Exception as ex:
        print(ex)
        logging.error('item defaults-{}'.format(ex))
        return result

SESSION_SYS_OPTIONS = get_sessionvars(CmnSysOptions)
SESSION_AP_OPTIONS = get_sessionvars(ApOptions)
SESSION_AP_OPTIONS = get_sessionvars(ApOptions)
SESSION_AR_OPTIONS = get_sessionvars(ArOptions)
SESSION_INV_OPTIONS = get_sessionvars(InvOptions)
SESSION_COMPANY  = get_sessionvars(CmnCompanies)
SESSION_BUSINESSUNIT = get_sessionvars(CmnBusinessUnits, p_filterby={
                    'cc_comp_id': commonutil.get_key_value(SESSION_COMPANY, 'comp_id')})
SESSION_USER = get_sessionvars(CmnUsers,p_filterby={'user_id':etl_settings.IMPEXP_USER_ID})
SESSION_LOCATION_ID ,SESSION_LOCATION  = get_defaultlocation(SESSION_USER)
ITEM_DEFAULTS = get_lookupcodes('ITEM_DEFAULTS')

def get_lookup_val(p_lookup:{} = {},p_lookupcode:str = None, p_key:str ='attribute1',p_default:str =""):
    val = p_default
    if p_lookupcode is None:
        return val
    try:
        val = p_lookup[p_lookupcode][p_key]
        return val
    except Exception as ex:
        print(ex)
        return val
