from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindInvoiceForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ArInvoiceHeaders, ArInvoiceLines, ArPaymentHeaders, ArPaymentLines)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class InvoiceForm(ModelForm):

    class Meta:
        model = ArInvoiceHeaders
        fields = '__all__'
        exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ArInvSummaryForm(FindInvoiceForm):

    customer = forms.CharField(max_length=30,label='Customer',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},
                                                        ))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ArInvSummaryForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:arinvoicesum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ArInvSummaryView(ListView):
    model = ArInvoiceHeaders
    template_name = 'enquiry/arinvsummary.html'
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
        return super(ArInvSummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ArInvSummaryView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'invoice_header_id',
                              commonutil.get_key_value(self.inputparams,'invoice_header_id'),'')
        commonutil.filter_add(self.queryparams,'order_header_id',
                              commonutil.get_key_value(self.inputparams,'order_header_id'),'')
        commonutil.filter_add(self.queryparams,'customer_id__customer_id',
                              commonutil.get_key_value(self.inputparams,'customer_id'),'')
        commonutil.filter_add(self.queryparams,'invoice_number',
                              commonutil.get_key_value(self.inputparams,'invoice_number'),'exact')
        commonutil.filter_add(self.queryparams,'invoice_type',
                              commonutil.get_key_value(self.inputparams,'invoice_type'),'exact')
        commonutil.filter_add(self.queryparams,'batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'startswith')
        commonutil.filter_add(self.queryparams,'invoice_status',
                              commonutil.get_key_value(self.inputparams,'invoice_status'),'exact')
        commonutil.filter_add(self.queryparams,'balance_total',
                              commonutil.get_key_value(self.inputparams,'balance_total') , "filter",'int')
        commonutil.filter_date_range(self.queryparams,'invoice_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        if not self.queryparams:
            return self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            customerfilter = commonutil.get_key_value(self.inputparams,'customer')
            if commonutil.hasstrvalue(customerfilter):
                qs = qs.filter(Q(customer_id__customer_number=customerfilter ) |
                    Q(customer_id__customer_name__icontains=customerfilter))
            qs = qs.order_by('-invoice_status_date','invoice_number')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                   vat_total=Sum('vat_total'),
                   gross_total=Sum('gross_total'),
                    balance_total=Sum('balance_total'),
                    paid_amount=Sum('paid_amount'))
            if len(qs) == 1:
                invoiceinstance  = qs[0]
                self.detailform = InvoiceForm(instance=invoiceinstance)
                invoiceid = invoiceinstance.invoice_header_id
                self.invlines = ArInvoiceLines.objects.filter(invoice_header_id__invoice_header_id=invoiceid).order_by(
                'invoice_header_id','sl_no' )
                self.rowset2_totals = self.invlines.aggregate(qty_invoiced_units=Sum('qty_invoiced_units'),
                   invoice_unit_so=Sum('invoice_unit_sp'),
                   net_amount=Sum('net_amount'),
                    tax_amount=Sum('tax_amount'),
                    total_line_amount=Sum('total_line_amount'))
                self.pmntlines = ArPaymentLines.objects.filter(invoice_header_id__invoice_header_id=invoiceid)

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
        self.form = commonutil.initalise_find_form(ArInvSummaryForm)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Invoices'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'], = enquirygrids.arinv_grid()
        print('pmntlines:',self.pmntlines)
        if  self.invlines:
            context['tabletitle2'] = 'Invoice Lines'
            context['rowset2'] = self.invlines
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                'rowset2_tablefooter'], = enquirygrids.arinvline_grid('row2.','rowset2_totals')
        if self.pmntlines:
            context['tabletitle3'] = 'Payments'
            context['rowset3'] = self.pmntlines
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], context[
                'rowset3_tablefooter'], = enquirygrids.pmnt_grid('row3.','rowset3_totals')
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Invoice Details'
        print('******* set context')
        return context
