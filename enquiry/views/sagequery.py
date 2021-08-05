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
REP_SAGETRANSEXPORT_V={
'fields':['trans_id','trans_type','report_date','account_ref','gl_code','net_amount','tax_amount','exchange_rate',
          'trans_reference','payment_method','operatorname','account_name','trans_source','extra_reference',],
'headers':['Trans_Id','Sage Type','Date','AccountNumber','GL Code','Net Amount','Tax Amount ','XchangeRate',
           'Reference','Payment Method','User','Account Name','Source','Extra Reference',],
}


class DetailForm(ModelForm):

    class Meta:
        model = None
        fields = '__all__'
        exclude = ('customer_id',)


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindDateForm):

    transaction_type  = forms.CharField(max_length=30,label='Transaction Type',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    account_ref = forms.CharField(max_length=30,label='Account Reference',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    account_code = forms.CharField(max_length=30,label='Account Code ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    account_name = forms.CharField(max_length=30,label='Account Name ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    trans_source = forms.CharField(max_length=30,label='Source ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    trans_reference = forms.CharField(max_length=30,label='Trans Reference ',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))
    payment_method = forms.CharField(max_length=30,label='Payment Method',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))


    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = False
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:sagequery'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = ArInvoiceHeaders
    template_name = 'enquiry/sagequery.html'
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
        return super(SummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(SummaryView, self).get_form_kwargs()
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
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'trans_type',
                              commonutil.get_key_value(self.inputparams,'transaction_type'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'trans_reference',
                              commonutil.get_key_value(self.inputparams,'trans_reference'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'trans_source',
                              commonutil.get_key_value(self.inputparams,'trans_source'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'payment_method',
                              commonutil.get_key_value(self.inputparams,'payment_method'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'account_ref',
                              commonutil.get_key_value(self.inputparams,'account_ref'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'account_name',
                              commonutil.get_key_value(self.inputparams,'account_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'gl_code',
                              commonutil.get_key_value(self.inputparams,'account_code'),' like ')
        self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'report_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """Select trans_id,trans_type,report_date,account_ref,gl_code,net_amount,tax_amount,exchange_rate,
                    trans_reference,payment_method,operatorname,account_name,trans_source,extra_reference
                    From REP_SAGETRANSEXPORT_V {}  order by report_date desc,trans_type  """.format(self.queryparams)
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
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.get_grid('SAGEQUERY')
        return context
