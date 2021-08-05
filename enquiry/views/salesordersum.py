from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindSalesOrderForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ArSalesorderHeaders, ArSalesorderLines, ArSalesorderPicklist, ArInvoiceHeaders)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class OrderForm(ModelForm):

    class Meta:
        model = ArSalesorderHeaders
        fields = '__all__'
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ArOrderForm(FindSalesOrderForm):

    phase_code = forms.CharField(max_length=30,label='Phase Code',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small'],
                                                        ))

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(ArSalesorderHeaders)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ArOrderForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:salesordersum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ArOrderView(ListView):
    model = ArSalesorderHeaders
    template_name = 'enquiry/salesordersum.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    detailform = None
    linequery = {}
    emptysearch = True
    child1 = None
    child2 = None
    child3 = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        self.initial =  self.inputparams
        return super(ArOrderView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ArOrderView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'order_number',
                              commonutil.get_key_value(self.inputparams,'order_number'),'exact')
        commonutil.filter_add(self.queryparams,'order_type',
                              commonutil.get_key_value(self.inputparams,'order_type'),'exact')
        commonutil.filter_add(self.queryparams,'batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'startswith')
        commonutil.filter_add(self.queryparams,'order_status',
                              commonutil.get_key_value(self.inputparams,'order_status'),'exact')
        commonutil.filter_add(self.queryparams,'order_line_status',
                              commonutil.get_key_value(self.inputparams,'line_status'),'icontains')
        commonutil.filter_add(self.queryparams,'phase_code',
                              commonutil.get_key_value(self.inputparams,'phase_code'),'icontains')
        commonutil.filter_add(self.queryparams,'order_header_id',
                              commonutil.get_key_value(self.inputparams,'order_header_id'),'')
        commonutil.filter_add(self.queryparams,'customer_id__customer_id',
                              commonutil.get_key_value(self.inputparams,'customer_id'),'')
        commonutil.filter_date_range(self.queryparams,'order_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        print('orderquery:',self.queryparams)
        if not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            customerfilter = commonutil.get_key_value(self.inputparams,'customer')
            if commonutil.hasstrvalue(customerfilter):
                qs = qs.filter(Q(customer_id__customer_number=customerfilter ) |
                    Q(customer_id__customer_name__icontains=customerfilter))
            qs = qs.order_by('-order_status_date','order_number')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                   vat_total=Sum('vat_total'),
                   gross_total=Sum('gross_total'),)
            if len(qs) == 1:
                detailinstance = qs[0]
                self.detailform = OrderForm(instance=detailinstance)
                parentid = detailinstance.order_header_id
                self.child1 = ArSalesorderLines.objects.filter(order_header_id__order_header_id=parentid).order_by(
                'order_header_id','sl_no' )
                self.rowset2_totals = self.child1.aggregate(
                qty_userpicked_units=Sum('qty_userpicked_units'),
                qty_picked_units=Sum('qty_picked_units'),
                   order_unit_so=Sum('order_unit_sp'),
                   net_amount=Sum('net_amount'),
                    tax_amount=Sum('tax_amount'),
                    total_line_amount=Sum('total_line_amount'))
                self.child2 = ArSalesorderPicklist.objects.filter(order_header_id__order_header_id=parentid)
                self.child3 = ArInvoiceHeaders.objects.filter(order_header_id__order_header_id=parentid)
        self.object_list = qs
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
        self.form = commonutil.initalise_find_form(ArOrderForm)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Orders'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'], context['rows_tablecolumns'], context['rows_tablefooter'] = enquirygrids.arorder_grid()
        if  self.child1:
            context['tabletitle2'] = 'Order Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                'rowset2_tablefooter'] = enquirygrids.arorderline_grid('row2.','rowset2_totals.')
        if self.child2:
            context['tabletitle3'] = 'Picked Lines'
            context['rowset3'] = self.child2
            context['rowset3_tableheader'], context['rowset3_tablecolumns'],_ = enquirygrids.arorderpick_grid('row3.','rowset3_totals.')
        context['tabletitle4'] = 'No Invocie'
        if self.child3:
            context['tabletitle4'] = 'Invocies'
            context['rowset4'] = self.child3
            context['rowset4_tablefooter'] = None
            context['rowset4_tableheader'], context['rowset4_tablecolumns'], _ = enquirygrids.arinv_grid('row4.','rowset4_totals.')
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Order Details'
        print('******* set context')
        return context
