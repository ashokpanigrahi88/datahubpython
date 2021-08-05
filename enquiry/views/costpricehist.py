from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindDateForm,FindItemForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (AuditItempriceHistory)
from common import (commonutil,sysutil)
from django import forms

#Create your form here


class ItemPriceHistForm(FindDateForm, FindItemForm):

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ItemPriceHistForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:costpricehistory'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ItemPriceHistoryView(ListView):
    model = AuditItempriceHistory
    template_name = 'enquiry/costpricehist.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(ItemPriceHistoryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ItemPriceHistoryView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'item_id__item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'),'exact')
        commonutil.filter_add(self.queryparams,'item_id__item_name',
                              commonutil.get_key_value(self.inputparams,'invoice_type'),'icontains')
        commonutil.filter_date_range(self.queryparams,'last_update_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        if not self.queryparams:
            return self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams).order_by('-last_update_date','item_id__item_number')
            commonutil.debugmessage(qs.query,'costpricehistory')
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
        self.form = ItemPriceHistForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['rows_tableheader'] ="""    
                                <th>Item Number</th>
                                <th>Changed On</th>
                                <th>Item Name</th>
                                <th>Old Price</th>
                                <th>Changed Price</th>
                                <th>Current Price</th>
                                <th>Reason</th>
                                <th>Category </th> """
            context['rows_tablecolumns'] = """   
                    <td>{{row.last_update_date|date:"SHORT_DATE_FORMAT"  }}</td>
                    <td>{{row.item_id.item_name }}</td>
                    <td>{{row.old_price }}</td>
                    <td>{{row.new_price }}</td>
                    <td>{{row.item_id.unit_cp }}</td>
                    <td>{{row.change_reason }}</td>
                    <td>{{row.change_category }}</td>"""
        print('******* set context')
        return context
