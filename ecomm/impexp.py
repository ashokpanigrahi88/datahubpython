import requests
import common.submodels.imp_models as impmodels

END_POINT_BASE_URL ='http://127.0.0.1:8000/rest-api/'


def get_data(p_endpoint:str = 'itemexp',p_parameters:str = ""):
    endpointurl = END_POINT_BASE_URL+p_endpoint+'/'
    if len(p_parameters) > 0:
        endpointurl = endpointurl+'?'+p_parameters
    print('endpointurl', endpointurl)
    data = requests.get(endpointurl)
    return data

def get_model_fields(p_model):
    fields = {f.name:'' for f in p_model._meta.get_fields()}
    return fields

def get_nonblank_fields(p_data:{}):
    data = {k: v for k, v in p_data.items() if isinstance(v, str) and len(v) > 0}
    return data

def get_onlymodel_fields(p_data:{}, p_modelfields:{}):
    nonblankdata = get_nonblank_fields(p_data)
    data = {k: v for k, v in nonblankdata.items() if k in p_modelfields.keys()}
    return data

def import_items(p_primarykey:{} = {'imp_item_id':None},p_parameters:str = ""):
    error_position  = 'start'
    item = {}
    modelfields = get_model_fields(impmodels.ImpItems)
    error_position ='1a'
    try:
        data = get_data(p_endpoint='itemexp',p_parameters=p_parameters)
        results = data.json()['results']
        error_position ='1b'
        for result in results:
            if result == {}:
                print('nothing to import')
                break;
            item = get_onlymodel_fields(result,modelfields)
            error_position = '1c'
            item.update(p_primarykey)
            iteminstance = impmodels.ImpItems(**item)
            error_position ='1d'
            iteminstance.save()
    except Exception as ex:
        print('import_items:',error_position, ex)
