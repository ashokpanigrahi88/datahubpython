from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindInvoiceForm
from enquiry import enquirygrids

from  datetime import datetime, date

from common.models  import (ApInvoiceHeaders, ApInvoiceLines, ApPaymentHeaders, ApPaymentLines)
from common import (commonutil,sysutil)
from django import forms

#Create your form here

class ApInvSummaryForm(FindInvoiceForm):
    supp_invoice = forms.CharField(max_length=30,required=False,initial="", label="Supplier Invoice",
                                    widget=forms.TextInput(attrs={'style': 'width:100px'}))

    supp_number = forms.CharField(max_length=30,label='Supplier Number',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    supplier = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs={'style': 'width:175px'},
                                        choices=sysutil.populatelistitem(None,sysutil.AP_SUPPLIERS_L
                                                                         )))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ApInvSummaryForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:apinvoicesum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ApInvSummaryView(ListView):
    model = ApInvoiceHeaders
    template_name = 'enquiry/apinvsummary.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    queryparams = {}
    emptysearch = True
    invlines = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}

    def get(self, request, *args, **kwargs):
        self.suppinvoice =  self.request.GET.get('supp_invoice')
        self.invoicenumber = self.request.GET.get('invoice_number')
        self.suppnumber = self.request.GET.get('supp_number')
        self.batchname = self.request.GET.get('batch_name')
        self.supplier = self.request.GET.get('supplier')
        self.supplierid = self.request.GET.get('supplier_id')
        self.invoicetype = self.request.GET.get('invoice_type')
        self.invoicestatus  = self.request.GET.get('invoice_status')
        self.balancetotal  = self.request.GET.get('balance_total')
        self.lineinvoiceid = self.request.GET.get('line_invoice_id')
        self.datefrom = self.request.GET.get('date_from')
        self.dateto = self.request.GET.get('date_to')
        print(self.datefrom, self.dateto)

        print( commonutil.string_to_date(self.datefrom), commonutil.string_to_date(self.dateto))
        self.initial =  {'supp_invoice': self.suppinvoice,
                    'invoice_number': self.invoicenumber,
                    'supp_number':self.suppnumber,
                    'batch_name':  self.batchname,
                    'supplier' : self.supplier,
                    'invoice_type' : self.invoicetype,
                    'invoice_status': self.invoicestatus,
                    'balance_total': self.balancetotal,
                    'date_from': self.datefrom,
                    'date_to': self.dateto
                         }
        return super(ApInvSummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ApInvSummaryView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'voucher_num',self.suppinvoice,'exact')
        commonutil.filter_add(self.queryparams,'invoice_number',self.invoicenumber,'exact')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',self.supplier,"",'int')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',self.supplierid,"",'int')
        commonutil.filter_add(self.queryparams,'invoice_status',self.invoicestatus,'exact')
        commonutil.filter_add(self.queryparams,'invoice_type',self.invoicetype,'exact')
        commonutil.filter_add(self.queryparams,'batch_name',self.batchname,'startswith')
        commonutil.filter_add(self.queryparams,'invoice_status',self.invoicestatus,'exact')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_number',self.suppnumber,"exact")
        commonutil.filter_add(self.queryparams,'balance_total', self.balancetotal , "filter",'int')
        commonutil.filter_date_range(self.queryparams,'invoice_received_date', self.datefrom, self.dateto ,'str')
        if not self.queryparams:
            print('empty querying',self.queryparams)
            return self.model.objects.none()
        else:
            print('querying',self.queryparams)
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-invoice_status_date','invoice_number')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                       vat_total=Sum('vat_total'),
                       gross_total=Sum('gross_total'),
                        balance_total=Sum('balance_total'),
                        paid_total=Sum('paid_total'))
            if len(qs) == 1:
                invoiceid = qs[0].invoice_id
                self.invlines = ApInvoiceLines.objects.filter(invoice_id__invoice_id=invoiceid)
                self.rowset2_totals = self.invlines.aggregate(qty_invoiced_units=Sum('qty_invoiced_units'),
                       invoice_amount_exl_tax=Sum('invoice_amount_exl_tax'),
                       net_amount=Sum('net_amount'),
                        tax_amount=Sum('tax_amount'),
                        total_line_amount=Sum('total_line_amount'))
                self.pmntlines = ApPaymentLines.objects.filter(invoice_id__invoice_id=invoiceid)
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
        self.form = ApInvSummaryForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Invoices'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'] , context['rows_tablecolumns'] , context['rows_tablefooter'], = enquirygrids.apinv_grid()
        print('pmntlines:',self.pmntlines)
        if  self.invlines:
            context['tabletitle2'] = 'Invoice Lines'
            context['rowset2'] = self.invlines
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'] , context['rowset2_tablecolumns'] , context[
                            'rowset2_tablefooter'], = enquirygrids.apinvline_grid('row2.','rowset2_totals.')
        if self.pmntlines:
            context['tabletitle3'] = 'Payments'
            context['rowset3'] = self.pmntlines
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], context[
                'rowset3_tablefooter'], = enquirygrids.pmnt_grid('row3.', 'rowset3_totals.')

        print('******* set context')
        return context
