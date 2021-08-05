import csv
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from datetime import datetime
from common.sysutil import CHOICES


def nvl(val, retval):
    if val:
        return val
    if not val:
        return retval
    if val is None:
        return retval
    if val == "":
        return retval

def ifnull(val):
    if not val:
        return True
    if val == "":
        return True
    return False

def ifnegative(val:int):
    if val < int('0'):
        return True
    return False

def ifnegativeozero(val:int):
    if val == 0:
        return True
    return ifnegative(val)

def hasstrvalue(val:str):
    if val is None or val == "":
        return False
    return True

def hasintvalue(val:int):
    if val is None or str(val) == "":
        return False
    return True

def hasintnonaerovalue(val:int):
    if val is None or str(val) == "":
        return False
    try:
        if int(val) > 0:
            return True
    except:
        pass
    return False

def handleerroor(p_message, p_pos, p_errortype = 'INFO', p_source = "" , **kwargs):
    if p_errortype == "ERROR":
        raise Exception;
    print(p_message)

def debugmessage(p_message, p_pos, p_force:bool = False, p_errortype = 'INFO', p_source = "" , **kwargs):
    if p_force or settings.DEBUG:
        print(p_message, p_pos)

def handlemessages(p_message, **kwargs):
    return p_message

def succes(**kwargs):
    pass

def failed(p_ex:Exception, p_raise:bool = True, **kwargs):
    raise p_ex

def download_csv(request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied
    model = queryset.model
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    # the csv writer
    writer = csv.writer(response, delimiter=";")
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for row in queryset:
        values = []
        for field in field_names:
            value = getattr(row, field)
            if callable(value):
                try:
                    value = value() or ''
                except:
                    value = 'Error retrieving value'
            if value is None:
                value = ''
            values.append(value)
        writer.writerow(values)
    return response

def string_to_date(p_string:str, p_format:str = "%d-%m-%Y"):
    val = None
    try:
        if hasstrvalue(p_string):
            val = datetime.strptime(p_string, p_format )
    except:
        val = datetime.strptime(p_string, "%m/%d/%Y" )
    print(val)
    return val

def string_to_time(p_string:str, p_format:str = "%d-%m-%Y H:i:s"):
    val = None
    if hasstrvalue(p_string):
        val = datetime(p_string, p_format)
    print(val)
    return val

def strip_qty_filter(p_querydict:{},p_colname, p_val):
    columnstr = ""
    val = 0
    if hasstrvalue(p_val):
        columnstr = "{0}{1}".format(p_colname,
            p_val.replace('> 0', '__gt'
                        ).replace('< 0', '__lt'
                        ).replace('= 0', ''
                        ).replace('>= 0', '__gte').replace('<= 0', '__lte')
                                    )
    p_querydict[columnstr] = val

def filter_date_range(p_querydict:{},p_column:str, p_datefrom, p_dateto, p_type = 'str'):
    vdatefrom = p_datefrom
    vdateto = p_dateto
    try:
        if p_type == 'str':
            vdatefrom = string_to_date(p_datefrom)
            vdateto = string_to_date(p_dateto)
    except Exception as ex:
        debugmessage(ex,'filter_daate_range')
    if vdatefrom:
        p_querydict["{0}__gte".format(p_column)] = vdatefrom
    if vdateto:
        p_querydict["{0}__lte".format(p_column)] = vdateto

def filter_date(p_querydict:{},p_column:str, p_date, p_type = 'str'):
    vdate = p_date
    try:
        if p_type == 'str':
            vdate = string_to_date(p_date)
    except Exception as ex:
        debugmessage(ex)
    if vdate:
        p_querydict["{0}".format(p_column)] = vdate

def filter_add(p_querydict:{}, p_colname, p_val, p_cond:str = "" , p_type = 'str',p_force:bool = False,p_reset:bool=False):
        columnstr = None
        if p_reset:
            if hasstrvalue(p_val):
                p_querydict = {}
        val = p_val
        if not hasstrvalue(p_colname):
            return
        if hasstrvalue(p_cond):
            if p_cond == 'filter' and hasstrvalue(val):
                columnstr = "{0}{1}".format(p_colname,
                    p_val.replace('> 0', '__gt'
                        ).replace('< 0', '__lt'
                        ).replace('= 0', ''
                        ).replace('>= 0', '__gte').replace('<= 0', '__lte'))
                val = 0
            else:
                columnstr = "{0}__{1}".format(p_colname,p_cond)
        else:
            columnstr = "{0}".format(p_colname)
        if p_type == 'str':
            if hasstrvalue(val) or p_force:
                p_querydict[columnstr] = nvl(val,"")
        if p_type == 'int' or p_force:
            if hasintvalue(val):
                p_querydict[columnstr] = nvl(int(val),0)


def filter_numberorname(p_queryset, p_colname, p_val, p_cond1:str ="" , p_cond2:str = "__icontains"):
    queryset = p_queryset
    try:
        queryset = p_queryset.filter(**{"{0}{1}".format(p_colname,p_cond1):p_val}) \
                   | p_queryset.filter(**{"{0}{1}".format(p_colname,p_cond2):p_val})

    except Exception as ex:
        debugmessage(ex)
    finally:
        return queryset


def filter_numberandname(p_queryset, p_colname, p_val, p_cond1:str ="" , p_cond2:str = "__icontains"):
    queryset = p_queryset
    try:
        queryset = p_queryset.filter(**{"{0}{1}".format(p_colname,p_cond1):p_val}) \
                   & p_queryset.filter(**{"{0}{1}".format(p_colname,p_cond2):p_val})

    except Exception as ex:
        debugmessage(ex)
    finally:
        return queryset

def get_key_value(p_dict:{}, p_key:str):
    val = None
    try:
        val = p_dict[p_key]
    except Exception as ex:
        pass
    finally:
        return val

def iskeyempty(p_dict:{}, p_key:str):
    val = get_key_value(p_dict,p_key)
    try:
        if val.isdecimal():
            return hasintvalue(val)
        else:
            return hasstrvalue(val)
    except:
        pass
    finally:
        return False

def choice_modelcharfields(p_model=None, p_fields:[] =[] , p_exclude:[]= []):
    blankchoice = list((("",'-------'),))
    if not p_model:
        return blankchoice
    fields = [(f.name,f.name) for f in p_model._meta.get_fields() if f.get_internal_type() == 'CharField']
    fields.append(blankchoice[0])
    return  fields

def choice_modelfields(p_model=None, p_fields:[] =[] , p_exclude:[]= []):
    blankchoice = list((("",'-------'),))
    if not p_model:
        return blankchoice
    fields = ((f.name,f.name) for f in p_model._meta.get_fields() )
    fields.append(blankchoice[0])
    return  fields

def add_html_tag(p_val:str,p_open:str = "<th>", p_close:str = '</th>',p_prefix:str ="", p_suffix:str = ""):
    if hasstrvalue(p_val):
        return "{}{}{}{}{}".format(p_open,p_prefix,p_val,p_suffix,p_close)
    return ""


def filter_add_raw(p_where, p_colname, p_val,  p_operator:str = "=" , p_cond:str=' AND ',
                   p_type = 'str',p_force:bool = False):
        val = p_val
        if not hasstrvalue(p_colname):
            return p_where
        if not hasstrvalue(val):
            return p_where
        if not hasstrvalue(p_where):
            p_where = 'WHERE '
        else:
            p_where += p_cond
        if p_type == 'str':
            if hasstrvalue(p_operator):
                p_where += "{} {} '{}'".format(p_colname,p_operator,val)
            else:
                p_where += "{} {} {}".format(p_colname,p_operator,val)
        else:
            p_where += "{} {} {}".format(p_colname, p_operator, val)
        print('pwhere',p_where)
        return p_where

def filter_date_range_raw(p_where,p_column:str, p_datefrom, p_dateto, p_type = 'str'):
    vdatefrom = p_datefrom
    vdateto = p_dateto
    try:
        if p_type == 'str':
            vdatefrom = string_to_date(p_datefrom)
            vdateto = string_to_date(p_dateto)
    except Exception as ex:
        debugmessage(ex,'filter_daate_range')
    if not hasstrvalue(p_where):
        p_where = 'WHERE '
    else:
        p_where += ' AND '
    if vdatefrom:
         vdatefrom = "to_date('{}', '{}')".format( p_datefrom ,'DD-MM-YYYY')
         p_where = "{} {} {} {} ".format(p_where, p_column , '>=' , vdatefrom)
    if vdateto:
         vdateto = "to_date('{}', '{}')".format(p_dateto ,'DD-MM-YYYY')
         p_where = "{} {} {} {} ".format(p_where, p_column , '<=' , vdateto)
    return p_where


def initalise_find_form(p_form, p_initial:{} = {} ):
    if not p_initial:
        return p_form()

    newinitial = {}
    for key in p_initial.keys():
        if not key.endswith('_id'):
            newinitial[key] = p_initial[key]
    return p_form(initial=newinitial)

def initalise_form(p_initial:{} = {} ):
    if not p_initial:
        return {}
    newinitial = {}
    print(p_initial)
    for key in p_initial.keys():
        if key.endswith('_id'):
            newinitial[key] = None
        else:
            newinitial[key] = p_initial[key]
    print(newinitial)
    return newinitial