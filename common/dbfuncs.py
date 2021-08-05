from django.db import connection
from django.conf import settings
from common import (commonutil)
from common.models import CmnUsers
import cx_Oracle


def allrowsto_dict(cursor,columnscase:str = 'UPPER'):
    "Return all rows from a cursor as a dict"
    if columnscase == 'lower':
        columns = [col[0].lower() for col in cursor.description]
    else:
        columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def rowto_dict(cursor, p_rettype = 'tuple'):
    "Return all rows from a cursor as a dict"
    if p_rettype != 'dict':
        return cursor.fetchall()
    columns = [col[0].lower() for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def singlerowto_dict(cursor,p_rettype = 'dict'):
    "Return all rows from a cursor as a dict"
    try:
        if p_rettype != 'dict':
            return cursor.fetchone()
        columns = [col[0].lower() for col in cursor.description]
        return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
            ][0]
    except Exception as ex:
        print(ex)
        return {}

def get_fuzzyserch(fuzzyword:str ,**kwargs):
    with connection.cursor() as cursor:
        return  cursor.callfunc("Inv_Pkg.item_FuzzySearch", str, [fuzzyword])


def exec_int_func(funcame:str, param:[] ,**kwargs):
    #cursor.callproc("so_test", keywordParameters = dict(p2 = "Y", p3 = "Z"))
    with connection.cursor() as cursor:
        if kwargs:
            val = cursor.callfunc(funcame, int, keywordParameters = kwargs)
        else:
            val = cursor.callfunc(funcame, int, param)
        return val

def exec_str_func(funcame:str, param:[], **kwargs):
    #cursor.callproc("so_test", keywordParameters = dict(p2 = "Y", p3 = "Z"))
    val = None
    with connection.cursor() as cursor:
        if kwargs:
            val = cursor.callfunc(funcame, str, keywordParameters=kwargs)
        else:
            val = cursor.callfunc(funcame, str, param)
    return val


def exec_proc(procname:str,  param: [], **kwargs):
    #cursor.callproc("so_test", keywordParameters = dict(p2 = "Y", p3 = "Z"))
    with connection.cursor() as cursor:
        if kwargs:
            val = cursor.callproc(procname, keywordParameters=kwargs)
        else:
            val = cursor.callproc(procname, param)
        return val

def exec_sql(sql:str, rettype:str = 'dict' , rows = -1, columnscase:str = 'UPPER' , **kwargs):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if rows == 1:
                return singlerowto_dict(cursor,p_rettype=rettype)
            if rettype == 'dict':
                return allrowsto_dict(cursor,columnscase)
            return cursor.fetchall()
    except Exception as ex:
        print(ex)
        return []

def exec_sqlraw(sql:str, rettype:str = 'dict' , rows = -1 , **kwargs):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if rows == 1:
                return singlerowto_dict(cursor,p_rettype=rettype)
            return rowto_dict(cursor=cursor,p_rettype=rettype)
    except Exception as ex:
        print(ex)
        return []

def select_sqlfunc(funcname :str ,**kwargs):
    with connection.cursor() as cursor:
        sql = "SELECT " + funcname + " val  from DUAL"
        print(sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        print(row,row[0])
        return row[0]

def exec_plsqlblock(p_block :str ,**kwargs):
    try:
        with connection.cursor() as cursor:
            block = """
            BEGIN  
            {}  
            END;
            """.format(p_block)
            cursor.execute(block)
    except Exception as ex:
        print(ex)
        commonutil.handleerroor(ex)


def exec_plsqlblockraw(p_block:str, **kwargs):
    try:
        with connection.cursor() as cursor:
            block = """{}
                    """.format(p_block)
            cursor.execute(block)
    except Exception as ex:
        print(ex)
        commonutil.handleerroor(ex)

def get_lookupattribute(lookuptype:str, lookupcode:str, attr:int = 1, defval = None ):
    retval = None
    with connection.cursor() as cursor:
        retval = cursor.callfunc('Cmn_Common_Pkg.Get_LookupAttributeValues'
                                , str , [lookuptype,lookupcode,attr])
        if retval is None:
            return defval
        return retval


def get_itemprice(price:int, suid:int, itemid:int = None):
    priceincvat  = exec_int_func('price_pkg.get_susp',[itemid,suid,price, 'VAT'])
    priceexlvat   = exec_int_func('price_pkg.get_susp',[itemid,suid,price,'NOVAT'])
    return priceincvat, priceexlvat


def get_sublocation_id(locationid, sublocation):
    return select_sqlfunc("Mobile_Pkg.get_SubLocationId({0},upper('{1}'))".format(locationid, sublocation))

def get_default_sublocationid(locationid, itemid, locgroup:str ='PRIMARY SALES'):
    return select_sqlfunc("Location_Pkg.Get_ItemDefSubLocByGroup({0},{1},{2})".format(
                     locationid, itemid,locgroup))

def get_externallocation():
    return  select_sqlfunc("cmn_common_Pkg.Get_DefaultLookupCode('ITEM_EXTERNAL_LOCATIONS')")

def get_primarysubloc(subloctype:str = 'PRIMARY SALES', locationid:int = 1):
    return select_sqlfunc("Location_Pkg.Get_PrimarySubLoc('{0}',{1})".format('PRIMARY GRN',
                                               locationid))

def get_username(userid):
    if commonutil.hasintvalue(userid):
        user = CmnUsers.objects.get(user_id=userid)
        if not user:
            return user[0].user_name
    return "unknown"

def is_db_object_exists(p_objectname):
    val = 0
    retval = exec_sql("Select nvl(count(1),0) val from user_objects where object_name = '{}'".format(p_objectname), columnscase='lower')
    if len(retval) > 0:
        val = retval[0]['val']
    return val

def is_constraint_exists(p_objectname):
    val = 0
    retval = exec_sql("Select nvl(count(1),0) val from user_constraints where constraint_name = '{}'".format(p_objectname), columnscase='lower')
    if len(retval) > 0:
        val = retval[0]['val']
    return val

def get_col_def(p_tablename, p_columnname):
    sql = """select tname object_name,  cname column_name, coltype data_type,
                nvl(To_Char(Decode(coltype,'NUMBER',Precision,width)),'10') data_width,
                nvl(To_Char(Decode(coltype,'NUMBER',Scale,Precision)),'0') data_precision,
                defaultval  , decode(nulls,'NULL','True','False') nullable 
              from col
              Where tname = '{}'
              and   cname = '{}'
                """.format(p_tablename,p_columnname)
    retval = exec_sql(sql, columnscase='UPPER')
    if len(retval) > 0:
        retval = retval[0]
        defaultval = retval['DEFAULTVAL']
        if not commonutil.hasstrvalue(defaultval):
            retval['DEFAULTVAL'] = 'None'
        try:
            if 'NEXTVAL' in defaultval:
                defaultval = '.'.join(defaultval.split('.')[1:])
                retval['DEFAULTVAL'] = defaultval
        except:
            pass
        finally:
            return retval
    return {}