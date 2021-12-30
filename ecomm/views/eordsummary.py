from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.db.models import Avg, Max, Min, Sum
from ecomm.forms import FindOrderForm

from  datetime import datetime, date

from common.submodels.ecomm_models import *
from common import (commonutil,sysutil)
from django import forms
from django.forms import ModelForm
from ecomm import ecommgrids

#Create your form here

class DetailForm(ModelForm):

    class Meta:
        model = EcommOrderinfo
        fields = '__all__'
        exclude = ('order_id',)

    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['readonly'] = True

class FindForm(FindOrderForm):

    firstname = forms.CharField(max_length=30,label='First Name',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    lastname = forms.CharField(max_length=30,label='Last Name',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    email = forms.CharField(max_length=30,label='Email',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    phone = forms.CharField(max_length=30,label='Phone',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'ecomm/eordsummary'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class EcomOrdSummaryView(ListView):
    model = EcommOrderinfo
    template_name = 'ecomm/eordsummary.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    queryparams = {}
    emptysearch = True
    ordlines = None
    pmntlines = None
    totals = {}
    rowset2_totals ={}
    inputparams = {}
    child1 = child2 = child3 = child4 = None
    rowset_totals = rowset2_totals = rowset3_totals = rowset4_totals  =  {}
    parentid = None

    def get(self, request, *args, **kwargs):
        self.inputparams = {}
        for key, value in self.request.GET.items():
            if key != 'csrfmiddlewaretoken':
                self.inputparams[key] = value
        print('params', self.inputparams)
        self.initial = self.inputparams
        return super(EcomOrdSummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(EcomOrdSummaryView, self).get_form_kwargs()
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
        self.detailform = None
        commonutil.filter_add(self.queryparams,'orderno',
                              commonutil.get_key_value(self.inputparams,'orderno'),'exact')
        commonutil.filter_add(self.queryparams,'orderid',
                              commonutil.get_key_value(self.inputparams,'orderid'),'exact')
        commonutil.filter_date_range(self.queryparams,'orderdate',
                                     commonutil.get_key_value(self.inputparams,'date_from'),
                                     commonutil.get_key_value(self.inputparams,'date_to') ,'str')
        if not self.queryparams and commonutil.iskeyempty(self.inputparams,'search'):
            return self.model.objects.none()
        else:
            qs = queryset.filter(**self.queryparams)
            qs = qs.order_by('-orderdate','orderno')
            self.totals = qs.aggregate(net_total=Sum('nettotalamount'),
                       vat_total=Sum('taxamount'),
                       gross_total=Sum('grosstotalamount'))
            qs = qs.order_by('orderno')
            if len(qs) == 1:
                detailinstance  = qs[0]
                self.parentid = detailinstance.orderid
                self.detailform = DetailForm(instance=detailinstance)
                self.child1 = EcommOrderdetailsinfo.objects.filter(orderid__orderid=self.parentid).order_by('serialno')
                if self.child1:
                    self.rowset2_totals = self.child1.aggregate(net_total=Sum('productsubtotal'),
                            vat_total=Sum('producttaxamount'))
                self.child2 = EcommOrderpaymentinfo.objects.filter(orderid__orderid=self.parentid)
                """ 
                if self.child2:
                    self.rowset3_totals = self.child2.aggregate(net_total=Sum('net_total'),
                                               vat_total=Sum('vat_total'),
                                               gross_total=Sum('gross_total'),
                                               weight_total=Sum('weight_total'),
                                               volume_total=Sum('volume_total'),
                                               ingredient_total=Sum('ingredient_total')
                                               )
                """
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
            context['rows_tableheader'], context['rows_tablecolumns'], context['rows_tablefooter'],  = ecommgrids.ecommord_grid()
        if self.child1:
            context['tabletitle2'] = """Order Lines (<a href={% url 'ecomm:eordsummary' %}?orderid=""" + str(
                self.parentid) + """>All </a>)"""
            context['rowset2'] = self.child1
            context['rowset2_totals'] = self.rowset2_totals
            context['parentid'] = self.parentid
            context['rowset2_tableheader'], context['rowset2_tablecolumns'], context[
                'rowset2_totals'] =  ecommgrids.ecommordline_grid('row2.', 'rowset2_totals.')
        """
        if self.child2:
            context['tabletitle3'] = "Payment Details (<a href={% url 'ecomm:eordsummary' %}?orderid=" + str(
                self.parentid) + ">All </a>)"
            context['rowset3'] = self.child2
            context['rowset3_totals'] = self.rowset3_totals
            context['rowset3_tableheader'], context['rowset3_tablecolumns'], context[
                'rowset3_totals'] = enquirygrids.grn_grid('row3.', 'rowset3_totals.')
        """
        context['detailform'] = self.detailform
        context['detailform_title'] = 'Details'
        print('******* set context')
        return context
