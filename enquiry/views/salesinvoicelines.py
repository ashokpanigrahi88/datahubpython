from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindInvoiceForm, FindItemForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ArInvoiceHeaders, ArInvoiceLines, ArPaymentHeaders, ArPaymentLines)
from common import (commonutil,sysutil)
from django import forms

#Create your form here

class InvoiceLineForm(ModelForm):

    class Meta:
        model = ArInvoiceLines
        fields = '__all__'
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(InvoiceLineForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ArInvLineForm(FindInvoiceForm, FindItemForm):

    customer = forms.CharField(max_length=30,label='Customer',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                                        ))

    line_status = forms.CharField(max_length=30,label='Line Status',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small'],
                                                        ))

    phase_code = forms.CharField(max_length=30,label='Line Status',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small'],
                                                        ))

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(ArInvoiceLines)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ArInvLineForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:salesinvoicelines'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ArInvLinesView(ListView):
    model = ArInvoiceLines
    template_name = 'enquiry/salesinvoicelines.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    linequery = {}
    paymentquery = {}
    emptysearch = True
    invlines = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(ArInvLinesView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ArInvLinesView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'invoice_header_id__invoice_number',
                              commonutil.get_key_value(self.inputparams,'invoice_number'),'exact')
        commonutil.filter_add(self.queryparams,'invoice_header_id__invoice_type',
                              commonutil.get_key_value(self.inputparams,'invoice_type'),'exact')
        commonutil.filter_add(self.queryparams,'invoice_header_id__batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'startswith')
        commonutil.filter_add(self.queryparams,'invoice_header_id__invoice_status',
                              commonutil.get_key_value(self.inputparams,'invoice_status'),'exact')
        commonutil.filter_add(self.queryparams,'invoice_line_status',
                              commonutil.get_key_value(self.inputparams,'line_status'),'icontains')
        commonutil.filter_add(self.queryparams,'phase_code',
                              commonutil.get_key_value(self.inputparams,'phase_code'),'icontains')
        commonutil.filter_add(self.queryparams,'invoice_line_id',
                              commonutil.get_key_value(self.inputparams,'invoice_line_id'),'')
        commonutil.filter_add(self.queryparams,'invoice_header_id__balance_total',
                              commonutil.get_key_value(self.inputparams,'balance_total') , "filter",'int')
        commonutil.filter_date_range(self.queryparams,'invoice_line_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,'item_id__item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'),'exact')
        commonutil.filter_add(self.queryparams,'item_id__item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),'icontains')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        if not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            print(qs.query)
            customerfilter = commonutil.get_key_value(self.inputparams,'customer')
            if commonutil.hasstrvalue(customerfilter):
                qs = qs.filter(Q(customer_id__customer_number=customerfilter ) |
                    Q(customer_id__customer_name__icontains=customerfilter))

            print(qs.query)
            qs = qs.order_by('invoice_header_id','sl_no')
            self.totals = qs.aggregate(qty_invoiced_units=Sum('qty_invoiced_units'),
                   invoice_unit_so=Sum('invoice_unit_sp'),
                   net_amount=Sum('net_amount'),
                    tax_amount=Sum('tax_amount'),
                    total_line_amount=Sum('total_line_amount'))
            if len(qs) == 1:
                detailinstance  = qs[0]
                self.detailform = InvoiceLineForm(instance=detailinstance)

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
        self.form = ArInvLineForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Invoices Lines'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'] ="""
                                <th>ID</th>
                                <th>Invoice Number</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Location</th>
                                <th>Customer Name </th>
                                <th>Item Number </th>
                                <th>Item Name </th>
                                <th>Line Status </th>
                                     <th> Tax Rate </th>
                                     <th> Qty </th>
                                     <th> Price </th>
                                     <th> Net </th>
                                     <th> Tax </th>
                                     <th> Total </th> """
            context['rows_tablecolumns'] = """               
               <td> <a href={% url 'enquiry:salesinvoicelines' %}?invoice_line_id={{row.invoice_line_id}}>{{row.invoice_line_id}}</a></td>
                    <td>  <a href={% url 'enquiry:arinvoicesum' %}?invoice_number={{row.invoice_header_id.invoice_number }}>{{row.invoice_header_id.invoice_number }}</a> </td>
                    <td>{{row.invoice_line_status_date|date:"SHORT_DATE_FORMAT"  }}</td>
                    <td>{{row.invoice_header_id.invoice_status }}</td>
                    <td>{{row.invoice_header_id.shipfrom_location_id }}</td>
                    <td>{{row.invoice_header_id.customer_id.customer_name }}</td>
            <td>{{row.item_id.item_number}}</td>
            <td>{{row.item_name }}</td>
            <td>{{row.invoice_line_status }}</td>
            <td>{{row.tax_rate }}</td>
            <td>{{row.qty_invoiced_units }}</td>
            <td>{{row.invoice_unit_sp }}</td>
            <td>{{row.net_amount }}</td>
            <td>{{row.tax_amount }}</td>
            <td>{{row.total_line_amount }}</td>
                    """
            context['rows_tablefooter'] = """
                                <td>Total</td> 
                                <td></td>
                                <td> </td>
                                <td></td>
                                <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td> </td>                    
                        <td>{{rowset_totals.qty_invoiced_units }}</td>
                        <td>{{rowset_totals.invoice_unit_sp }}</td>
                        <td>{{rowset_totals.net_amount }}</td>
                        <td>{{rowset_totals.tax_amount }}</td>
                        <td>{{rowset_totals.total_line_amount }}</td>"""
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Line Details'
        print('******* set context')
        return context
