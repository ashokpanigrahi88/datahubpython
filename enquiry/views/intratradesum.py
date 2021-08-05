from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from enquiry.forms import FindCustomerForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm

from common.models  import (ArCustomers, ArInvoiceHeaders, ArInvoiceLines)
from common import (commonutil,sysutil, dbfuncs)
from django import forms
from enquiry import enquirygrids

#Create your form here
COLUMNS = ['commodity_code','item_number','item_name','qty_invoiced_units','net_total_after_discount',
          'netweight','netvolume','country_region_code',
          'invoice_number','invoice_status_date',
          'billto_country_code','customer_name']

class CustomerForm(ModelForm):

    class Meta:
        model = ArCustomers
        fields = '__all__'
        exclude = ('customer_id',)


    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindDateForm):
    country_code = forms.CharField(max_length=30,label='Country Code',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small']))

    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    customer_number = forms.CharField(max_length=30,label='Customer Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    customer_name = forms.CharField(max_length=30,label='Customer Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    invoice_number = forms.CharField(max_length=30,label='Invoice Number',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    commodity_code = forms.CharField(max_length=30,label='Commodity Code',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))


    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = False
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:intratradesum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class IntraTradeSumView(ListView):
    model = ArInvoiceHeaders
    template_name = 'enquiry/intratradesum.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = ""
    child1 = None
    child2 = None

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        self.initial =  self.inputparams
        return super(IntraTradeSumView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(IntraTradeSumView, self).get_form_kwargs()
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
        self.queryparams = ""
        self.detailform  = None
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'customer_name',
                              commonutil.get_key_value(self.inputparams,'customer_name'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'customer_id',
                              commonutil.get_key_value(self.inputparams,'customer_id'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'commodity_code',
                              commonutil.get_key_value(self.inputparams,'commodity_code'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'billto_country_code',
                              commonutil.get_key_value(self.inputparams,'country_code'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'invoice_number',
                              commonutil.get_key_value(self.inputparams,'invoice_number'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'commodity_code',
                              commonutil.get_key_value(self.inputparams,'commodity_code'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),' like ')
        self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'invoice_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """Select commodity_code,item_number,item_name,qty_invoiced_units,net_total_after_discount,
                    netweight,netvolume,country_region_code,
                        invoice_number,invoice_status_date, billto_country_code,customer_name,
                        customer_id, invoice_header_id
                    From REP_INTRASTATE_V  {}  order by invoice_status_date desc """.format(self.queryparams)
            qs  = dbfuncs.exec_sql(sql, 'dict', columnscase='lower')
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
        self.form = FindForm(initial=self.initial)
        # Add local context
        context['form'] = self.form
        if self.object_list:
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.commoditycode_grid()
        return context
