from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import SupplierTransForm, FindDateForm

from  datetime import datetime, date

from common.models  import (PoHeaders, PoLines, PoGrnHeaders, PoGrnLines)
from common import (commonutil,sysutil)
from django import forms

#Create your form here
PO_GRN_HEADERS_COLUMNS=[
    'supplier_name_disp','supplier_address','delivery_note_ref','delivery_date','received_date','grn_date',
    'po_number','grn_number','po_date','grn_status','grnuser_name_disp','grn_status_date','currency_code',
    'billto_location_disp','shipto_location_disp','shipto_location_address','container_id',
    'containers_by_weight','containers_by_volume','terms1','terms2','attribute1','attribute2',
    'trans_category','orig_system_ref','ext_po_reference','update_stock','po_header_id',
    'grn_id','sup_supplier_id','net_total','vat_total','carriage_total','discount_total','gross_total',
    'weight_total','volume_total','ingredient_total','total_net_weight','bu_id','container_name',
    'grn_user_id','shipto_location_id','billto_location_id',]
PO_GRN_HEADERS_LABEL=[
    'Supplier','Supplier  Address','Delivery Note ','DeliverDate ','Received On ','GRN Date','PO #',
    'GRN #','PO Date','Status','User','Status Date','Currency ','Bill To Location','Location',
    'Ship To Address','Container ',' By Weight',' By Volume','Terms1',
    'Terms2','Free Text1','Free Text2','Category','Orig Sys Ref','Ext PO Ref',
    'Update Stock ? ','PO ID','GRN ID','Sup Supplier Id','Net Total',
    'Vat Total','Carriage Total','Discount Total','Gross Total','Weight Total',
    'Volume Total','Ingredient Total','Total Net Weight','Bu Id','Container Id',
    'Buyer Id','Shipto Location Id','Billto Location Id',]

PO_GRN_LINES_COLUMNS=[
        'po_header_id','tax_code_id','item_id','bu_id','po_line_id','line_type',
        'sl_no','item_name','item_number','grn_line_desc','grn_line_notes','un_approved_sub_loc_disp',
        'sub_location_disp','reason_for_rejection','rejection_sublocation_disp','discount_price',
        'tax_rate','tax_price','net_price','case_size','exchange_rate','qty_difference','reason_for_difference',
        'sup_product_code','net_ingredient','qty_instock','grn_status','volume_total','weight_total',
        'ingredient_total','qty_reserved','unit_cp','case_cp','qty_ordered_units','qty_balance',
        'qty_delivered_units','qty_ordered_cases','qty_delivered_cases','qty_received_units',
        'qty_rejected','qty_received_cases','gross_unit_weight','unit_volume','min_qty','max_qty',
        'reorder_qty','qty_inorder','purchaseable','saleable','stockable','pgh_grn_id','grn_line_id','rejection_update_stock']
PO_GRN_LINES_LABEL=[
        'Poh Po Header Id','Tax Code Id','Item Id','Bu Id','Po Line Id','Line Type','Sl  No','Item Name','Item Number',
        ' Line Description',' Line Notes','Un-Approved Sub Location','Approved Sub Location','Rejected Reasons',
        'Rejection Sub Location','Discount Price','Tax Rate','Tax Price','Net Price','Case Size',
        'Exchange Rate','Diff Qty (units)','Difference  Reason','Supplier Code','Net Ingredient','Qty  Instock',
        'Order Status','Volume Total','Weight  Total','Ingredient  Total','Qty Reserved','Unit  CP','Case CP','Ordered','Balance','Delivered',
         'Qty Cases','Qty Cases','Received','Rejected ','Qty Cases','Gross Unit Weight',
        'Unit  Volume','Min','Max','ReorderQty','In Order','Pur?','Sell?','Stock?','Po Header Id',
        'Po Header Id','Rej Upd Stk']


class GrnHeaderForm(forms.ModelForm):

    class Meta:
        model = PoGrnHeaders
        fields = '__all__'
        #PO_HEADERS_COLUMNS
        #exclude = ['bu_id','buyer_id','customer_id','sub_location_id','container_id','po_header_id']
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(GrnHeaderForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class PoSumForm(FindDateForm, SupplierTransForm, ):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(PoGrnHeaders)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(PoSumForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:grnsum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class GrnSumView(ListView):
    model = PoGrnHeaders
    template_name = 'enquiry/grnsum.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    linequery = {}
    emptysearch = True
    invlines = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}
    child1 = None
    child2 = None

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(GrnSumView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(GrnSumView, self).get_form_kwargs()
        kwargs['hiddenfields'] = []
        return kwargs

    def get_success_url(self):
        print('******* get success url')
        return reverse(REVERSE)

    def form_invalid(self, form, **kwargs):
        print('******* form valid')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        print('******* form valid')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_queryset(self, *args, **kwargs):
        print('******* get queryset')
        queryset = super().get_queryset()
        self.queryparams = {}
        self.detailform  = None
        commonutil.filter_add(self.queryparams,'grn_number',
                              commonutil.get_key_value(self.inputparams,'grn_number'),'exact')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_number',
                              commonutil.get_key_value(self.inputparams,'supp_number'),'exact')
        commonutil.filter_add(self.queryparams,'grn_status',
                              commonutil.get_key_value(self.inputparams,'order_status'),'icontains')
        commonutil.filter_add(self.queryparams,'grn_id',
                              commonutil.get_key_value(self.inputparams,'grn_id'),'')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',
                              commonutil.get_key_value(self.inputparams,'supplier'),'')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',
                              commonutil.get_key_value(self.inputparams,'supplier_id'),'')
        commonutil.filter_date_range(self.queryparams,'grn_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        if not self.queryparams:
            print('empty querying',self.queryparams)
            return self.model.objects.none()
        else:
            print('querying',self.queryparams)
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-grn_status_date','grn_number')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                       vat_total=Sum('vat_total'),
                       gross_total=Sum('gross_total'),
                        weight_total=Sum('weight_total'),
                        volume_total=Sum('volume_total'),
                        ingredient_total=Sum('ingredient_total')
                                       )
            if len(qs) == 1:
                detailinstance = qs[0]
                self.detailform = GrnHeaderForm(instance=detailinstance)
                parentid = detailinstance.po_header_id
                self.child1 = PoGrnLines.objects.filter(pgh_grn_id__grn_id=parentid).order_by('pgh_grn_id__grn_id','sl_no')
                self.rowset2_totals = self.child1.aggregate(
                        qty_delivered_units=Sum('qty_delivered_units'),
                        qty_delivered_cases=Sum('qty_delivered_cases'),
                        qty_received_units=Sum('qty_received_units'),
                        qty_ordered_cases=Sum('qty_ordered_cases'),
                        qty_received_cases=Sum('qty_received_cases'),
                        qty_rejected=Sum('qty_rejected'),
                        weight_total=Sum('weight_total'),
                        volume_total=Sum('volume_total'),
                       net_price=Sum('net_price'),
                        tax_price=Sum('tax_price'))
        self.object_list  = qs
        return qs

    def download_csv(self):
        csvdata = commonutil.download_csv(self.request, self.object_list)
        response = HttpResponse(csvdata, content_type='text/csv')
        return response

    def get_context_data(self, **kwargs):
        print('******* get context')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add local context
        self.form = PoSumForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Goods In'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'] ="""    
                                <th>Number</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Supplier </th>
                                <th>Location </th>
                                <th>PO </th>
                                <th>Net </th>
                                <th>Vat</th>
                                <th>Gross</th>
                                <th>Weight</th>
                                <th>Volume</th>
                                <th>Ingredient</th>"""
            context['rows_tablecolumns'] = """   
               <td> <a href={% url 'enquiry:grnsum' %}?grn_id={{row.grn_id}}>{{row.grn_number}}</a></td>
                    <td>{{row.grn_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
                    <td>{{row.grn_status }}</td>
                    <td>{{row.sup_supplier_id.supplier_name }}</td>
                    <td>{{row.shipto_location_id.location_name }}</td>
               <td> <a href={% url 'enquiry:posum' %}?po_header_id={{row.po_header_id}}>{{row.po_header_id}}</a></td>
                    <td>{{row.net_total }}</td>
                    <td>{{row.vat_total }}</td>
                    <td>{{row.gross_total }}</td>
                    <td>{{row.weight_total }}</td>
                    <td>{{row.volume_total }}</td>
                    <td>{{row.ingredient_total }}</td>
                    """
            context['rows_tablefooter'] ="""   
                    <td>Total</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>{{row.net_total }}</td>
                    <td>{{row.vat_total }}</td>
                    <td>{{row.gross_total }}</td>
                    <td>{{row.weight_total }}</td>
                    <td>{{row.volume_total }}</td>
                    <td>{{row.ingredient_total }}</td>
                    """
        if  self.child1:
            context['tabletitle2'] = 'Goods In Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'] ="""   
                                    <th> ID</th>
                                    <th> Sl No </th>
                                     <th> Item Number </th>
                                     <th> Item Name</th>
                                     <th> Sub Location</th>
                                      <th> Case Size  </th>
                                       <th> Unit CP </th>
                                       <th> Case CP </th>
                                      <th> Tax Rate </th>
                                     <th> Ordered</th>
                                      <th> Delivered </th>
                                     <th> Received </th>
                                    <th> Rejected </th>
                                    <th> Rej Diff </th>
                                    <th> Rej Reason </th>
                                     <th> Net Price </th>
                                    <th> Tax Price </th>
                                   <th> Weight Total </th>
                                    <th> Volume Total </th>
                                    """
            context['rowset2_tablecolumns'] = """ 
                                    <td> {{ row2.grn_line_id }}</td>
                                    <td> {{ row2.sl_no }}</td>
                                     <td> {{ row2.item_id.item_number }}</td>
                                     <td> {{ row2.item_name }}</td>
                                     <td> {{ row2.sub_location_id.sub_location }}</td>
                                    <td> {{ row2.case_size }}</td>
                                    <td> {{ row2.unit_cp }}</td>
                                    <td> {{ row2.case_cp }}</td>
                                    <td> {{ row2.tax_rate }}</td>
                                     <td> {{ row2.qty_ordered_units }}</td>
                                      <td> {{ row2.qty_delivered_units  }}</td>
                                     <td> {{ row2.qty_received_units }}</td>
                                     <td> {{ row2.qty_rejected }}</td>
                                     <td> {{ row2.reason_for_rejection }}</td>
                                     <td> {{ row2.reason_for_difference }}</td>
                                      <td> {{ row2.net_price }}</td>
                                     <td> {{ row2.tax_Price }}</td>
                                    <td> {{ row2.weight_total }}</td>
                                     <td> {{ row2.volume_total }}</td> """
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tablefooter'] = """ <td>Totals</td>
                                    <td> </td>
                                     <td> </td>
                                     <td> </td>
                                     <td> </td>
                                    <td> </td>
                                    <td></td>
                                    <td></td>
                                    <td> </td>
                                     <td> {{ rowset2_totals.qty_ordered_units }}</td>
                                     <td> {{ rowset2_totals.qty_delivered_units }}</td>
                                     <td> {{ rowset2_totals.qty_received_units }}</td>
                                     <td> {{ rowset2_totals.qty_rejected }}</td>
                                      <td> </td>
                                     <td> </td>
                                      <td> {{ rowset2_totals.net_price }}</td>
                                     <td> {{ rowset2_totals.tax_Price }}</td>
                                    <td> {{ rowset2_totals.weight_total }}</td>
                                     <td> {{ rowset2_totals.volume_total }}</td>
                                     """
        if self.child2:
            context['tabletitle3'] = 'Child2'
            context['rowset3'] = self.child2
            context['rowset3_tableheader'] = """
                                """
            context['rowset3_tablecolumns'] = """
                                                """

        context['detailform'] = self.detailform
        context['detailform_title'] = 'Detail'
        print('******* set context')
        return context
