from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum, Count
from enquiry.forms import FindMovementForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (InvItemMovementHeaders, InvItemMovementLines)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here
INV_ITEM_MOVEMENT_LINES={
'fields':['to_location_id','to_sub_location_id','item_movement_line_id','iimh_item_movement_header_id','created_by',
          'bu_id','creation_date','last_updated_by','record_status','last_update_date','update_source','delete_flag',
          'iim_item_id','item_number','item_name','qty_instock','qty_inlocation','quantity','sub_location_id',
          'qty_goodsin','qty_rejected','total_grned','reason_for_rejection','rejection_sub_location',
          'rejection_sub_location_id','notes','notes_destination','reason_code_id',],
'headers':['To Location','To Sub Location','Item Movment Line Id','Iimh Item Movement Header Id','Created By',
           'Bu Id','Creation Date','Last Updated By','Record Status','Last Update Date','Update Source','Delete Flag',
           'Iim Item Id','Item Number','Item Name','Total Location  Stock','Qty inStock','Qty TransferTo Location',
           'To Sub Location','QtyGoodsIn','QtyRejected','TotalGRNed','RejectionReason','Rejection Sub Location',
           'To Sub Location','Notes (Source)','Notes Destination','Reason',],
}

class DetailForm(ModelForm):

    class Meta:
        model = InvItemMovementHeaders
        fields = '__all__'
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindMovementForm):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(InvItemMovementLines)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 20
REVERSE = 'enquiry:itemmovements'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvItemMovementLines
    template_name = 'enquiry/itemmovements.html'
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
        commonutil.filter_add(self.queryparams,'iimh_item_movement_header_id__batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'icoantains')
        commonutil.filter_add(self.queryparams,'iimh_item_movement_header_id__movement_type',
                              commonutil.get_key_value(self.inputparams,'movement_type'),'icontains')
        commonutil.filter_add(self.queryparams,'item_id__item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'),'exact')
        commonutil.filter_add(self.queryparams,'item_id__item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),'icontains')
        commonutil.filter_add(self.queryparams,'iimh_item_movement_header_id__header_movement_status',
                              commonutil.get_key_value(self.inputparams,'movement_status'),'exact')
        commonutil.filter_add(self.queryparams,'iimh_item_movement_header_id__movement_type',
                              commonutil.get_key_value(self.inputparams,'movement_type'),'icontains')
        commonutil.filter_add(self.queryparams,'iimh_item_movement_header_id__item_movement_header_id',
                              commonutil.get_key_value(self.inputparams,'movement_id'),'')
        commonutil.filter_add(self.queryparams,'location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'from_location'),'')
        commonutil.filter_add(self.queryparams,'sub_location_id__sub_location',
                              commonutil.get_key_value(self.inputparams,'from_sub_location'),'')
        commonutil.filter_add(self.queryparams,'to_location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'to_location'),'')
        commonutil.filter_add(self.queryparams,'to_sub_location_id__sub_location',
                              commonutil.get_key_value(self.inputparams,'to_sub_location'),'')
        commonutil.filter_date_range(self.queryparams,'iimh_item_movement_header_id__header_movement_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        if not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-iimh_item_movement_header_id__header_movement_status_date','iimh_item_movement_header_id')
            self.totals = None
            parentid = commonutil.get_key_value(self.inputparams,'movement_id')
            if len(qs) == 1:
                parentid =  qs[0].iimh_item_movement_header_id.item_movement_header_id
            if commonutil.hasintvalue(parentid):
                detailinstance = InvItemMovementHeaders.objects.get(item_movement_header_id=parentid)
                self.detailform = DetailForm(instance=detailinstance)
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
            context['tabletitle'] = 'Item Movements'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.get_grid('MOVEMENT')


        context['detailform_title'] = 'Details'
        context['detailform'] = self.detailform
        print('******* set context')
        return context
