from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q, F
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import  FindDateForm, ModelFieldsForm, SupplierForm, SupplierTransForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ApDbnoteLines, ApDbnoteHeaders)
from common import (commonutil, sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class DbNoteForm(ModelForm):
    class Meta:
        model = ApDbnoteHeaders
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(DbNoteForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ApDbNoteForm(FindDateForm, SupplierForm):
    dbnote_number = forms.CharField(max_length=30, label='DebitNote Number', required=False,
                                    widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'], ))
    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(ApDbnoteHeaders)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        kwargs.update({'modelobject': ApDbnoteHeaders})
        super(ApDbNoteForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = False
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.

PAGE_VAR = 14
REVERSE = 'enquiry:dbnotesum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ApDbnoteSumView(ListView):
    model = ApDbnoteHeaders
    template_name = 'enquiry/dbnotesum.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    totals = None
    child1 = None
    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        self.initial =  self.inputparams
        return super(ApDbnoteSumView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ApDbnoteSumView, self).get_form_kwargs()
        kwargs['hiddenfields'] = []
        kwargs['modelobject'] = ApDbnoteHeaders
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
        commonutil.filter_add(self.queryparams,'dbnote_number',
                              commonutil.get_key_value(self.inputparams,'dbnote_number'),'exact')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_name',
                              commonutil.get_key_value(self.inputparams,'supplier_name'),'icontains')
        commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_number',
                              commonutil.get_key_value(self.inputparams,'supplier_number'),'icontains')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        commonutil.filter_date_range(self.queryparams,'dbnote_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        if not self.queryparams and commonutil.iskeyempty(self.inputparams,'search'):
            return self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-dbnote_date')
            self.totals = qs.aggregate(net_total=Sum('net_total'),
                   vat_total=Sum('vat_total'),
                   gross_total=Sum('gross_total'))
            if len(qs) == 1:
                objectinstance  = qs[0]
                print(objectinstance)
                self.detailform = DbNoteForm(instance=objectinstance)
                parentid = objectinstance.dbnote_id
                self.child1 = ApDbnoteLines.objects.filter(dbnote_id=parentid).order_by(
                                                'dbnote_id','sl_no' )
                self.rowset2_totals = self.child1.aggregate(
                    qty_ordered_units=Sum('qty_ordered_units'),
                    qty_invoiced_units=Sum('qty_invoiced_units'),
                    qty_dbnote_units=Sum('qty_dbnote_units'),
                    qty_received_units=Sum('qty_received_units'),
                    qty_delivered_units=Sum('qty_delivered_units'),
                   unit_co=Sum('unit_cp'),
                   invoiced_price=Sum('invoiced_price'),
                   net_price=Sum('net_price'),
                    tax_price=Sum('tax_price'),
                    total_price=Sum(F('net_price')+F('tax_price')))
                #self.pmntlines = ArPaymentLines.objects.filter(invoice_header_id__invoice_header_id=invoiceid)
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
        self.form = ApDbNoteForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['rowset_totals'] = self.totals
            context['rows_tableheader'],  context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.get_grid('DBNHEADER')
        if self.child1:
            context['tabletitle2'] = 'Debit Note Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'],  context['rowset2_tablecolumns'], context[
                'rowset2_tablefooter'] = enquirygrids.get_grid('DBNLINE','row2.','rowset2_totals.')
        context['detailform_title'] = 'Debitnote Details'
        context['detailform'] = self.detailform
        print('******* set context')
        return context
