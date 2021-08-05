from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms.boundfield import BoundField
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from mobile.forms import CreateGRNForm
from common import (sessionfunc, commonutil, dbfuncs)
from purchase import (pogrnutil)
from inventory import (locationutil)
from common.models import (PoOrderpadHeaders, PoLines, PoGrnLines, PoGrnHeaders, ApSuppliers)


# specific to this view


REVERSE = 'mobile:creategrn'

@method_decorator(login_required, name='dispatch')
class CreateGRNView(FormView):
    template_name = 'mobile/newgrn.html'
    form_class = CreateGRNForm
    rows, rowset2, rowset3, rowset4, approvedpos  = (None,)*5
    context_object_name = 'form'
    itemdict, MYCONTEXT = ({},)*2
    grnid , supplierid ,grnnumber, deliveryref, suppliernumber,ponumber, itemnumber  = ("",)*7
    quantity = 0
    myform = ""
    message = ""
    success_url = "/mobile/newgrn/"


    def get(self, request, *args, **kwargs):
        form = self.get_form()

        def get_initial(self):
            initial = {'grn_id': self.grnid,
                       'goodsin_number': self.grnnumber,
                       'supplier_id': self.supplierid,
                       'delivery_reference': self.deliveryref,
                       'item_number': "",
                       'delivered_qty': ""
                       }
            print('inital:', initial)
            return initial

        def get_form_kwargs(self):
            kwargs = super(CreateGRNView, self).get_form_kwargs()
            if commonutil.hasintvalue(self.request.POST.get('grnid')) or commonutil.hasintvalue(self.grnid):
                kwargs['hiddenfields'] = ['goodsin_number', 'supplier_number', 'delivery_reference', 'po_number']
            else:
                kwargs['hiddenfields'] = ['item_number', 'delivered_qty']
            return kwargs

        self.suppliernumber =  self.request.GET.get('supplier_number')
        self.deliveryref =  self.request.GET.get('delivery_reference')
        self.grnnumber  =  self.request.GET.get('goodsin_number')
        self.ponumber =  self.request.GET.get('po_number')
        self.grnid  =  self.request.GET.get('grn_id')
        self.supplierid  =  self.request.GET.get('supplier_id')
        self.itemnumber  =  self.request.GET.get('item_number')
        self.quantity  =  self.request.GET.get('delivered_qty')
        return super(CreateGRNView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        def gotoerror():
            pass
            self.MYCONTEXT['errormessage'] = "Error while processing goods in"
            return self.form_invalid(form, **kwargs)

        def gotoend():
            print("form valid at end")
            return self.form_invalid(form, **kwargs)

        self.suppliernumber =  self.request.POST.get('supplier_number')
        self.deliveryref =  self.request.POST.get('delivery_reference')
        self.grnnumber  =  self.request.POST.get('goodsin_number')
        self.ponumber =  self.request.POST.get('po_number')
        self.grnid  =  self.request.POST.get('grn_id')
        self.supplierid  =  self.request.POST.get('supplier_id')
        self.itemnumber  =  self.request.POST.get('item_number')
        self.quantity  =  self.request.POST.get('delivered_qty')
        locationid = sessionfunc.get_location_id(self.request)
        page = self.request.POST.get('page')
        userid = self.request.user.user_id
        # self.form_class['to_sub_location'].   to_sub_location(initial='GRN STAGING')
        businessunit = self.request.user.bu_id
        userid = self.request.user.user_id
        if not commonutil.hasstrvalue(self.grnnumber) and commonutil.hasstrvalue(self.ponumber):
            self.grnid , self.message  = pogrnutil.ceategrn_frompo(userid,None,self.ponumber)
            if commonutil.hasintvalue(self.grnid) and self.grnid > 0:
                self.MYCONTEXT['successmessage'] = commonutil.handlemessages(
                    " Goods in created successfully from PO {}".format(self.ponumber))
            else:
                self.MYCONTEXT['errormessage'] = commonutil.handlemessages(self.message)

        self.grnid = pogrnutil.get_grnidbynumber(self.grnnumber)
        print('GRN ID', self.grnid, self.grnnumber)
        if commonutil.hasstrvalue(self.deliveryref) or commonutil.hasintvalue(self.grnid):
            self.MYCONTEXT['successmessage'] = 'Enter Item and Quantiy for Goods In {}'.format(
                self.grnnumber)
        if commonutil.hasstrvalue(self.ponumber) :
            sql = """Select p.PO_Number,s.Supplier_Number,s.Supplier_name,p.Order_STATUS, p.order_status_date,
                              p.PO_header_id, s.supplier_id
                             From PO_HEADERS p, AP_SUPPLIERS s 
                             Where p.Sup_Supplier_ID = s.Supplier_ID  
                             And   p.po_number = '{0}'
                             """.format(self.ponumber)
            approvedpos  = dbfuncs.exec_sql(sql, 'dict')
            self.rowset3 = approvedpos

        sql = """Select g.Grn_Number,s.Supplier_Number,s.Supplier_name,
                INV_PKG.GetLOCATIONname(g.Shipto_location_ID) Location_Name,
                        g.Grn_STATUS, g.last_update_Date,
                        g.grn_id, g.delivery_note_ref
                       From PO_GRN_HEADERS g, AP_SUPPLIERS s 
                       Where g.Sup_Supplier_ID = s.Supplier_ID  
                       And   g.Grn_Status = 'NEW'"""
        if commonutil.hasintvalue(self.grnid):
                sql += """ AND g.GRN_ID = {0}   """.format(self.grnid)
        sql += """Order By g.last_Update_Date Desc"""
        newgrns = dbfuncs.exec_sql(sql,'dict')
        self.rows = newgrns
        if commonutil.hasintvalue(self.grnid) and commonutil.hasstrvalue(self.itemnumber):
            self.grnlineid , message = pogrnutil.additemtogrn(self.itemnumber, userid,
                                                              self.grnid,  None,  self.quantity)
            if self.grnlineid <=0:
                self.MYCONTEXT['errormessage'] = message
            self.MYCONTEXT['successmessage'] = "Gen Number:{0}".format(self.grnnumber)
            gotoend()
        if commonutil.hasstrvalue(self.grnnumber):
            # grnrow = pogrnutil.getpomodelrow(PoGrnHeaders,'grn_number',p_string=self.grnnumber)
            grnrow = PoGrnHeaders.objects.all().filter(grn_number__exact=self.grnnumber)
            if not grnrow:
                grnrow = PoGrnHeaders.objects.all().filter(grn_id=self.grnid)
            if grnrow:
                grnrow = grnrow[0]
                self.supplierid = grnrow.sup_supplier_id
                self.deliveryref = grnrow.delivery_note_ref
                self.grnid = grnrow.grn_id
                print(self.supplierid, self.grnnumber, self.grnid)
                supplierrow = pogrnutil.getpomodelrow(ApSuppliers, 'supplier_id', p_number=self.supplierid)
                print(supplierrow)
            else:
                try:
                    if not commonutil.hasstrvalue(self.suppliernumber):
                        self.MYCONTEXT['errormessage'] = 'Please select a supplier'
                        raise ValueError
                    if not commonutil.hasstrvalue(self.deliveryref):
                        self.MYCONTEXT['errormessage'] = 'Please enter delivery reference'
                        raise ValueError
                    supplierrow = pogrnutil.getpomodelrow(ApSuppliers, 'supplier_number', p_string=self.suppliernumber)
                    if not supplierrow:
                        supplierrow = pogrnutil.getpomodelrow(ApSuppliers, 'supplier_idr', p_number=self.supplierid)
                    print('supplier', supplierrow)
                    if not grnrow:
                        print(3)
                        self.grnid, message = pogrnutil.createnewgrn(userid, self.supplierid, locationid,
                                                                     self.deliveryref)
                        self.MYCONTEXT['errormessage'] = message
                    self.MYCONTEXT['successmessage'] = "Gen Number:{0}".format(self.grnnumber)
                except Exception as error:
                    print(error)
                    self.MYCONTEXT['errormessage'] = error
        return self.form_invalid(form, **kwargs)

    def get_initial(self):
        initial =  {'grn_id': self.grnid,
                    'goodsin_number': self.grnnumber,
                    'supplier_id': self.supplierid,
                    'delivery_reference': self.deliveryref,
                    'item_number': "",
                    'delivered_qty': "",
                    'sub_location': ""
                    }
        print('inital:',initial)
        return initial

    def get_form_kwargs(self):
        kwargs = super(CreateGRNView, self).get_form_kwargs()
        if commonutil.hasintvalue(self.request.POST.get('grnid')) or commonutil.hasintvalue(self.grnid):
            kwargs['hiddenfields'] =  ['goodsin_number','supplier_number','delivery_reference','po_number']
        else:
            kwargs['hiddenfields'] =  ['item_number','delivered_qty','sub_location']
        return kwargs

    def get_queryset(self):
        pass

    def get_success_url(self):
        return reverse(REVERSE)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        #context['form'] = CreateGRNForm
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CreateGRNView , self).get_context_data(**kwargs)

        if commonutil.hasintvalue(self.grnid):
            print('getitems')
            sql = """Select i.Item_Number,Inv_Pkg.Get_SuBin(i.Item_Id) SuBin,i.Item_Name,
                        l.Qty_Received_Units, Inv_PKG.GetSUBLOCATIONname(l.Sub_Location_Id) Sub_Location  
                     From inv_Item_Masters i, PO_GRN_LINES l
                     Where i.Item_Id  = l.Item_ID 
                     And   l.PGH_GRN_ID = {0}""".format(self.grnid)
            grnlines = dbfuncs.exec_sql(sql, 'dict')
            print(grnlines)
            self.rowset2 = grnlines
        context['businessunit'] = self.request.user.bu_id
        print(self.MYCONTEXT)
        context['itemdict'] = self.itemdict
        context['rows'] = self.rows
        context['rowset2'] = self.rowset2
        context['rowset3'] = self.rowset3
        currform = context['form']
        if commonutil.hasstrvalue(self.itemnumber):
            self.myform = str(currform).replace(
                self.itemnumber,'').replace(
                'value="{0}"'.format(self.quantity),'value=""' ).replace(
                self.ponumber, '')
        context['myform'] = self.myform
        self.MYCONTEXT['grnnumber'] = self.grnnumber
        self.MYCONTEXT['grnid'] = self.grnid
        context['MYCONTEXT'] = self.MYCONTEXT
        return context

