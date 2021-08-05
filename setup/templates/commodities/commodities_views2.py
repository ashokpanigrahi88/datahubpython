from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django import forms

# Custom Imports
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list

# View specific imports
from common.moduleattributes.table_fields import CMN_COMMODITY_CODES, CMN_COMMODITY_RATES
from common.models import CmnCommodityCodes, CmnCommodityRates

MODEL = CmnCommodityCodes
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = CMN_COMMODITY_CODES

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                   x[0] in form_field_list}

### From XML
# ccc_field_list = ('commodity_code',
#                   'name',
#                   'section',
#                   'chapter',
#                   'heading',
#                   'active',
#                   'legal_act',
#                   'exclusions',
#                   'conditions',
#                   'measure_type',
#                   'additional_codes',
#                   'attribute1',
#                   'attribute2',
#                   'attribute3',
#                   'attribute4',
#                   'attribute5',
#                   'attribute6',
#                   'start_date_active',
#                   'end_date_active',
#                   'footnote',
#                   'description')


class CommodityCodesForm(forms.ModelForm):

    class Meta:
        model = CmnCommodityCodes
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(CommodityCodesForm, self).__init__(*args, **kwargs)
        self.fields['active'].initial = 'Y'
        for field in CmnCommodityCodes._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityCodes._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # try:
                    #     self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # except:
                    #     print('CommodityCodesForm: Couldnt save:', self.cleaned_data[field.name],'/nField:',field)
        return self.cleaned_data


# ccr_field_list = ('ccc_id',
#                   'country_code',
#                   'duty_rate',
#                   'start_date_active',
#                   'end_date_active',
#                   'description',
#                   'attribute1',
#                   'attribute2',
#                   'attribute3',
#                   'attribute4',
#                   'attribute5',
#                   'attribute6',)

ccr_non_editable_list = [field.name for field in CmnCommodityRates._meta.fields if not field.editable]

ccr_exclude_list = general_exclude_list + ccr_non_editable_list

ccr_form_field_list = [field for field in CMN_COMMODITY_RATES['fields'] if field not in ccr_exclude_list]

ccr_form_field_dict = {x[0]: x[1] for x in list(zip(CMN_COMMODITY_RATES['fields'], CMN_COMMODITY_RATES['headers'])) if
                   x[0] in ccr_form_field_list}

class CommodityRatesForm(forms.ModelForm):
    # start_date_active = forms.DateField(
    #     widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)
    # end_date_active = forms.DateField(
    #     widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = CmnCommodityRates
        fields = ccr_form_field_list
        labels = ccr_form_field_dict

    def __init__(self, *args, **kwargs):
        super(CommodityRatesForm, self).__init__(*args, **kwargs)

        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


cc_search_field_list = ['name','section','chapter',]
class CCSearchForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = cc_search_field_list
        labels = form_field_dict
        widgets = {x: forms.TextInput(attrs={'required': False, }) for x in cc_search_field_list}

    def __init__(self, *args, **kwargs):
        super(CCSearchForm, self).__init__(*args, **kwargs)
        for field in cc_search_field_list:
            self.fields[field].required = False


class CCDetailForm(forms.ModelForm):
    class Meta:
        model = CmnCommodityCodes
        fields = form_field_list
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in CmnCommodityCodes._meta.fields}


class CRDetailForm(forms.ModelForm):
    class Meta:
        model = CmnCommodityRates
        fields = ccr_form_field_list
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in CmnCommodityRates._meta.fields}
        
        
# cr_search_field_list = ['name', 'country', ]
# class CRSearchForm(forms.ModelForm):
#     class Meta:
#         model = CmnCommodityRates
#         fields = cr_search_field_list
#         labels = ccr_form_field_dict
#         widgets = {x: forms.TextInput(attrs={'required': False, }) for x in cr_search_field_list}
#
#     def __init__(self, *args, **kwargs):
#         super(CRSearchForm, self).__init__(*args, **kwargs)
#         for field in cr_search_field_list:
#             self.fields[field].required = False

APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/commoditycodes{0}/'
SLUG_FIELD = 'ccc_id'
SLUG_URL_KWARG = 'ccc_id'
TEMPLATE_PREFIX = 'commodities/cmncommoditycodes-{0}.html'
ORDERING = ('-ccc_id',)
FORM_CLASS = CommodityCodesForm
MODEL = CmnCommodityCodes
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:commoditycodes_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Commodity Codes',
             'findfield': 'Commodity Code/Name',
             }

### From XML
tab_fields = {'OTHERS': ['start_date_active', 'end_date_active', 'footnote', 'description'],
              'GENERAL': ['commodity_code',
                          'name',
                          'section',
                          'chapter',
                          'heading',
                          'active'],
              'INFO': ['legal_act',
                       'exclusions',
                       'conditions',
                       'measure_type',
                       'additional_codes'],
              'ATTRIBUTES': ['attribute1', 'attribute2', 'attribute3',
                             'attribute4', 'attribute5', 'attribute6'], }

ccc_listview_filed_list = ['commodity_code', 'name', 'section', 'chapter',
                           'heading', 'active']

ccc_listview_filed_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                           all([x[0] in form_field_list, x[0] not in ['attribute1', 'attribute2', 'attribute3',
                                                                      'attribute4', 'attribute5', 'attribute6']])}

ccr_listview_filed_list = ['commodity_code', 'name', 'section', 'chapter',
                       'heading', 'active']

ccr_listview_filed_dict = {x[0]: x[1] for x in list(zip(CMN_COMMODITY_RATES['fields'], CMN_COMMODITY_RATES['headers'])) if
                       all([x[0] in ccr_form_field_list, x[0] not in ['attribute1', 'attribute2', 'attribute3',
                                                                      'attribute4', 'attribute5', 'attribute6']])}

@method_decorator(login_required, name='dispatch')
class CommodityCodesListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(CommodityCodesListView, self).get_context_data(**kwargs)

        ### Commodity Codes
        comm_codes = self.get_queryset()
        context['comm_codes'] = comm_codes
        context['cc_search_form'] = CCSearchForm()
        context['ccc_listview_filed_dict'] = ccc_listview_filed_dict
        context['ccr_listview_filed_dict'] = ccr_listview_filed_dict

        if 'cc_filter' in self.request.GET:
            comm_codes = formfilter_queryset(self.request.GET, comm_codes, cc_search_field_list)
            context['cc_search_form'] = CCSearchForm(self.request.GET)
            context['comm_codes'] = comm_codes

        if len(comm_codes) == 1:
            context['commcode'] = comm_codes[0]
            context['cc_details'] = CCDetailForm(instance=comm_codes[0])
            cr_list = CmnCommodityRates.objects.filter(ccc_id=comm_codes[0].ccc_id)
            context['comm_rates'] = cr_list
            if len(cr_list) == 1:
                context['commrate'] = cr_list[0]
                context['cr_details'] = CRDetailForm(instance=cr_list[0])

        elif self.request.GET.get('commoditycode'):
            print('commoditycode -->', self.request.GET.get('commoditycode'))
            comm_codes = CmnCommodityCodes.objects.filter(commodity_code=self.request.GET.get('commoditycode'))
            context['comm_codes'] = comm_codes
            context['commcode'] = comm_codes[0]
            context['cc_details'] = CCDetailForm(instance=comm_codes[0])
            cr_list = CmnCommodityRates.objects.filter(ccc_id=comm_codes[0])
            context['comm_rates'] = cr_list
            if len(cr_list) == 1:
                context['commrate'] = cr_list[0]
                context['cr_details'] = CRDetailForm(instance=cr_list[0])

        if len(comm_codes) > REC_IN_PAGE:
            ccpage = self.request.GET.get('CCpage')
            cc_paginator = Paginator(comm_codes, self.paginate_by)
            try:
                cc_rows = cc_paginator.get_page(ccpage)
            except PageNotAnInteger:
                cc_rows = cc_paginator.get_page(1)
            except EmptyPage:
                cc_rows = cc_paginator.get_page(cc_paginator.num_pages)
            context['comm_codes'] = cc_rows

        context['MYCONTEXT'] = MYCONTEXT
        # print(' --------------- CONTEXT ---------------')
        # for k,v in context.items():
        #     if k in ['comm_codes',]:
        #         print(k,'--->',v)
        # print(' --------------- End of CONTEXT ---------------')
        return context


@method_decorator(login_required, name='dispatch')
class CommodityCodesCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def get_context_data(self, **kwargs):
        context = super(CommodityCodesCreateView, self).get_context_data(**kwargs)
        context['general_field_list'] = tab_fields['GENERAL']
        context['info_field_list'] = tab_fields['INFO']
        context['attributes_field_list'] = tab_fields['ATTRIBUTES']
        context['others_field_list'] = tab_fields['OTHERS']
        context['field_counts'] = {x: len(tab_fields[x]) for x in tab_fields.keys()}
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.ccc_id = get_sequenceval('cmn_commodity_codes_s.nextval')
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class CommodityCodesUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class CommodityCodesDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('d')

    def get_success_url(self):
        return reverse(REVERSE)


###########################################################
#### COMMODITY RATES VIEWS ################################
@method_decorator(login_required, name='dispatch')
class CommodityRatesCreateView(CreateView):
    model = CmnCommodityRates
    form_class = CommodityRatesForm
    template_name = 'commodities/cmncommodityrates-c.html'

    def get_context_data(self, **kwargs):
        context = super(CommodityRatesCreateView, self).get_context_data(**kwargs)
        if self.request.GET.get('commoditycode'):
            commcode = CmnCommodityCodes.objects.get(commodity_code=self.request.GET.get('commoditycode'))
            initial_values = {'ccc_id': commcode}
            context['form'] = CommodityRatesForm(initial=initial_values)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.ccr_id = get_sequenceval('cmn_commodity_rates_s.nextval')
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class CommodityRatesUpdateView(UpdateView):
    model = CmnCommodityRates
    slug_field = 'ccr_id'
    slug_url_kwarg = 'ccr_id'
    form_class = CommodityRatesForm
    template_name = 'commodities/cmncommodityrates-u.html'
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class CommodityRatesDeleteView(DeleteView):
    model = CmnCommodityRates
    slug_field = 'ccr_id'
    slug_url_kwarg = 'ccr_id'
    template_name = 'commodities/cmncommodityrates-d.html'

    def get_success_url(self):
        return reverse(REVERSE)