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
from common.models import CmnPaymentTerms, CmnPaymenttermBreakups
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_PAYMENT_TERMS

MODEL = CmnPaymentTerms
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = CMN_PAYMENT_TERMS

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
              x[0] in form_field_list}


class PaymentTermForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(PaymentTermForm, self).__init__(*args, **kwargs)
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


breakup_field_dict = {'cpt_cpt_id':'Payment Term','sl_no': 'SL#', 'cpb_name': 'Name',
                      'cpb_type': 'Break-up Type', 'cpb_percent': 'Break-up Percentage'}

class PaymentTermBreakupForm(forms.ModelForm):
    class Meta:
        model = CmnPaymenttermBreakups
        fields = breakup_field_dict.keys()
        labels = breakup_field_dict

    def __init__(self, *args, **kwargs):
        super(PaymentTermBreakupForm, self).__init__(*args, **kwargs)
        for field in CmnPaymenttermBreakups._meta.fields:
            if field.name in breakup_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in CmnPaymenttermBreakups._meta.fields:
            if field.name in breakup_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


class DetailForm(forms.ModelForm):
    class Meta:
        model = CmnPaymenttermBreakups
        fields = '__all__'
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in CmnPaymenttermBreakups._meta.fields}


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/paymentterms{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'payment_terms/paymentterms-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = PaymentTermForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:paymentterms_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Payment Methods',
             }

search_field_list = ['terms_name', 'terms_type',]
listview_filed_list = ['cpt_id','terms_name','terms_days','terms_type']


listview_filed_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                       all([x[0] in form_field_list, x[0] not in [ ]])}


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
class PaymentTermsListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(PaymentTermsListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->',context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        context['breakup_field_dict'] = breakup_field_dict
        terms_list = CmnPaymentTerms.objects.all().order_by(PK_NAME).order_by('terms_days')

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            terms_list = formfilter_queryset(self.request.GET, terms_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(terms_list)==1:
            breakup_list = CmnPaymenttermBreakups.objects.filter(cpt_cpt_id=terms_list[0])
            context['details'] = breakup_list

        elif self.request.GET.get('paymentterm_id'):
            print('paymentterm_id -->', self.request.GET.get('paymentterm_id'))
            parent_term = CmnPaymentTerms.objects.get(cpt_id=self.request.GET.get('paymentterm_id'))
            breakup_list = CmnPaymenttermBreakups.objects.filter(cpt_cpt_id=parent_term)
            context['details'] = breakup_list

        if len(terms_list)>REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(terms_list, self.paginate_by)
            try:
                terms_list = paginator.page(page)
            except PageNotAnInteger:
                terms_list = paginator.page(1)
            except EmptyPage:
                terms_list = paginator.page(paginator.num_pages)

        context['href_fields'] = ['terms_name',]
        context['terms_list'] = terms_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class PaymentTermsCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.cpt_id = get_sequenceval('cmn_payment_terms_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PaymentTermsUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PaymentTermsDeleteView(DeleteView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PaymentTermBreakupCreateView(CreateView):
    model = CmnPaymenttermBreakups
    form_class = PaymentTermBreakupForm
    template_name = TEMPLATE_PREFIX.format('c')

    def get_context_data(self, **kwargs):
        context = super(PaymentTermBreakupCreateView, self).get_context_data(**kwargs)
        context['form'] = PaymentTermBreakupForm()
        context['model'] = 'Payment Term Breakup'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.cpb_id = get_sequenceval('cmn_paymentterm_breakups_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return '/setup/pmntterms_list/?paymentterm_id={0}'.format(self.object.cpt_cpt_id.cpt_id)


@method_decorator(login_required, name='dispatch')
class PaymentTermBreakupUpdateView(UpdateView):
    model = CmnPaymenttermBreakups
    form_class = PaymentTermBreakupForm
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = 'cpb_id'
    slug_url_kwarg = 'cpb_id'

    def get_context_data(self, **kwargs):
        context = super(PaymentTermBreakupUpdateView, self).get_context_data(**kwargs)
        context['model'] = 'Payment Term Breakup'
        context['paymentterm_id'] = self.object.cpt_cpt_id.cpt_id
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/pmntterms_list/?paymentterm_id={0}'.format(context['paymentterm_id'])


@method_decorator(login_required, name='dispatch')
class PaymentTermBreakupDeleteView(DeleteView):
    model = CmnPaymenttermBreakups
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = 'cpb_id'
    slug_url_kwarg = 'cpb_id'

    def get_context_data(self, **kwargs):
        context = super(PaymentTermBreakupDeleteView, self).get_context_data(**kwargs)
        context['model'] = 'Payment Term Breakup'
        context['paymentterm_id'] = self.object.cpt_cpt_id.cpt_id
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/setup/pmntterms_list/?paymentterm_id={0}'.format(context['paymentterm_id'])