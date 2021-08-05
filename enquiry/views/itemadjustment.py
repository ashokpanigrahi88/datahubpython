from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from enquiry.forms import IteminLocationForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm

from common.models  import (InvItemAdjustmentHeaders, InvItemAdjustmentLines)
from common import (commonutil,sysutil, dbfuncs)
from django import forms
from enquiry import enquirygrids

#Create your form here
INV_ITEM_ADJUSTMENTS_VAL={
'fields':['location_name','sub_location_name','report_date','batch_name','item_number','item_name','qty_adjusted',
          'reason_desc','supplier_name','category_name','sub_category_name','created_by','creation_date','daily',
          'weekly','monthly','yearly','hourly','dailychar','weeklychar','monthlychar','yearlychar','hourlychar',
          'bu_id','location_id','item_id','supplier_id','sub_location_id','category_id','sub_category_id',
          'adjust_header_id','adjust_line_id','operatorname',],
'headers':['Location','Sub Location','Updated On','Group Code','Item Number','Item Name',
           'Adjusted','Reason','Supplier Name','Category Name','Sub Category Name','Created By','Creation Date',
           'Daily','Weekly','Monthly','Yearly','Hourly','Dailychar','Weeklychar','Monthlychar','Yearlychar','Hourlychar',
           'Bu Id','Location Id','Item Id','Supplier Id','Sub Location Id',
           'Category Id','Sub Category Id',' Header Id',' Line Id','OperatorName',],
            }



class DetailForm(ModelForm):

    class Meta:
        model = InvItemAdjustmentHeaders
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(IteminLocationForm,FindDateForm):

    adjusted_by = forms.CharField(max_length=30,label='Adjusted By', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = True
        self.fields['location'].required  = True
        self.fields['sub_location_type'].widget  =  forms.HiddenInput()
        self.fields['sub_location_type'].label  =  ""
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:itemadjustment'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummmaryView(ListView):
    model = InvItemAdjustmentHeaders
    template_name = 'enquiry/itemadjustment.html'
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
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'operatorname',
                              commonutil.get_key_value(self.inputparams,'adjusted_by'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'location_id',
                              commonutil.get_key_value(self.inputparams,'location_id'))
        self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'report_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """ Select location_name,sub_location_name,report_date,batch_name,item_number,item_name,
                    qty_adjusted,reason_desc,supplier_name,category_name,sub_category_name,created_by,
                    creation_date,daily,weekly,monthly,yearly,hourly,dailychar,weeklychar,monthlychar,yearlychar,
                    hourlychar,bu_id,location_id,item_id,supplier_id,sub_location_id,category_id,
                    sub_category_id,adjust_header_id,adjust_line_id,operatorname
                    From inv_item_adjustments_val  {}  order by report_date desc """.format(self.queryparams)
            qs  = dbfuncs.exec_sql(sql, 'dict', columnscase='lower')
        self.object_list = qs
        if qs:
            adjustid = qs[0]['adjust_header_id']
            #self.child1 = InvItemAdjustmentLines.objects.filter(iiah_adjust_header_id__adjust_header_id=adjustid)
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
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.get_grid('ITEMADJUST')

        if self.child1:
            context['tabletitle2'] = 'Adjustment Lines'
            context['rowset2'] = self.child1
            context['rowset2_totals'] = None
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                           'rowset2_tablefooter'] = enquirygrids.get_grid('ITEMADJUST', 'row2.', 'rowset2_totals.')
        return context
