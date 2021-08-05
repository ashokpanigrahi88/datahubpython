from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from common.models  import (InvSubLocations)
from common import (commonutil,sysutil)
from django import forms
from enquiry import enquirygrids

#Create your form here

class FindForm(forms.Form):
    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs={'style': 'width:150px'},
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    sub_location = forms.CharField(max_length=30,label='Sub Location', required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    sub_location_group = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs={'style': 'width:150px'},
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,
                                                                         'SUB_LOCATION_GROUP_CODE')))
    sub_location_type = forms.CharField(max_length=30,required=False,initial="",
                                    widget=forms.Select(attrs={'style': 'width:150px'},
                                        choices=sysutil.populatelistitem(None,sysutil.CMN_LOOKUP_CODES_L,
                                                                         'SUB_LOCATION_TYPES')))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:iteminsubloc'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class SummaryView(ListView):
    model = InvSubLocations
    template_name = 'enquiry/sublocations.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    location,sublocation,sublocgroup,subloctype = ("",)*4
    print('******* start')
    initial =  {'location': ""}

    def get(self, request, *args, **kwargs):
        print('******* get')
        for key,value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial =  self.inputparams
        return super(SummaryViewView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print('******* poat')
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
        commonutil.filter_add(self.queryparams,'il_location_id__location_id',
                              commonutil.get_key_value(self.inputparams,'location_id'))
        commonutil.filter_add(self.queryparams,'sub_location',
                              commonutil.get_key_value(self.inputparams,'sub_location'),'icontains')
        commonutil.filter_add(self.queryparams,'sub_location_type',
                              commonutil.get_key_value(self.inputparams,'sub_location_type'),'icontains')
        commonutil.filter_add(self.queryparams,'sub_loc_group_code',
                              commonutil.get_key_value(self.inputparams,'sub_location_group'),'icontains')
        if not self.queryparams:
            print('empty querying', self.queryparams)
            return self.model.objects.none()
        else:
            print('querying', self.queryparams)
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('location_id', 'sub_location')
        self.object_list  = qs
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
        context['rows'] = self.object_list
        if self.object_list:
            context['tabletitle'] = 'Sub Locations'
            context['rowset_totals'] = None
            context['rows_tableheader'], context['rows_tablecolumns'], context[
                'rows_tablefooter'] = enquirygrids.get_grid('INVSUBLOCATIONS')
        print('******* set context')
        return context
