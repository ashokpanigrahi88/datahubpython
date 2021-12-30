from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindSupplierForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ApSuppliers, ApInvoiceLines, ApInvoiceHeaders, PoHeaders, PoGrnHeaders)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class DetailForm(ModelForm):

    class Meta:
        model = ApSuppliers
        fields = '__all__'
        exclude = ('supplier_id',)


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindSupplierForm, FindDateForm):

    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = False
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:supplierdrilldown'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class DrilldownView(ListView):
    model = ApSuppliers
    template_name = 'enquiry/supplierdrilldown.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    child1 = child2 = child3 = child4 = None
    rowset_totals = rowset2_totals = rowset3_totals = rowset4_totals  =  {}
    parentid = None

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(DrilldownView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(DrilldownView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'supplier_number',
                              commonutil.get_key_value(self.inputparams,'supplier_number'),'exact')
        commonutil.filter_add(self.queryparams,'supplier_id',
                              commonutil.get_key_value(self.inputparams,'supplier_id'))
        commonutil.filter_add(self.queryparams,'supplier_name',
                              commonutil.get_key_value(self.inputparams,'supplier_name'),'icontains')
        commonutil.filter_add(self.queryparams,'address_line1',
                              commonutil.get_key_value(self.inputparams,'address_line1'),'icontains')
        commonutil.filter_add(self.queryparams,'post_code',
                              commonutil.get_key_value(self.inputparams,'post_code'),'icontains')
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
            qs = qs.order_by('supplier_name')
            if len(qs) == 1:
                detailinstance  = qs[0]
                self.parentid = detailinstance.supplier_id
                self.detailform = DetailForm(instance=detailinstance)
                self.child1 = PoHeaders.objects.filter(sup_supplier_id__supplier_id=self.parentid).order_by('-order_status_date')[:20]
                if self.child1:
                    self.rowset2_totals = self.child1.aggregate(net_total=Sum('net_total'),
                               vat_total=Sum('vat_total'),
                               gross_total=Sum('gross_total'),
                                weight_total=Sum('weight_total'),
                                volume_total=Sum('volume_total'),
                                ingredient_total=Sum('ingredient_total')
                                               )
                self.child2 = PoGrnHeaders.objects.filter(sup_supplier_id__supplier_id=self.parentid).order_by('-grn_status_date')[:20]
                if self.child2:
                    self.rowset3_totals = self.child2.aggregate(net_total=Sum('net_total'),
                                               vat_total=Sum('vat_total'),
                                               gross_total=Sum('gross_total'),
                                               weight_total=Sum('weight_total'),
                                               volume_total=Sum('volume_total'),
                                               ingredient_total=Sum('ingredient_total')
                                               )
                self.child3 = ApInvoiceHeaders.objects.filter(sup_supplier_id__supplier_id=self.parentid).order_by('-invoice_status_date')[:20]
                if self.child3:
                    self.rowset4_totals =self.child3.aggregate(net_total=Sum('net_total'),
                               vat_total=Sum('vat_total'),
                               gross_total=Sum('gross_total'),
                                balance_total=Sum('balance_total'),
                                paid_total=Sum('paid_total'))
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
        self.form = FindForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.supplier_grid()
        if  self.child1:
            context['tabletitle2'] = """Last 20 PO(<a href={% url 'enquiry:posum' %}?supplier_id="""+str(self.parentid)+""">All </a>)"""
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['parentid'] = self.parentid
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                    'rowset2_totals'] = enquirygrids.po_grid('row2.','rowset2_totals.')
        if self.child2:
            context['tabletitle3'] = """Last 20 Goods In(<a href={% url 'enquiry:grnsum' %}?supplierr_id="""+str(self.parentid)+""">All </a>)"""
            context['rowset3'] = self.child2
            context['rowset3_totals'] = self.rowset3_totals
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], context[
                    'rowset3_totals']  = enquirygrids.grn_grid('row3.','rowset3_totals.')
        if self.child3:
            context['tabletitle4'] = """Last 20 Invoices(<a href={% url 'enquiry:apinvoicesum' %}?supplier_id="""+str(self.parentid)+""">All </a>)"""
            context['rowset4'] = self.child3
            context['rowset4_totals'] = self.rowset4_totals
            context['rowset4_tableheader'], context['rowset4_tablecolumns'], context[
                    'rowset4_totals'] = enquirygrids.apinv_grid('row4.','rowset4_totals.')
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Details'
        print('******* set context')
        return context
