from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from common.models  import (InvItemMasters, InvItemLocations, InvItemLocations)
from common import (commonutil,sysutil)
from django import forms

#Create your form here

class IteminLocationForm(forms.Form):
    location = forms.CharField(max_length=30,required=False,initial="",label="Location",
                                    widget=forms.Select(attrs={'style': 'width:150px'},
                                        choices=sysutil.populatelistitem(None,sysutil.INV_LOCATIONS_L)))
    item_number = forms.CharField(max_length=30,label='Item Number',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:100px'},))
    item_name = forms.CharField(max_length=30,label='Item Name ',required=False,
                                   widget=forms.TextInput(attrs={'style': 'width:300px'},))
    category = forms.CharField(max_length=30,required=False,initial="",label="Category",
                                    widget=forms.Select(attrs={'style': 'width:150px'},
                                        choices=sysutil.populatelistitem(None,sysutil.INV_ITEM_CATEGORIES_l)))
    qty_filter = forms.CharField(max_length=10,label='Qty Filter',required=False,initial='> 0',
                                    widget=forms.Select(attrs={'style': 'width:100px'},
                                        choices=sysutil.populatelistitem('QTY_FILTER',None)))

    def __init__(self, hiddenfields:[]=[],  *args, **kwargs):
        super(IteminLocationForm, self).__init__(*args, **kwargs)
        self.fields['item_number'].widget.attrs.update({'autofocus': 'autofocus',
                                                 "value":""})
        if len(hiddenfields) > 0:
            for hf in hiddenfields:
                self.fields[hf].widget = forms.HiddenInput()

# Create your views here.


PAGE_VAR = 14
REVERSE = 'enquiry:iteminloc'

# Create your views here.


@method_decorator(login_required, name='dispatch')
class IteminLocationView(ListView):
    model = InvItemLocations
    template_name = 'enquiry/iteminloc.html'
    paginate_by = PAGE_VAR
    context_object_name = 'rows'
    location,sublocation,itemnumber,sublocgroup,subloctype,qtyfilter = ("",)*6
    print('******* start')
    initial =  {'location': ""}

    def get(self, request, *args, **kwargs):
        print('******* get')
        self.location =  self.request.GET.get('location')
        self.qtyfilter  =  self.request.GET.get('qty_filter')
        self.itemnumber  =  self.request.GET.get('item_number')
        self.category  =  self.request.GET.get('category')
        self.itemname  =  self.request.GET.get('item_name')
        if not commonutil.hasstrvalue(self.qtyfilter):
            self.qtyfilter = '> 0'
        self.initial =  {'location': self.location,
                    'item_number':self.itemnumber,
                    'item_name':  self.itemname,
                    'category':  self.category,
                    'qty_filter': self.qtyfilter
                         }
        return super(IteminLocationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.form_invalid(self.form, **kwargs)

    def get_initial(self):
        print('inital:', self.initial)
        return self.initial

    def get_form_kwargs(self):
        print('******* fprm kwargs')
        kwargs = super(IteminLocationView, self).get_form_kwargs()
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
        if commonutil.hasstrvalue(self.location):
            queryset = queryset.filter(location_id=int(self.location))
        if commonutil.hasstrvalue(self.itemname):
            queryset = queryset.filter(item_id__item_name__icontains=self.itemname)
        if commonutil.hasstrvalue(self.itemnumber):
            queryset = queryset.filter(item_id__item_number=self.itemnumber)
        if commonutil.hasstrvalue(self.category):
            queryset = queryset.filter(item_id__iic_category_id__category_id=self.category)
        if not commonutil.hasstrvalue(self.qtyfilter):
            return self.model.objects.none()
        if commonutil.hasstrvalue(self.qtyfilter):
            qtyfilterstring = 'quantity{0}'.format(
                    self.qtyfilter.replace('> 0','__gt').replace('< 0', '__lt').replace('= 0', ''))
            print(qtyfilterstring)
            queryset = queryset.filter(**{qtyfilterstring:0})
        qs = queryset.order_by('item_id__item_number')
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
        self.form = IteminLocationForm(initial=self.initial)
        context['form'] = self.form
        print('******* set context')
        return context
