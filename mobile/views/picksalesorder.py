from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import SalesOrderPickForm
from common import dbfuncs as dbfunc
from common.models import (ArSalesorderHeaders)
from sales import orderutil as orderutil
# specific to this view

REVERSE = 'mobile:picksalesorder'
# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class ValueTooSmallError(Error):
    """Raised when the input value is too small"""
    pass

@method_decorator(login_required, name='dispatch')
class SalesOrderPickingView(FormView):
    template_name = 'mobile/picksalesorder.html'
    form_class = SalesOrderPickForm
    deforderid = '0'
    MYCONTEXT = {}
    MYCONTEXT['errormessage'] = None
    MYCONTEXT['order_header_id'] = deforderid
    if 'mode' not in MYCONTEXT:
        MYCONTEXT['mode'] = 'NEW'
        MYCONTEXT['HIDEFIELDS'] = ['item_number','quantity']

    def get(self, request, *args, **kwargs):
        self.MYCONTEXT['order_number'] = None
        return super(SalesOrderPickingView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.form_invalid(form, **kwargs)

    def get_queryset(self):
        pass

    def get_success_url(self):
        return reverse(REVERSE)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SalesOrderPickingView, self).get_context_data(**kwargs)
        f_ordernumber = self.request.POST.get('order_number')
        f_orderid = self.request.POST.get('order_id')
        f_pickeditemnumber = self.request.POST.get('picked_item_number')
        f_quantity = self.request.POST.get('quantity')
        f_lineid = self.request.POST.get('line_id')
        f_boxslno = self.request.POST.get('box_slno')
        f_fromsublocation =   self.request.POST.get('from_sub_location')
        f_categorystring = self.request.POST.get('categorystring')
        f_pickingconfirmation = self.request.POST.get('pickingconfirmation')
        f_enablepalleting = self.request.POST.get('enable_palleting')
        userid = self.request.user.user_id
        order = None
        if not f_orderid:
            f_orderid = self.deforderid
        if not f_ordernumber:
            return context

        if f_orderid != self.deforderid:
            order = ArSalesorderHeaders.objects.filter(order_header_id=int(f_orderid))
        else:
            order = ArSalesorderHeaders.objects.filter(order_number__exact=f_ordernumber)
        print(order)
        if not order:
            print('ordernumber', f_ordernumber)
            self.MYCONTEXT['errormessage'] = 'Invalid order number {0}'.format(f_ordernumber)
            self.MYCONTEXT['order_number'] = None
            self.MYCONTEXT['order_id'] = self.deforderid
            context['MYCONTEXT'] = self.MYCONTEXT
            return context

        print('outside', f_ordernumber)
        order = order[0]
        locationid = self.request.user.location_id
        try:
            print('status', type(locationid), type(order.shipfrom_location_id))
            if order.shipfrom_location_id.location_id != int(locationid):
                print('status1')
                self.MYCONTEXT['errormessage'] = 'Order does not belong your location {0} , {1}'.format(
                    order.shipfrom_location_id, locationid
                )
                raise Error
            print('status')
            if order.order_status == 'CLOSED':
                self.MYCONTEXT['errormessage'] = 'Order is already closed'
                raise Error
            if order.order_status == 'NEW':
                self.MYCONTEXT['errormessage'] = 'Order in NEW state'
                raise Error
            if order.order_status == 'INVOICED':
                self.MYCONTEXT['errormessage'] = 'Order is already invoiced'
                raise Error
            if order.order_status == 'DELIVERED':
                self.MYCONTEXT['errormessage'] = 'Order is already delivered'
                raise Error
        except:
            self.MYCONTEXT['order_number'] = None
            self.MYCONTEXT['order_id'] = self.deforderid
            context['MYCONTEXT'] = self.MYCONTEXT
            return context

        print('orderquery', order)
        if 'customername' not in self.MYCONTEXT:
            self.MYCONTEXT['customername'] = order.customer_id.customer_name

        f_boxslno = self.request.POST.get('box_slno')
        self.MYCONTEXT['categorystring'] = dbfunc.exec_str_func('Emp_Pkg.SO_CheckCategories',
                                              [userid, order.order_header_id])
        self.MYCONTEXT['pickingconfirmation'] = orderutil.get_pickingconfirmaton()
        self.MYCONTEXT['order_number'] = order.order_number
        self.MYCONTEXT['order_id'] = order.order_header_id
        self.MYCONTEXT['boxslno'] = f_boxslno
        self.MYCONTEXT['enablepalleting'] = orderutil.is_palletingenabled()
        self.MYCONTEXT['successmessage'] = 'Order Number:{3} , Customer:{0} Number:{1} , Picking by:{2}'.format(
            self.MYCONTEXT['customername'], order.customer_id.customer_number, self.request.user.user_name,
            order.order_number)
        self.MYCONTEXT['mode'] = 'PICK'
        context['MYCONTEXT'] = self.MYCONTEXT
        if  f_pickeditemnumber != "":
            print('fpickedItem',f_pickeditemnumber)
            message = orderutil.pick_orderline(userid,order,f_ordernumber,f_boxslno,
                                           f_lineid,f_fromsublocation,f_pickeditemnumber,
                                           f_quantity,f_categorystring, locationid)
            if message != "OK":
                self.MYCONTEXT['errormessage'] = message

        sql = """ Select Sub_Loc_Sort, Item_Number, Order_Number, Order_Line_ID, Sub_Location_Name
                        , Item_Name, SUB_LOCATION_STOCK_QTY, Qty_picked_Units,
                        Total_Picked, To_Be_Picked_Qty, To_Be_Picked_Qty_case,
                        Itemstatus_Pkg.GetQtyInStock(item_Id, PICKED_LOCATION_ID, null, 'LOC', 'FULL')
                        Loc_Stock_qty, Item_Id
                From  Mobile_readytopick_v
                Where Order_Header_ID = {0}
                AND  Qty_Picked_Units > 0
                AND  Emp_Pkg.So_DisplayCategory('{1}', Category_Id) = 1
                ORDER By  1, 2""".format(order.order_header_id,self.MYCONTEXT['categorystring'])
        orderlines = dbfunc.exec_sql(sql, 'dict')
        linestopick = ""
        othersubloc = ""
        for row in orderlines:
            sql = """ Select Sub_Loc_Sort,Sub_Location,Quantity
                       From 	mobile_PickableSubLocs_V
                       Where    Item_Id = {0} 
                       AND      sub_Location <> '{1}' 
                       and      rownum <5
                       Order by 1,2""".format(row['ITEM_ID'],row['SUB_LOCATION_NAME'])
            sublocations =  dbfunc.exec_sql(sql, 'dict')
            othersubloc = ""
            for subloc in sublocations:
                othersubloc  +=  """ <p>{0} __:{1}</p>""".format(subloc['SUB_LOCATION'], int(subloc['QUANTITY']))
            linestopick += """ <tr> 
                           <td> {0} </td>
                           <td> {1} </td>
                           <td> {2} {3} </td>
                           <td> {4} </td>
                           <td> {5} </td>
                           <td> {6} </td>
                           <td> {7} </td>
                           <td> {8} </td>
                           <td> {9} </td>
                           </tr>""".format(row['ORDER_NUMBER'],
                                           row['ORDER_LINE_ID'],
                                           row['SUB_LOCATION_NAME'],
                                           othersubloc,
                                           row['ITEM_NUMBER'],
                                           row['ITEM_NAME'],
                                           row['LOC_STOCK_QTY'],
                                           row['SUB_LOCATION_STOCK_QTY'],
                                           int(row['QTY_PICKED_UNITS']),
                                           row['TOTAL_PICKED'],
                                           row['TO_BE_PICKED_QTY'],
                                           row['TO_BE_PICKED_QTY_CASE'],
                                           )

        context['linestopick'] = linestopick

        return context