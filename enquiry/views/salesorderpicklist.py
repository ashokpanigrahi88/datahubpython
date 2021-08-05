from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from enquiry.forms import FindSalesOrderForm, FindItemForm
from django.forms import ModelForm
from  datetime import datetime, date

from common.models  import (ArSalesorderHeaders, ArSalesorderLines, ArSalesorderPicklist)
from common import (commonutil,sysutil)
from django import forms

#Create your form here

class PicklistForm(ModelForm):

    class Meta:
        model = ArSalesorderPicklist
        fields = '__all__'
        #exclude = ('customer_id','sub_location_id','shipfrom_location_id','invoice_header_id','payto_location_id')


    def __init__(self, *args, **kwargs):
        super(PicklistForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class ArOrderPickForm(FindSalesOrderForm, FindItemForm):

    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium'],
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    sub_location = forms.CharField(max_length=30,label='Sub Location', required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['medium']))

    line_status = forms.CharField(max_length=30,label='Line Status',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small'],
                                                        ))

    phase_code = forms.CharField(max_length=30,label='Phase Code',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['small'],
                                                        ))

    available_fields = forms.CharField(max_length=30,required=False,initial="",label='Available Fields',
                                    widget=forms.Select(attrs=sysutil.DISPLAY_FIELD_WIDTH['large'],
                                        choices=commonutil.choice_modelcharfields(ArSalesorderPicklist)))

    field_contains = forms.CharField(max_length=30,label='Field Contanis',required=False,
                                   widget=forms.TextInput(attrs=sysutil.DISPLAY_FIELD_WIDTH['large']))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(ArOrderPickForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:salesorderpicklist'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class ArOrderPickView(ListView):
    model = ArSalesorderPicklist
    template_name = 'enquiry/salesorderpicklist.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    getvars = {}
    inputparams = {}
    queryparams = {}
    linequery = {}
    emptysearch = True
    invlines = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}

    def get(self, request, *args, **kwargs):
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        self.initial =  self.inputparams
        return super(ArOrderPickView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(ArOrderPickView, self).get_form_kwargs()
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
        commonutil.filter_add(self.queryparams,'location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'location'),'')
        commonutil.filter_add(self.queryparams,'sub_location_id__sub_location',
                              commonutil.get_key_value(self.inputparams,'sub_location'),'exact')
        commonutil.filter_add(self.queryparams,'order_header_id__order_number',
                              commonutil.get_key_value(self.inputparams,'order_number'),'exact')
        commonutil.filter_add(self.queryparams,'order_header_id__order_type',
                              commonutil.get_key_value(self.inputparams,'order_type'),'exact')
        commonutil.filter_add(self.queryparams,'order_header_id__batch_name',
                              commonutil.get_key_value(self.inputparams,'batch_name'),'startswith')
        commonutil.filter_add(self.queryparams,'order_header_id__order_status',
                              commonutil.get_key_value(self.inputparams,'order_status'),'exact')
        commonutil.filter_add(self.queryparams,'order_line_status',
                              commonutil.get_key_value(self.inputparams,'line_status'),'icontains')
        commonutil.filter_add(self.queryparams,'order_header_id__phase_code',
                              commonutil.get_key_value(self.inputparams,'phase_code'),'icontains')
        commonutil.filter_add(self.queryparams,'picklist_id',
                              commonutil.get_key_value(self.inputparams,'picklist_id'),'')
        commonutil.filter_date_range(self.queryparams,'picklist_status_date',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        commonutil.filter_add(self.queryparams,'item_id__item_number',
                              commonutil.get_key_value(self.inputparams,'item_number'),'exact')
        commonutil.filter_add(self.queryparams,'item_name',
                              commonutil.get_key_value(self.inputparams,'item_name'),'icontains')
        commonutil.filter_add(self.queryparams,commonutil.get_key_value(self.inputparams,'available_fields'),
                              commonutil.get_key_value(self.inputparams,'field_contains'),'icontains')
        if not self.queryparams:
            qs =  self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            print(qs.query)
            customerfilter = commonutil.get_key_value(self.inputparams,'customer')
            if commonutil.hasstrvalue(customerfilter):
                qs = qs.filter(Q(order_header_id__customer_id__customer_number=customerfilter ) |
                    Q(order_header_id__customer_id__customer_name__icontains=customerfilter))

            print(qs.query)
            qs = qs.order_by('-picklist_status_date')
            if len(qs) == 1:
                detailinstance  = qs[0]
                parentid = detailinstance.picklist_id
                self.detailform = PicklistForm(instance=detailinstance)
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
        self.form = ArOrderPickForm(initial=self.initial)
        context['form'] = self.form
        if self.object_list:
            context['tabletitle'] = 'Order Lines'
            context['rowset_totals'] = self.totals
            context['rows_tableheader'] =""" 
                                            <th> ID </th>
                                            <th> Order Number </th>
                                            <th> Order Line </th>
                                            <th> Status Date </th> 
                                            <th> Item Number </th> 
                                            <th> Item Name </th> 
                                            <th> From Location </th> 
                                            <th> From Sub Location </th> 
                                            <th> Quantity </th> 
                                            <th> Status </th> 
                                            """
            context['rows_tablecolumns'] = """                      
            <td>  <a href={% url 'enquiry:salesorderpicklist' %}?picklist_id={{row.picklist_id }}>{{row.picklist_id }}</a> </td>           
                    <td>  <a href={% url 'enquiry:salesordersum' %}?order_header_id={{row.order_header_id.order_header_id }}>{{row.order_header_id.order_number }}</a> </td>
                    <td>  <a href={% url 'enquiry:salesorderlines' %}?order_line_id={{row.order_line_id.order_line_id }}>{{row.order_line_id.order_line_id }}</a> </td>
              <td> {{ row.picklist_status_date|date:"SHORT_DATE_FORMAT"   }}
            </td> <td> {{ row.item_id.item_number }} </td>
            <td> {{ row.item_id.item_name }} </td><td> {{ row.location_id.location_name }} </td>
            <td> {{ row.sub_location_id.sub_location }} </td><td> {{ row.quantity}} </td>
            <td> {{ row.picklist_status }} </td></td>"""

        context['detailform'] = self.detailform
        context['detailform_title'] = 'Pick List  Details'
        print('******* set context')
        return context
