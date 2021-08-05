from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum, Count
from enquiry.forms import FindReqForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (InvRequisitionHeaders, InvRequisitionLines)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class DetailForm(ModelForm):

    class Meta:
        model = InvRequisitionHeaders
        fields = '__all__'
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindReqForm):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(InvRequisitionHeaders)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:reqsum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvRequisitionHeaders
    template_name = 'enquiry/reqsum.html'
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
        self.queryparams = {}
        self.detailform  = None
        commonutil.filter_add(self.queryparams,'requisition_number',
                              commonutil.get_key_value(self.inputparams,'requisition_number'),'exact')
        commonutil.filter_add(self.queryparams,'requisition_type',
                              commonutil.get_key_value(self.inputparams,'req_type'),'exact')
        commonutil.filter_add(self.queryparams,'batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'startswith')
        commonutil.filter_add(self.queryparams,'requisition_status',
                              commonutil.get_key_value(self.inputparams,'req_status'),'exact')
        commonutil.filter_add(self.queryparams,'phase_code',
                              commonutil.get_key_value(self.inputparams,'phase_code'),'icontains')
        commonutil.filter_add(self.queryparams,'requisition_id',
                              commonutil.get_key_value(self.inputparams,'requisition_id'),'')
        commonutil.filter_add(self.queryparams,'location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'picked_location_id'),'')
        commonutil.filter_add(self.queryparams,'from_location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'picked_location'),'')
        commonutil.filter_add(self.queryparams,'to_location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'received_location'),'')
        commonutil.filter_date_range(self.queryparams,'requisition_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        if not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-requisition_status_date','requisition_number')
            self.totals = None
            if len(qs) == 1:
                detailinstance = qs[0]
                self.detailform = DetailForm(instance=detailinstance)
                parentid = detailinstance.requisition_id
                self.child1 = InvRequisitionLines.objects.filter(requisition_id__requisition_id=parentid).order_by(
                'requisition_id__requisition_id','sl_no' )
                self.rowset2_totals = self.child1.aggregate(
                    qty_requested_units= Sum('qty_requested_units'),
                    qty_fullfilled_units= Sum('qty_fullfilled_units'),
                    qty_allocated_units= Sum('qty_allocated_units'),
                    qty_cancelled_units= Sum('qty_cancelled_units'),
                    qty_difference_units= Sum('qty_difference_units'),
                    qty_received_units=Sum('qty_received_units'),
                    qty_balance_units= Sum('qty_balance_units'))
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
            context['tabletitle'] = 'Requisition'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.get_grid('REQH')

        if  self.child1:
            context['tabletitle2'] = 'Requisition Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                           'rowset2_tablefooter'] = enquirygrids.get_grid('REQLINE', 'row2.', 'rowset2_totals.')

        if self.child2:
            context['tabletitle3'] = 'Picked Lines'
            context['rowset3'] = self.child2
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], _ = enquirygrids.arorder_grid()
        context['detailform_title'] = 'Details'
        context['detailform'] = self.detailform
        print('******* set context')
        return context
