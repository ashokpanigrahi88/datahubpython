from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import SalesOrderQueryForm
from common import dbfuncs as dbfunc
from common.models import (ArSalesorderHeaders)

# specific to this view

REVERSE='mobile:salesorderquery'

@method_decorator(login_required, name='dispatch')
class SalesOrderQueryView(FormView):
        template_name = 'mobile/salesorderquery.html'
        context_object_name = 'form'
        form_class = SalesOrderQueryForm
        itemdict = {}
        MYCONTEXT = {}

        def get(self, request, *args, **kwargs):
            self.MYCONTEXT['order_number'] = None
            return super(SalesOrderQueryView, self).get(request, *args, **kwargs)

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
            context = super(SalesOrderQueryView, self).get_context_data(**kwargs)

            f_ordernumber = self.request.POST.get('order_number')
            f_orderstatus = str(self.request.POST.get('order_status'))+'%'
            f_linestatus = str(self.request.POST.get('Line_status'))+'%'
            f_linephase = str(self.request.POST.get('Line_phase'))+'%'
            f_deliverystatus =  str(self.request.POST.get('delivery_status'))+'%'
            f_webordernumber = str(self.request.POST.get('web_order_number'))+'%'
            orderid = None
            if f_ordernumber != "":
                orderid = dbfunc.select_sqlfunc("SalOrder_Pkg.Get_OrderIdFromNumber('{0}')".format(f_ordernumber))
                print(orderid)
                orderheader = ArSalesorderHeaders.objects.filter(order_header_id=orderid)
                context['rows'] = orderheader
                if orderheader:
                    orderh = orderheader[0]
                    sql = """Select Order_Header_Id,
                                    Qty_Ordered_Units,
                                    Qty_Accepted_Units,
                                    Qty_Userpicked_Units,
                                    Qty_Delivered_Units,
                                    Qty_Invoiced_Units,
                                    Qty_Cancelled_Units
                                    From AR_SALORDLINESTAT_V
                            Where Order_Header_ID = {0}""".format(orderh.order_header_id)
                    qtystatus = dbfunc.exec_sql(sql,'dict')
                    context['rowset2'] = qtystatus
                    sql = """Select
                                Total_Lines , 
                                New_Count,
                                Approved_Count,
                                Picked_Count,
                                Invoiced_Count,
                                Delivered_Count,
                                Readytopick_Count,
                                Readytodeliver_Count,
                                Weorder_Count
                                    From AR_SALORDLINESTAT_V
                            Where Order_Header_ID = {0}""".format(orderh.order_header_id)
                    linestatus = dbfunc.exec_sql(sql,'dict')
                    context['rowset3'] = linestatus
                    sql = """Select Sl_No,Item_Number,Qty_Ordered_Units,
                                Qty_Picked_Units,Qty_UserPicked_Units,
                          Qty_Delivered_Units,LineStatus,LinePhaseCode,
                          t_OrderNumber,Delivery_status,Delivery_Date,Item_name
                            From REP_ITEMSALESORDER_V
                         Where Order_Header_ID = {0}
                        And  LineStatus like '{1}'
                        And  LinePhaseCode like '{2}'
                        And  nvl(T_ORDERNUMBER,'%') like '{3}'
                        And  nvl(Delivery_Status,'%') like '{4}'
                        order by 1,2,3""".format(orderh.order_header_id, f_linestatus,
                                f_linephase, f_webordernumber,f_deliverystatus)
                    lines = dbfunc.exec_sql(sql,'dict')
                    context['rowset4'] = lines
            page = self.request.POST.get('page')
            userid = self.request.user.user_id
            return context

