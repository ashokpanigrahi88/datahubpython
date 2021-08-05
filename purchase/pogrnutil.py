from django.db import (connection, models)
from common.models import (ArSalesorderHeaders,ArSalesorderLines)
from common import dbfuncs as dbfuncs
from common import (commonutil, dbfuncs)
from common.models import (ApSuppliers, PoOrderpadHeaders,PoLines, PoGrnHeaders, PoGrnLines)


def getpomodelrow(p_model = models.Model,p_colname:str ="", p_string:str = "", p_number:int = 0, records:int = 0):
    rec = None
    searchstring = ""
    try:
        if not p_model:
            return rec
        if not commonutil.hasstrvalue(p_colname):
            return rec
        if commonutil.hasintvalue(p_number):
            searchstring = "{0}".format(p_colname)
            rec = p_model.objects.all().filter( **{searchstring: p_number})
        if commonutil.hasintvalue(p_string):
            searchstring = "{0}__exact".format(p_colname)
            rec = p_model.objects.all().filter(**{searchstring: p_string})
            #rec = p_model.objects.filter(grn_number__exact=p_string)
        if rec:
            return rec[records]
        return rec
    except Exception as error:
        print(error)
        return error

def get_poheaderdetail(p_number:str = "" , p_id:int = 0 , p_model = PoOrderpadHeaders):
    rec = None
    if  commonutil.hasstrvalue(p_number):
        rec = p_model.objects.all().filter(po_number__exact=p_number)
    elif commonutil.hasintvalue(p_id):
        rec = p_model.objects.all().filter(po_header_id=p_id)
    if rec:
        return rec[0]
    return rec


def get_polinedetail(p_number:str = "" , p_id:int = 0 , p_model = PoLines):
    rec = None
    if  commonutil.hasstrvalue(p_number):
        rec = p_model.objects.all().filter(po_number__exact=p_number)
    elif commonutil.hasintvalue(p_id):
        rec = p_model.objects.all().filter(po_header_id=p_id)
    if rec:
        return rec[0]
    return rec

def createnewgrn(p_userid:int, p_supplierid:int, p_locationid:int, p_deliveryref:str, p_buid:int = 1 ):
    print('ingrn')
    try:
        with connection.cursor() as cursor:
            grnid = cursor.var(int)
            message = cursor.var(str)
            cursor.execute("""
                begin
                    :outgrnid := GRN_PKG.CreateGRN_Header(
                    p_GrnUserId => :userid,
                    p_supplierid => :supplierid,
                    p_shiptolocationid => :locationid,
                    p_DeliveryNoteRef => :deliverynoteref,
                    p_message => :outmessage);
                end;""", outgrnid=grnid, userid=p_userid, supplierid=p_supplierid,locationid=p_locationid, \
                         deliverynoteref=p_deliveryref,  outmessage=message)
            return grnid.getvalue(), message.getvalue()
    except Exception as error:
        print(error)
        return -1,  error

def additemtogrn(p_itemnumber:str, p_userid:int, p_grnid:int, p_itemid:int, p_quantity:int ,  p_buid:int = 1 ):
    itemid = p_itemid
    message = "Invalie value enetered {0}  on {1}"
    if not commonutil.hasintvalue(p_itemid):
        itemid = dbfuncs.select_sqlfunc("Inv_Pkg.GetItemIdBybarcode('{0}')".format(p_itemnumber))
    try:
        if not commonutil.hasintvalue(itemid):
            message = message.format('Item Number', p_itemnumber)
            raise ValueError
        if not commonutil.hasintvalue(p_grnid):
            message = message.format('GRN ID', p_grnid)
            raise ValueError
    except Exception as error:
        return -1,  message

    try:
        message = dbfuncs.exec_str_func("Mobile_Pkg.GRN_SingleItem",[p_grnid, itemid, p_quantity])
        print(message)
        return 1, message
    except Exception as error:
        print(error)
        return -1, error


def additemtogrnold(p_itemnumber:str, p_userid:int, p_grnid:int, p_itemid:int, p_quantity:int ,  p_buid:int = 1 ):
    itemid = p_itemid
    message = "Invalie value enetered {0}  on {1}"
    if not commonutil.hasintvalue(p_itemid):
        itemid = dbfuncs.select_sqlfunc("Inv_Pkg.GetItemIdBybarcode('{0}')".format(p_itemnumber))
    try:
        if not commonutil.hasintvalue(itemid):
            message = message.format('Item Number', p_itemnumber)
            raise ValueError
        if not commonutil.hasintvalue(p_grnid):
            message = message.format('GRN ID', p_grnid)
            raise ValueError
    except Exception as error:
        return -1,  message

    try:
        with connection.cursor() as cursor:
            grnlineid = cursor.var(int)
            message = cursor.var(str)
            print('adding item')
            cursor.execute("""
                begin
                    :outgrnlineid := GRN_PKG.AddItem_To_GRN(
                    p_UserID => :userid,
                    p_PghGrnId  => :grnid,
                    p_QtyGoodsin  => :qty
                    p_ItemId => :itemid,
                    p_message => :outmessage);
                end;""", outgrnlineid=grnlineid, userid=p_userid, grnid=p_grnid,qty=p_quantity, itemid=itemid,  outmessage=message )
            print(grnlineid.getvalue() )
            return grnlineid.getvalue(), message.getvalue()
    except Exception as error:
        print(error)
        return -1,  error

def get_grnidbynumber(p_grnnumber:str):
    val = None
    if not commonutil.hasstrvalue(p_grnnumber):
        return None
    val = dbfuncs.select_sqlfunc("GRN_PKG.Get_GRNIDByNumber('{0}')".format(p_grnnumber))
    print('grnval',val)
    return val

def ceategrn_frompo(p_userid:int, p_poheaderid:int, p_ponumber:str):
    grnid = int()
    try:
        with connection.cursor() as cursor:
            outgrnid = cursor.var(int).var
            print('Creating Grn From PO')
            message = dbfuncs.exec_str_func("GRN_PKG.Create_FromPO", [p_userid, p_poheaderid,  p_ponumber, outgrnid ])
            grnid = outgrnid.getvalue()
            return grnid, message
    except Exception as error:
        print(error)
        return -1,  error
