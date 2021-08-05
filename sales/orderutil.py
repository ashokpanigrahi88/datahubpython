from django.db import connection
from common.models import (ArSalesorderHeaders,ArSalesorderLines)
from common import dbfuncs as dbfuncs
from common import commonutil as commonutil


def get_pickingconfirmaton(**kwargs):
    val = dbfuncs.select_sqlfunc("NVL(AR_PKG.Get_Optionval('PICKING_CONFIRMATION'),'THREEWAY')")
    print('pick',val)
    return val

def is_palletingenabled(**kwargs):
    val = dbfuncs.select_sqlfunc("Inv_Pkg.Get_Optionval('ENABLE_PALLETING')")
    return val

def get_orderheader(orderheaderid, **kwargs):
    orderheader = ArSalesorderHeaders.objects.filter(order_header_id=orderheaderid)
    if  orderheader:
        return orderheader[0]
    return None

def get_itemid(itemstring:str):
    if not commonutil.hasstrvalue(itemstring):
        return None
    itemid = dbfuncs.select_sqlfunc("Inv_Pkg.GetItemIdByIndex(upper('{0}'))".format(itemstring.upper()))
    return itemid

def get_orderline(orderlineid,**kwargs):
    orderline = ArSalesorderLines.objects.filter(order_line_id=orderlineid)
    if orderline:
        return orderline[0]
    return None

def get_barcodeqty(itemstring):
    qty =  dbfuncs.select_sqlfunc("Inv_Pkg.Get_barcodeQty(upper('{0}'))".format(itemstring.upper()))
    qty = int(qty)
    return commonutil.nvl(qty,1)

def get_ordertotalpicked(orderid, orderlineid):
    qty = dbfuncs.select_sqlfunc("Nvl(SalOrder_Pkg.Get_TotalPicked({0},{1}),0)".format(orderid,orderlineid))
    return commonutil.nvl(qty,0)


def pick_orderline(p_userid:int = 1,
                    p_ordernumber = "",
                    p_orderid = 0,
					p_boxslno = 0,
                    p_lineid = "",
                    p_fromsublocation = "",
                    p_pickeditemnumber = "" ,
                    p_quantity:int = 0,
					p_categorystring = "",
                    p_locationid:int = 0):

    errorpos = '1'
    pickingconfirmation = get_pickingconfirmaton()
    palletenabled = is_palletingenabled()
    orderitemid = 0
    lineid =0
    orditemnumber = ""
    try:
        lineid = p_lineid.split('-')[0]
        orditemnumber = p_lineid.split('-')[1]
    except:
        pass
    print(lineid)
    errorpos = '2'
    try:
        if commonutil.hasintvalue(lineid):
            orderitemid = get_itemid(p_pickeditemnumber)
            if commonutil.hasintvalue(orderitemid):
                errorpos = '20'
                sql = """Select  Order_Line_ID From Ar_SalesOrder_Lines
                            where  Order_Header_Id = {0}
                            and Item_Id = {1}
                            And RowNum = 1; """.format(p_orderid, orderitemid)
                orderline = dbfuncs.exec_sql(sql,'dixt')
                lineid = orderline['ORDER_LINE_ID']
        errorpos = '2A'
        if commonutil.hasstrvalue(orditemnumber):
            orditemnumber = p_orderid
        quantity = commonutil.nvl(p_quantity,0)
        orditemnumber = orditemnumber.upper()
        orderitemid = get_itemid(orditemnumber)
        orderline = get_orderline(lineid)
        print('orderline',orderline)
        errorpos = '2B'
        orderid = orderline.order_header_id
        qtytopick = orderline.qty_picked_units

        errorpos = '2B1'
        if pickingconfirmation == "TWOWAY":
            itemnumber = orditemnumber
            quantity = qtytopick
        else:
            itemnumber = p_pickeditemnumber.upper()
        itemid = get_itemid(itemnumber)

        errorpos = '3'
        actualorderid = p_orderid
        quantity = int(quantity) * get_barcodeqty(itemnumber)

        errorpos = '3A'
        if int(orderline.order_header_id) != int(p_orderid):
            return  "Invalid Order Id / Does not exist in the order :{0} , {1}".format(orderline.order_header_id,p_orderid)
        if commonutil.ifnegative(quantity):
            return "Quantity must be positive"
        if commonutil.ifnull(itemnumber):
            return "Incalid Pick Item Number or blank"
        errorpos = '3B'
        if commonutil.ifnegative(quantity):
            return "Quantity must be positive"
        if commonutil.ifnegativeozero(orderitemid):
            return "Blank Order Item "
        if itemid != orderitemid:
            return 'Mismatching Order vs Picked Item:{0} and {1}'.format(orderitemid, itemid)
        locationid = p_locationid

        errorpos = '4'
        sublocationid = dbfuncs.get_sublocation_id(locationid, p_fromsublocation)
        if commonutil.ifnegativeozero(sublocationid):
            return "Invalid from sub location {0} id:{1}".format(p_fromsublocation, sublocationid)

        errorpos = '5'
        qtypickedsofar = get_ordertotalpicked(orderid,lineid)
        if commonutil.ifnegative(qtypickedsofar):
            return "Something went wrong with this order picked more than ordered , see manager"
        totalpicking = qtypickedsofar + quantity
        if totalpicking > qtytopick:
            return "Cannot pick more than accepted quantity :Accepted:{0}  Picking:".format(
                            qtytopick, totalpicking)
        boxslno = commonutil.nvl(p_boxslno,1)

        errorpos = '6'
        message = dbfuncs.exec_str_func("MOBILE_PKG.SALORDPICK_SingleItem",
                [p_userid, p_orderid, lineid, locationid, sublocationid,itemid,quantity, boxslno])
        return message
    except Exception as ex:
        return
        #"ERROR Picklist @ {0} , {1}".format(errorpos,ex)


