from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.db import transaction

# specific to this view
from common.models import CmnTaxCodes, CmnTaxBreakups
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_TAX_CODES, CMN_TAX_BREAKUPS

MODEL = CmnTaxCodes
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = CMN_TAX_CODES

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
              x[0] in form_field_list}


class TaxCodeForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(TaxCodeForm, self).__init__(*args, **kwargs)
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        return self.cleaned_data


taxbreakup_non_editable_list = [field.name for field in CmnTaxBreakups._meta.fields if not field.editable]

taxbreakup_exclude_list = general_exclude_list + taxbreakup_non_editable_list

taxbreakup_form_field_list = [field for field in CMN_TAX_BREAKUPS['fields'] if field not in taxbreakup_exclude_list]

taxbreakup_field_dict = {x[0]: x[1] for x in list(zip(CMN_TAX_BREAKUPS['fields'], CMN_TAX_BREAKUPS['headers'])) if
                   x[0] in taxbreakup_form_field_list}


class TaxBreakupsForm(forms.ModelForm):
    class Meta:
        model = CmnTaxBreakups
        fields = taxbreakup_field_dict.keys()
        labels = taxbreakup_field_dict

    def __init__(self, *args, **kwargs):
        super(TaxBreakupsForm, self).__init__(*args, **kwargs)
        for field in CmnTaxBreakups._meta.fields:
            if field.name in taxbreakup_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnTaxBreakups._meta.fields:
            if field.name in taxbreakup_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


class DetailForm(forms.ModelForm):
    class Meta:
        model = CmnTaxBreakups
        fields = '__all__'
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in CmnTaxBreakups._meta.fields}


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/taxcodes{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'tax_codes/taxcodes-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = TaxCodeForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:taxcodes_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Tax Codes',
             }

search_field_list = ['tax_code',]
listview_filed_list = [PK_NAME] + form_field_list


listview_filed_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                       all([x[0] in listview_filed_list, x[0] not in [ ]])}


class SearchForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = search_field_list
        labels = form_field_dict
        widgets = {x: forms.TextInput(attrs={'required': False, }) for x in search_field_list}

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        for field in search_field_list:
            self.fields[field].required = False


@method_decorator(login_required, name='dispatch')
class TaxCodesListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(TaxCodesListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->',context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        context['taxbreakup_field_dict'] = taxbreakup_field_dict
        taxcodes_list = CmnTaxCodes.objects.all().order_by(PK_NAME).order_by('tax_code')

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            taxcodes_list = formfilter_queryset(self.request.GET, taxcodes_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(taxcodes_list)==1:
            breakup_list = CmnTaxBreakups.objects.filter(ctc_tax_code_id=taxcodes_list[0])
            context['details'] = breakup_list

        elif self.request.GET.get('taxcode_id'):
            print('taxcode_id -->', self.request.GET.get('taxcode_id'))
            parent_term = CmnTaxCodes.objects.get(tax_code_id=self.request.GET.get('taxcode_id'))
            breakup_list = CmnTaxBreakups.objects.filter(ctc_tax_code_id=parent_term)
            context['details'] = breakup_list

        if len(taxcodes_list)>REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(taxcodes_list, self.paginate_by)
            try:
                taxcodes_list = paginator.page(page)
            except PageNotAnInteger:
                taxcodes_list = paginator.page(1)
            except EmptyPage:
                taxcodes_list = paginator.page(paginator.num_pages)

        context['taxcodes_list'] = taxcodes_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class TaxCodesCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def get_context_data(self, **kwargs):
        context = super(TaxCodesCreateView, self).get_context_data(**kwargs)
        context['model'] = 'Tax Code'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.tax_code_id = get_sequenceval('cmn_tax_codes_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class TaxCodesUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_context_data(self, **kwargs):
        context = super(TaxCodesUpdateView, self).get_context_data(**kwargs)
        context['model'] = 'Tax Code'
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class TaxCodesDeleteView(DeleteView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_context_data(self, **kwargs):
        context = super(TaxCodesDeleteView, self).get_context_data(**kwargs)
        context['model'] = 'Tax Code'
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class TaxBreakupsCreateView(CreateView):
    model = CmnTaxBreakups
    form_class = TaxBreakupsForm
    template_name = TEMPLATE_PREFIX.format('c')

    def get_context_data(self, **kwargs):
        context = super(TaxBreakupsCreateView, self).get_context_data(**kwargs)
        context['form'] = TaxBreakupsForm()
        context['model'] = 'Tax Breakup'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.ctb_id = get_sequenceval('cmn_tax_breakups_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return '/setup/taxcodes_list/?taxcode_id={0}'.format(self.object.ctc_tax_code_id.tax_code_id)


@method_decorator(login_required, name='dispatch')
class TaxBreakupsUpdateView(UpdateView):
    model = CmnTaxBreakups
    form_class = TaxBreakupsForm
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = 'ctb_id'
    slug_url_kwarg = 'ctb_id'

    def get_context_data(self, **kwargs):
        context = super(TaxBreakupsUpdateView, self).get_context_data(**kwargs)
        context['model'] = 'Tax Breakup'
        context['taxcode_id'] = self.object.ctc_tax_code_id.tax_code_id
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/taxcodes_list/?taxcode_id={0}'.format(context['taxcode_id'])


@method_decorator(login_required, name='dispatch')
class TaxBreakupsDeleteView(DeleteView):
    model = CmnTaxBreakups
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = 'ctb_id'
    slug_url_kwarg = 'ctb_id'

    def get_context_data(self, **kwargs):
        context = super(TaxBreakupsDeleteView, self).get_context_data(**kwargs)
        context['model'] = 'Tax Breakup'
        context['taxcode_id'] = self.object.ctc_tax_code_id.tax_code_id
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/taxcodes_list/?taxcode_id={0}'.format(context['taxcode_id'])