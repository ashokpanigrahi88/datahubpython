from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from enquiry.forms import FindCustomerForm, FindDateForm, ModelFieldsForm
from django.forms import ModelForm

from common.models  import (InvItemCountHeaders, InvItemCountLines)
from common import (commonutil,sysutil, dbfuncs)
from django import forms
from enquiry import enquirygrids
from enquiry.forms import FindStkTakeForm

#Create your form here
REP_STKTAKEAUDIT_V={
'fields':['location_name','sub_location_name','report_date','stktake_name','item_number','item_name','qty_instock',
          'qty_counted','diffqty','percentagediff','batch_name','comments','supplier_name',
          'category_name','sub_category_name','reason_name','reason_desc','stktake_type','created_by',
          'creation_date','daily','weekly','count_date','monthly','yearly','hourly','dailychar','weeklychar',
          'monthlychar','yearlychar','hourlychar','item_count_header_id','bu_id','location_id','item_id',
          'ctc_tax_code_id','supplier_id','item_count_line_id','sub_location_id','stktake_type_id',
          'reason_code_id','operatorname','averagevalue','lastboughtvalue','basevalue','unit_cp',
          'average_unitcp','last_bought_unitcp','count_status','stockable','valuable','minus_quantity',],
'headers':['Location','Sub Location','Approved On','Stock Take','Item Number','Item Name','Qty Instock',
           'Qty Counted','QtyDifference','%Difference','Batch Name','Comments','Supplier Name',
           'Category Name','Sub Category Name','Reason Name','Reason Desc','Stktake Type',
           'Created By','Creation Date','Daily','Weekly','Count Date','Monthly','Yearly','Hourly',
           'Dailychar','Weeklychar','Monthlychar','Yearlychar','Hourlychar','ID','Bu Id','Location Id',
           'Item Id','Tax Code Id','Supplier Id',' Line Id','Sub Location Id','Stktake Type Id',
           'Reason Code Id','OperatorName','Average Value',' Last Bought Value','Base Value','Unit CP',
           'Average Unit CP','Last BoughtUnit CP',' Status','STK','VAL','Minus Quantity'],
}


class DetailForm(ModelForm):

    class Meta:
        model = InvItemCountHeaders
        fields = '__all__'
        #exclude = ('customer_id',)


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindStkTakeForm):

    def __init__(self, hiddenfields:[]=[],  *args,**kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].required  = True
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 25
REVERSE = 'enquiry:stktakesum'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvItemCountHeaders
    template_name = 'enquiry/stktakesum.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    detailform = None
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
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'location_id',
                              commonutil.get_key_value(self.inputparams,'location'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'sub_location_name',
                              commonutil.get_key_value(self.inputparams,'sub_location'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),' like ')
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'count_status',
                              commonutil.get_key_value(self.inputparams,'stktake_status'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'stktake_type_id',
                              commonutil.get_key_value(self.inputparams,'stktake_type'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'item_count_header_id',
                              commonutil.get_key_value(self.inputparams,'item_count_header_id'))
        self.queryparams = commonutil.filter_add_raw(self.queryparams,'phase_code',
                              commonutil.get_key_value(self.inputparams,'phase_code'))
        self.queryparams =  commonutil.filter_date_range_raw(self.queryparams,'report_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        print('query params:',self.queryparams)
        if len(self.queryparams) < 10:
            return self.model.objects.none()
        else:
            sql = """Select location_name,sub_location_name,report_date,stktake_name,item_number,item_name,qty_instock,
                    qty_counted,diffqty,percentagediff,batch_name,comments,
                    supplier_name,category_name,sub_category_name,reason_name,
                    reason_desc,stktake_type,created_by,
                    creation_date,daily,weekly,count_date,monthly,yearly,hourly,dailychar,weeklychar,monthlychar,yearlychar,
                    hourlychar,item_count_header_id,bu_id,location_id,item_id,ctc_tax_code_id,
                    supplier_id,item_count_line_id,sub_location_id,stktake_type_id,reason_code_id,
                    operatorname,averagevalue,lastboughtvalue,basevalue,unit_cp,average_unitcp,
                    last_bought_unitcp,count_status,stockable,valuable,minus_quantity
                    From REP_STKTAKEAUDIT_V  {}  order by report_date desc """.format(self.queryparams)
            print(sql)
            qs  = dbfuncs.exec_sql(sql, 'dict', columnscase='lower')
        parentid =  commonutil.get_key_value(self.inputparams,'item_count_header_id')
        if commonutil.hasintvalue(parentid):
            detailinstance = InvItemCountHeaders.objects.get(item_count_header_id=parentid)
            self.detailform = DetailForm(instance=detailinstance)
        return qs

    def download_csv(self):
        csvdata = commonutil.download_csv(self.request, self.object_list)
        response = HttpResponse(csvdata, content_type='text/csv')
        return response

    def get_context_data(self, **kwargs):
        print('******* get context')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.form = FindForm(initial=commonutil.initalise_form(self.initial))
        # Add local context
        context['form'] = self.form
        context['detailform_title'] = 'Details'
        context['detailform'] = self.detailform
        if self.object_list:
            context['rows_tableheader'] ,context['rows_tablecolumns'], _ = enquirygrids.get_grid('STKTAKE')
        return context
