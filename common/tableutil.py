from common.moduleattributes import table_fields

commonexclusions = ['bu_id','created_by','delete_flag','creation_date','last_update_date','last_updated_by',
                    'record_status','update_source']

def exclude_columns(p_columns:[] = [],p_commonexclusions:bool = True):
    exclude = []
    if p_commonexclusions:
        exclude = commonexclusions
    if not p_columns:
        exclude.append(p_columns)
    return exclude

def get_tablemeta(p_table:{}, p_key:str = 'felds'):
    try:
        return p_table[p_key]
    except:
        return None

def include_columns(p_table:{}, p_excludecolumns:[] = [],p_commonexclusions:bool = True):
    include = []
    exclude = []
    fields = get_tablemeta(p_table,'fields')
    if not fields:
        return []
    if p_excludecolumns:
        exclude.append(p_excludecolumns)
    if p_commonexclusions:
        exclude.append(p_commonexclusions)
    incluse = [field for field in fields if field not in exclude]
    return include





