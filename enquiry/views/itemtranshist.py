from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from enquiry.forms import IteminLocationForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm

from common.models  import (InvItemMasters , InvItemSubLocations)
from common import (commonutil,sysutil, dbfuncs)
from django import forms
from enquiry import enquirygrids

#Create your form here
INV_ITEM_TRANS_HISTORY_V={
'fields':['trans_seq','item_id','bu_id','location_id','sub_location_id','source_header_id',
          'source_line_id','item_name','item_number','trans_source','report_date','location_name',
          'sub_location_name','resetqty','credit_quantity','debit_quantity',
          'source_type','source_info1','source_info2',],
'headers':['Trans Seq','Item Id','Bu Id','Location Id','Sub Location Id','Source Header Id','Source Line Id',
           'Item Name','Item Number','Trans Source','Report Date','Location Name','Sub Location ',
           'ResetQuantity','Credit Quantity','Debit Quantity','Source Type','Source Info1','Source Info2',],
}


class DetailForm(ModelForm):

    class Meta:
        model = InvItemMasters
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(IteminLocationForm,FindDateForm):
    trans_seq = forms.CharField(max_length=30,label='Trans Seq',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small']))

    source_info1 = forms.CharField(max_length=30,label='Info1',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small']))


    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = True
        self.fields['location'].required  = True
        self.fields['item_number'].required  = True
        self.fields['sub_location_type'].widget  =  forms.HiddenInput()
        self.fields['sub_location_type'].label  =  ""
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:itemtranshist'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummmaryView(ListView):
    model = InvItemMasters
    template_name = 'enquiry/itemtranshist.html'
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
        return super(SummmaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(SummmaryView, self).get_form_kwargs()
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
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'trans_seq',
                              commonutil.get_key_value(self.inputparams,'trans_seq'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'source_info1',
                              commonutil.get_key_value(self.inputparams,'source_info1'),)
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'sub_location',
                              commonutil.get_key_value(self.inputparams,'sub_location'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'sub_location_id',
                              commonutil.get_key_value(self.inputparams,'sub_location_idr'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'location_id',
                              commonutil.get_key_value(self.inputparams,'location'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'location_id',
                              commonutil.get_key_value(self.inputparams,'location_id'))
        self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'report_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """ Select trans_seq,item_id,bu_id,location_id,sub_location_id,source_header_id,
          source_line_id,item_name,item_number, initcap(trans_source) trans_source ,report_date,location_name,
          decode(credit_quantity,null,'-',sub_location_name) to_sub_location ,
          decode(debit_quantity,null,'-',sub_location_name) from_sub_location ,
          nvl(resetqty,0) resetqty ,credit_quantity credit_quantity,
          debit_quantity debit_quantity,
          source_type,source_info1,source_info2
                    From INV_ITEM_TRANS_HISTORY_V  {}  order by report_date,source_header_id desc """.format(self.queryparams)
            qs  = dbfuncs.exec_sql(sql, 'dict', columnscase='lower')
        self.object_list = qs
        if qs:
            itemid = qs[0]['item_id']
            self.child1 = InvItemSubLocations.objects.filter(item_id__item_id=itemid).filter(quantity__gte=0.0).order_by('location_id','sub_location_id')
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
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.get_grid('ITEMTRANSHIST')

        if self.child1:
            context['tabletitle2'] = 'Item in Sub Locations'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = None
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                           'rowset2_tablefooter'] = enquirygrids.get_grid('ITEMINSUBLOC', 'row2.', 'rowset2_totals.')
        return context
