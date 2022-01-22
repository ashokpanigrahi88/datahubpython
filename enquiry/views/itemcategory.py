from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum, Count
from enquiry.forms import FindCategoryForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (InvItemCategories, InvItemSubCategories)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class DetailForm(ModelForm):

    class Meta:
        model = InvItemCategories
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindCategoryForm):

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(InvItemSubCategories)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 20
REVERSE = 'enquiry:itemcategory'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvItemSubCategories
    template_name = 'enquiry/itemcategory.html'
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
        self.inputparams = {}
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken' :
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
        kwargs.update['hiddenfields'] = ['category_id','sub_category_id']
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
        commonutil.filter_add(self.queryparams,'iic_category_id__category_id',
                              commonutil.get_key_value(self.inputparams,'category_id'),)
        commonutil.filter_add(self.queryparams,'sub_category_id',
                              commonutil.get_key_value(self.inputparams,'sub_category_id'),)
        commonutil.filter_add(self.queryparams,'iic_category_id__category_name',
                              commonutil.get_key_value(self.inputparams,'category_name'),'istartswith')
        commonutil.filter_add(self.queryparams,'sub_category_name',
                              commonutil.get_key_value(self.inputparams,'sub_category_name'),'istartswith')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        print( self.queryparams)
        if False or not self.queryparams :
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('iic_category_id__category_name','sub_category_name')
            self.totals = None
            if len(qs) == 1:
                detailinstance = qs[0]
                parentid = detailinstance.iic_category_id.category_id
                category =  InvItemCategories.objects.get(category_id=parentid)
                self.detailform = DetailForm(instance=category)
                self.child1 = InvItemSubCategories.objects.filter(iic_category_id__category_id=parentid).order_by(
                'sub_category_name' )
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
        self.form = commonutil.initalise_find_form(FindForm,self.initial)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Categories'
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.get_grid('SUBCAT')

        if  self.child1:
            context['tabletitle2'] = 'Sub Categories'
            context['rowset2'] = self.child1
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                           'rowset2_tablefooter'] = enquirygrids.get_grid('SUBCAT', 'row2.', 'rowset2_totals.')

        context['detailform_title'] = 'Category'
        context['detailform'] = self.detailform
        print('******* set context')
        return context
