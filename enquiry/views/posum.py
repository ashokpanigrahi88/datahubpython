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
from enquiry import enquirygrids

#Create your form here

PO_HEADERS_COLUMNS = [
    'shipto_location_id', 'po_number', 'sup_supplier_id', 'po_date', 'po_type', 'agreement_number',
    'trans_category', 'currency_code', 'order_status', 'buyer_id', 'order_status_date', 'billto_location_id',
    'container_id', 'containers_by_weight', 'containers_by_volume', 'terms1', 'terms2', 'attribute1',
    'attribute2', 'customer_id', 'shipto_address', 'shipto_city', 'shipto_county', 'shipto_post_code',
    'shipto_country_code', 'shipto_contact', 'shipto_phone', 'needby_date', 'revision_number', 'promised_date',
    'update_stock', 'orig_system_ref', 'po_header_id', 'net_total', 'vat_total', 'gross_total',
    'carriage_total', 'discount_total', 'bu_id', 'weight_total', 'volume_total', 'container_name',
    'total_net_weight', 'ingredient_total']
PO_HEADERS_LABEL = [
    'Location', 'PO#', 'Supplier', 'PO Date', ' Type', 'Agreement ', 'Category', 'Currency ',
    'Status', 'Buyer Id', 'Status Date', 'Bill To Location', 'Container ', ' By Weight', ' By Volume',
    'Terms1', 'Terms2', 'Free Text1', 'Free Text2', 'Customer', 'Address', 'City', 'County', 'Post Code', 'Country',
    'Contact', 'Phone', 'Need by Date ', 'Revision', 'Promised Date ', 'Update Stock ? ', 'External PO Ref', 'ID',
    'Net', 'Vat ', 'Gross', 'Carriage Total', 'Discount Total', 'Bu Id', 'Weight Total',
    'Volume Total', 'Container Id', 'Total Net Weight', 'Ingredient Total']
PO_LINES_COLUMNS=[
    'poh_po_header_id','tax_code_id','item_id','bu_id','po_line_id','line_type','sl_no',
    'item_name','sup_product_code','qty_instock','case_size','unit_cp','case_cp','qty_ordered_units',
    'qty_goodsin','net_price','qty_balance','po_line_desc','po_line_notes',
    'revision_number','discount_price','tax_rate','tax_price','net_ingredient',
    'order_status','exchange_rate','weight_total','volume_total','ingredient_total',
    'qty_reserved','qty_ordered_cases','gross_unit_weight','unit_volume','needby_date','promised_date']
PO_LINES_LABEL=[
    'Poh Po Header Id','Tax Code Id','Item Id','Bu Id','Po Line Id','Line Type','Sl  No','Item Name',
    'Supplier Code','Qty Instock','Case Size','Unit CP','Case CP','Qty Ordered','Qty Goodsin',
    'Net Price','Qty Balance',' Line Description',' Line Notes','Revision','Discount Price',
    'Tax Rate','Tax Price','Net Ingredient','Line Status','Exchange Rate','Weight Total','Volume Total',
    'Ingredient Total','Qty Reserved','Qty Cases','Gross Unit Weight','Unit Volume','Needby Date','Promised Date']


class PoHeaderForm(forms.ModelForm):

    class Meta:
        model = PoHeaders
        fields = PO_HEADERS_COLUMNS
        exclude = ['bu_id','buyer_id','customer_id','sub_location_id','container_id','po_header_id']
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(PoHeaderForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class PoSumForm(FindDateForm, SupplierTransForm, ):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(PoHeaders)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))
    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(PoSumForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:posum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class PoSumView(ListView):
    model = PoHeaders
    template_name = 'enquiry/posum.html'
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
    rowset3_totals ={}
    child1 = None
    child2 = None

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(PoSumView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(PoSumView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'po_number',
                              commonutil.get_key_value(self.inputparams,'po_number'),'exact')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_number',
                              commonutil.get_key_value(self.inputparams,'supp_number'),'exact')
        commonutil.filter_add(self.queryparams,'order_status',
                              commonutil.get_key_value(self.inputparams,'order_status'),'icontains')
        commonutil.filter_add(self.queryparams,'po_header_id',
                              commonutil.get_key_value(self.inputparams,'po_header_id'),'')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',
                              commonutil.get_key_value(self.inputparams,'supplier'),'')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',
                              commonutil.get_key_value(self.inputparams,'supplier_id'),'')
        commonutil.filter_date_range(self.queryparams,'order_status_date',
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
            qs = qs.order_by('-order_status_date','po_number')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                       vat_total=Sum('vat_total'),
                       gross_total=Sum('gross_total'),
                        weight_total=Sum('weight_total'),
                        volume_total=Sum('volume_total'),
                        ingredient_total=Sum('ingredient_total')
                                       )
            if len(qs) == 1:
                detailinstance = qs[0]
                self.detailform = PoHeaderForm(instance=detailinstance)
                parentid = detailinstance.po_header_id
                self.child1 = PoLines.objects.filter(poh_po_header_id__po_header_id=parentid).order_by('poh_po_header_id__po_header_id','sl_no')
                self.rowset2_totals = self.child1.aggregate(
                        qty_ordered_units=Sum('qty_ordered_units'),
                        qty_ordered_cases=Sum('qty_ordered_cases'),
                        qty_goodsin=Sum('qty_goodsin'),
                        qty_balance=Sum('qty_balance'),
                        weight_total=Sum('weight_total'),
                        volume_total=Sum('volume_total'),
                       net_price=Sum('net_price'),
                        tax_price=Sum('tax_price'))
                self.child2 = PoGrnHeaders.objects.filter(po_header_id=parentid)
                self.rowset3_totals = self.child2.aggregate(net_total=Sum('net_total'),
                                           vat_total=Sum('vat_total'),
                                           gross_total=Sum('gross_total'),
                                           weight_total=Sum('weight_total'),
                                           volume_total=Sum('volume_total'),
                                           ingredient_total=Sum('ingredient_total')
                                           )
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
            context['tabletitle'] = 'Purchase Orders'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'], context['rows_tablecolumns'] , context[
                     'rows_tablefooter']  = enquirygrids.po_grid()

        if  self.child1:
            context['tabletitle2'] = 'PO Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'], context['rowset2_tablecolumns'] , context[
                     'rowset2_tablefooter']  = enquirygrids.poline_grid('row2.','rowset2_totals.')
        if self.object_list:
            context['tabletitle3'] = 'Goods In'
            context['rowset3'] = self.child2
            context['rowset3_totals'] = self.rowset3_totals
            context['rowset3_tableheader'], context['rowset3_tablecolumns'] , context[
                     'rowset3_tablefooter']  = enquirygrids.grn_grid('row3.','rowset3_totals')
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Order Detail'
        print('******* set context')
        return context
