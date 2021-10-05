from common.models import (InvItemMasters)
from common import (commonutil, dbfuncs)


def get_locationid(request = None, defval:int = 0):
    if not request:
        return defval
    try:
        if 'locationid' in request.session:
            return int(request.session['locationid'])
        return request.user.location_id
    except:
        return defval

def get_item(itemnumber, context:{}):
    try:
        item = InvItemMasters.objects.all().filter(item_number__exact=itemnumber)
        if not item:
           context['itemerror'] = "Item does not exist or Invalid:{0} ".format(itemnumber)
        item = item[0]
        return item
    except:
        return None


def move_item(p_movementtype:str = 'INTERNALTOINTERNAL',
            p_userid:int =1,
            p_itemnumber:str ="",
            p_fromlocationid:int = 0,
            p_fromsublocation:str ="",
            p_quantity:int = 0,
            p_tolocationid:int = 0,
            p_tosublocation:str = "",
            p_fromlocation:str ="",
            p_fromsublocationid:int = 0,
            p_tolocation:str = "",
            p_tosublocationid:int = 0,
            p_itemid:int = 0):
    if p_itemnumber == "" and p_itemid == 0:
        return "Invalid Item Number"
    if p_fromlocation == "" and p_fromlocationid == 0:
        return "Invalid From Location"
    if p_tolocation == "" and p_tolocationid == 0:
        return "Invalid To  Location"
    if not commonutil.hasintvalue(p_quantity):
        return "Quantity must be greater thann ZERO"
    if p_fromsublocation == "" and p_fromsublocationid == 0:
        return "Invalid From Sub Location"
    if p_tosublocation == "" and p_tosublocationid == 0:
        return "Invalid To Sub Location"
    fromlocationid = p_fromlocationid
    tolocationid = p_tosublocationid
    fromlocation = p_fromlocation
    fromsublocation = p_fromsublocation
    tolocation = p_tolocation
    tosublocation = p_tosublocation
    quantity = p_quantity
    itemnumber = p_itemnumber
    itemid = p_itemid
    mycontext = {}
    message = ""
    if itemnumber != "":
        item = get_item(itemnumber, mycontext)
        print(item, fromlocationid, fromsublocation, quantity)
        fromsublocationid  = dbfuncs.get_sublocation_id(fromlocationid, fromsublocation)
        if tosublocation is not None:
            tosublocationid = dbfuncs.get_sublocation_id(tolocationid, tosublocation)
        else:
            tosublocationid  = dbfuncs.get_default_sublocationid(tolocationid, item.item_id)
        message = dbfuncs.exec_str_func('mobile_pkg.Move_SingleItem',
                                        [p_userid , p_movementtype, fromlocationid,
                     fromsublocationid, item.item_id, quantity, tolocationid, tosublocationid])

        return message
