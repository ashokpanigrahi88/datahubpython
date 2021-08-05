from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# specific to this view
from common.sysutil import get_sequenceval
from common.table_gen import get_table_html
# from setup.templates.commodities.commodities_forms import *
# from common.models import CmnCommodityCodes,CmnCommodityRates

from django import forms
from django.conf import settings
from common.models import CmnCommodityCodes, CmnCommodityRates

### From XML
ccc_field_list = ('commodity_code',
                  'name',
                  'section',
                  'chapter',
                  'heading',
                  'active',
                  'legal_act',
                  'exclusions',
                  'conditions',
                  'measure_type',
                  'additional_codes',
                  'attribute1',
                  'attribute2',
                  'attribute3',
                  'attribute4',
                  'attribute5',
                  'attribute6',
                  'start_date_active',
                  'end_date_active',
                  'footnote',
                  'description')


class CommodityCodesForm(forms.ModelForm):
    # start_date_active = forms.DateField(
    #     widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)
    # end_date_active = forms.DateField(
    #     widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = CmnCommodityCodes
        fields = ccc_field_list

    def __init__(self, *args, **kwargs):
        super(CommodityCodesForm, self).__init__(*args, **kwargs)

        self.fields['active'].initial = 'Y'

        for field in CmnCommodityCodes._meta.fields:
            if field.name in ccc_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityCodes._meta.fields:
            if field.name in ccc_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # try:
                    #     self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    # except:
                    #     print('CommodityCodesForm: Couldnt save:', self.cleaned_data[field.name],'/nField:',field)
        return self.cleaned_data


ccr_field_list = ('ccc_id',
                  'country_code',
                  'duty_rate',
                  'start_date_active',
                  'end_date_active',
                  'description',
                  'attribute1',
                  'attribute2',
                  'attribute3',
                  'attribute4',
                  'attribute5',
                  'attribute6',)


class CommodityRatesForm(forms.ModelForm):
    start_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)
    end_date_active = forms.DateField(
        widget=forms.SelectDateWidget(), input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = CmnCommodityRates
        fields = ccr_field_list

    def __init__(self, *args, **kwargs):
        super(CommodityRatesForm, self).__init__(*args, **kwargs)

        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnCommodityRates._meta.fields:
            if field.name in ccr_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/commoditycodes{0}/'
SLUG_FIELD = 'ccc_id'
SLUG_URL_KWARG = 'ccc_id'
TEMPLATE_PREFIX = 'commodities/cmncommoditycodes-{0}.html'
ORDERING = ('-ccc_id',)
FORM_CLASS = CommodityCodesForm
MODEL = CmnCommodityCodes
REC_IN_PAGE = 6  # settings.PUB_PAGE_LINES
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

import django_tables2 as tables
from django_tables2 import SingleTableView


class CommRatesTable(tables.Table):
    class Meta:
        model = CmnCommodityRates
        template_name = "django_tables2/bootstrap.html"
        fields = ccr_field_list


@method_decorator(login_required, name='dispatch')
class CommodityRatesListView(SingleTableView):
    model = CmnCommodityRates
    table_class = CommRatesTable
    template_name = 'commodities/cmncommodityrates-i-l.html'


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
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        page1 = self.request.GET.get('CCpage')
        if f_nm is not None:
            set1 = rows.filter(name__icontains=f_nm)
            set2 = rows.filter(commodity_code__icontains=f_nm)
            rows = set1 | set2
        paginator1 = Paginator(rows, self.paginate_by)
        try:
            rows = paginator1.page(page1)
        except PageNotAnInteger:
            rows = paginator1.page(1)
        except EmptyPage:
            rows = paginator1.page(paginator1.num_pages)
        context['comm_codes'] = rows

        ### Commodity Rate
        commrate_filter = self.request.GET.get('commrate_filter')
        if commrate_filter:
            set1 = CmnCommodityCodes.objects.filter(name__icontains=commrate_filter)
            set2 = CmnCommodityCodes.objects.filter(commodity_code__icontains=commrate_filter)
            ccc_set = set1 | set2
            ccr_queryset = CmnCommodityRates.objects.filter(ccc_id__in=ccc_set).order_by('-ccr_id')
        elif f_nm:
            set1 = CmnCommodityCodes.objects.filter(name__icontains=f_nm)
            set2 = CmnCommodityCodes.objects.filter(commodity_code__icontains=f_nm)
            ccc_set = set1 | set2
            ccr_queryset = CmnCommodityRates.objects.filter(ccc_id__in=ccc_set).order_by('-ccr_id')
        else:
            ccr_queryset = CmnCommodityRates.objects.all().order_by('-ccr_id')
        page2 = self.request.GET.get('CRpage')
        paginator2 = Paginator(ccr_queryset, self.paginate_by)
        try:
            ccr_queryset = paginator2.page(page2)
        except PageNotAnInteger:
            ccr_queryset = paginator2.page(1)
        except EmptyPage:
            ccr_queryset = paginator2.page(paginator2.num_pages)

        context['comm_rates'] = ccr_queryset

        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        # field_list = {'ccr_id': 'Rate ID', 'ccc_id_id': 'Code ID', 'bu_id': 'BU ID', 'duty_rate': 'Duty Rate',
        #               'country_code': 'Country', 'creation_date': 'Created At'}
        # context['test_table'] = get_table_html(CmnCommodityRates,
        #                                        field_list, filter_dict={'ccr_id__lt': '500', 'ccr_id__gt': '490'},
        #                                        ordering=['country_code', '-ccr_id', ],
        #                                        totals_list=['duty_rate', 'bu_id'])
        print('CONTEXT -->', context)
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


# @method_decorator(login_required, name='dispatch')
# class CompaniesDetailView(DetailView):
#     model = MODEL
#     slug_field = SLUG_FIELD
#     slug_url_kwarg = SLUG_URL_KWARG
#     template_name = TEMPLATE_PREFIX.format('d')
#     context_object_name = 'form'
#
#     def get_success_url(self):
#         return reverse(REVERSE)

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