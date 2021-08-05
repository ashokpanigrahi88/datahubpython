from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindCustomerForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ArCustomers, ArInvoiceHeaders, ArSalesorderHeaders)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class CustomerForm(ModelForm):

    class Meta:
        model = ArCustomers
        fields = '__all__'
        exclude = ('customer_id',)


    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ArCustomerForm(FindCustomerForm, FindDateForm, ModelFieldsForm):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs={'style': 'width:200px'},
                                        choices=commonutil.choice_modelcharfields(ArCustomers)))
    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False);
    kwargs =  {'modelobject': ArCustomers}
    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(ArCustomerForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = False
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:customerdrilldown'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ArCustDrilldownView(ListView):
    model = ArCustomers
    template_name = 'enquiry/customerdrilldown.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    child1 = None
    child2 = None
    customerid = None

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(ArCustDrilldownView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ArCustDrilldownView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'customer_number',
                              commonutil.get_key_value(self.inputparams,'customer_number'),'exact')
        commonutil.filter_add(self.queryparams,'customer_id',
                              commonutil.get_key_value(self.inputparams,'customer_id'))
        commonutil.filter_add(self.queryparams,'customer_name',
                              commonutil.get_key_value(self.inputparams,'customer_name'),'icontains')
        commonutil.filter_add(self.queryparams,'billto_address_line1',
                              commonutil.get_key_value(self.inputparams,'billto_address_line1'),'icontains')
        commonutil.filter_add(self.queryparams,'billto_post_code',
                              commonutil.get_key_value(self.inputparams,'billto_post_code'),'icontains')
        commonutil.filter_add(self.queryparams,'shipto_address_line1',
                              commonutil.get_key_value(self.inputparams,'shipto_address_line1'),'icontains')
        commonutil.filter_add(self.queryparams,'shipto_post_code',
                              commonutil.get_key_value(self.inputparams,'shipto_post_code'),'icontains')
        commonutil.filter_add(self.queryparams,'email',
                              commonutil.get_key_value(self.inputparams,'email'),'icontains')
        commonutil.filter_add(self.queryparams,'phone1',
                              commonutil.get_key_value(self.inputparams,'phone1'),'icontains')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        commonutil.filter_date_range(self.queryparams,'last_update_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        if not self.queryparams and commonutil.iskeyempty(self.inputparams,'search'):
            return self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('customer_name')
            if len(qs) == 1:
                objectinstance  = qs[0]
                parentid = objectinstance.customer_id
                self.customerid = parentid
                self.detailform = CustomerForm(instance=objectinstance)
                self.child1 = ArInvoiceHeaders.objects.filter(customer_id__customer_id=parentid).order_by('-invoice_status_date')[:20]
                self.child2 = ArSalesorderHeaders.objects.filter(customer_id__customer_id=parentid).order_by('-order_status_date')[:20]
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
        self.form = ArCustomerForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.customer_grid()
        if  self.child1:
            context['tabletitle2'] = """Last 20 Invoices(<a href={% url 'enquiry:arinvoicesum' %}?customer_id="""+str(self.customerid)+""">All </a>)"""
            context['rowset2'] = self.child1
            context['rowset2_totals'] = None
            context['parentid'] = self.customerid
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], _ = enquirygrids.arinv_grid('row2.','rowset2_totals')
        if self.child2:
            context['tabletitle3'] = """Last 20 Orders(<a href={% url 'enquiry:salesordersum' %}?customer_id="""+str(self.customerid)+""">All </a>)"""
            context['rowset3'] = self.child2
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], _ = enquirygrids.arorder_grid('row3.','rowset3_totals.')
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Customer Details'
        print('******* set context')
        return context
