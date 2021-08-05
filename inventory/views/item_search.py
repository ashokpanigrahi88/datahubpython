from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum, Count
from enquiry.forms import ItemSearchForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (InvItemMasters,InvItemSalesUnits, InvItemPrices, InvItemBarcodes)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class DetailForm(ModelForm):

    class Meta:
        model = InvItemMasters
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(ItemSearchForm):

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 20
REVERSE = 'inventory:itemsearch'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvItemMasters
    template_name = 'inventory/item_search.html'
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
        forcequery = False
        print('******* get queryset')
        queryset = super().get_queryset()
        self.queryparams = {}
        self.detailform  = None
        if commonutil.hasstrvalue(commonutil.get_key_value(self.inputparams, 'item_id')):
            print('query',self.queryparams)
            commonutil.filter_add(self.queryparams, 'item_id',
                                  commonutil.get_key_value(self.inputparams, 'item_id'),'','int')
            print('query',self.queryparams)
        else:
            commonutil.filter_add(self.queryparams,'item_number',
                                  commonutil.get_key_value(self.inputparams,'item_number'),'exact')
            commonutil.filter_add(self.queryparams,'item_name',
                                  commonutil.get_key_value(self.inputparams,'item_name'),'icontains')
            commonutil.filter_add(self.queryparams,'iic_category_id__category_id',
                                  commonutil.get_key_value(self.inputparams,'category'))
            commonutil.filter_add(self.queryparams,'iisc_sub_category_id__sub_category_id',
                                  commonutil.get_key_value(self.inputparams,'sub_category'))
            commonutil.filter_add(self.queryparams,'sup_supplier_id__supplier_id',
                                  commonutil.get_key_value(self.inputparams,'supplier'))
            commonutil.filter_add(self.queryparams,'iim_manf_id__manf_id',
                                  commonutil.get_key_value(self.inputparams,'manufacturer'))
            commonutil.filter_add(self.queryparams,'season_code_id',
                                  commonutil.get_key_value(self.inputparams,'season'))
            commonutil.filter_add(self.queryparams,'ctc_tax_code_id',
                                  commonutil.get_key_value(self.inputparams,'tax_code'))
            commonutil.filter_add(self.queryparams,'item_status',
                                  commonutil.get_key_value(self.inputparams,'item_status'))
            commonutil.filter_add(self.queryparams,'image_hint',
                                  commonutil.get_key_value(self.inputparams,'image_hint'))
            commonutil.filter_add(self.queryparams,'item_condition',
                                  commonutil.get_key_value(self.inputparams,'item_condition'))
            commonutil.filter_add(self.queryparams,'instrunctiont',
                                  commonutil.get_key_value(self.inputparams,'instruction'),'icontains')
            if commonutil.hasstrvalue(commonutil.get_key_value(self.inputparams, 'advanced')):
                queryset = queryset.extra(where=[commonutil.get_key_value(self.inputparams, 'advanced')])
                forcequery = True
            if commonutil.hasstrvalue(commonutil.get_key_value(self.inputparams, 'user_query')):
                queryset = queryset.extra(where=[commonutil.get_key_value(self.inputparams, 'user_query')])
                print(queryset.query)
                forcequery = True

        if not forcequery and  not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('item_number')
            self.totals = None
            parentid = commonutil.get_key_value(self.inputparams,'item_id')
            if len(qs) == 1:
                parentid =  qs[0].item_id
            if commonutil.hasintvalue(parentid):
                detailinstance = InvItemMasters.objects.get(item_id=parentid)
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
        self.initial['item_id'] = ""
        self.form = FindForm()
        context['form'] = self.form
        if self.object_list:
            context['rows'] =  self.object_list
            context['tabletitle'] = 'Items'
            context['rowset_totals'] = None
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.itemsearch_grid()


        context['detailform_title'] = 'Details'
        context['detailform'] = self.detailform
        print('******* set context')
        return context
