from django.db import connection
from common.models import (ArSalesorderHeaders,ArSalesorderLines)
from common import dbfuncs as dbfuncs
from common import commonutil as commonutil
from common.models import (InvItemMasters, InvItemSalesUnits, InvItemPicklist, InvPriceTypes, InvItemBarcodes)


def get_itemdetail(itemstring:str = "" , itemid:int = 0 , model = InvItemMasters):
    item = None
    if  commonutil.hasstrvalue(itemstring):
        item = model.objects.filter(item_number__exact=itemstring)
    elif commonutil.hasintvalue(itemid):
        item = model.objects.filter(item_id=itemid)
    if not item:
        item = item[0]
    return item


def get_barcodeqty(itemstring):
    qty =  dbfuncs.select_sqlfunc("Inv_Pkg.Get_barcodeQty(upper('{0}'))".format(itemstring.upper()))
    qty = int(qty)
    return commonutil.nvl(qty,1)

def add_itemtobatch(p_batchname:str,
                    p_itemnumber:str,
                    p_batchid:int = None,
                    p_itemid:int = None,
                    p_qty:int = 1,
                    p_userid:int = 1,
                    p_buid:int = 1):
    print('AddItem:',p_batchname, p_itemnumber)
    batchid = p_batchid
    itemid = p_itemid
    try:
        if not commonutil.hasintvalue(p_batchid) and commonutil.hasstrvalue(p_batchname):
            batchid = dbfuncs.select_sqlfunc("ITemBatch_Pkg.get_batchidbyname('{}')".format(p_batchname))
        if not commonutil.hasintvalue(p_itemid) and commonutil.hasstrvalue(p_itemnumber):
            itemid = dbfuncs.select_sqlfunc("Inv_Pkg.GetItemIdBybarcode('{}')".format(p_itemnumber))

        if commonutil.hasintnonaerovalue(batchid) and commonutil.hasintnonaerovalue(itemid):
            sql = """ItemBAtch_Pkg.CreateBatch(p_batchid => {0},
                        p_ItemId => {1},
                         p_Query => Null,
                         p_Userid => {2},
                         p_BuId => {3});""".format(batchid,itemid,p_userid,p_buid)
            dbfuncs.exec_plsqlblock(sql)
    except Exception as ex:
        commonutil.debugmessage(ex)
        return -1, ex
    finally:
        commonutil.debugmessage('batchid:'+str(batchid),'1')
        return batchid, commonutil.handlemessages("Item added")

