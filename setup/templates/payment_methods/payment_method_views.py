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
from common.models import CmnPaymentMethods
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_PAYMENT_METHODS

MODEL = CmnPaymentMethods
PK_NAME = MODEL._meta.pk.name
non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in CMN_PAYMENT_METHODS['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(CMN_PAYMENT_METHODS['fields'], CMN_PAYMENT_METHODS['headers'])) if
              x[0] in form_field_list}


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


class DetailForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = '__all__'
        widgets = {x: forms.TextInput(attrs={'readonly': True, }) for x in form_field_list}


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/paymentmethods{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'payment_methods/paymentmethods-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = PaymentMethodForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:paymentmethods_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Payment Methods',
             }
search_field_list = ['pmnt_code', 'pmnt_method',]
listview_filed_list = ['sl_no','pmnt_code','pmnt_method']
listview_filed_dict = {x[0]: x[1] for x in list(zip(CMN_PAYMENT_METHODS['fields'], CMN_PAYMENT_METHODS['headers'])) if
                       all([x[0] in form_field_list, x[0] not in ['validation_criteria', ]])}


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
class PaymentMethodsListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(PaymentMethodsListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->',context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        methods_list = CmnPaymentMethods.objects.all().order_by(PK_NAME)

        # context['search_field_dict'] = {x: {'label': form_field_dict[x], 'value': ''} for x in search_field_list}
        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            methods_list = formfilter_queryset(self.request.GET, methods_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(methods_list)==1:
            context['details'] = DetailForm(instance=methods_list[0])
        elif self.request.GET.get('paymentmethod_id'):
            print('paymentmethod_id -->', self.request.GET.get('paymentmethod_id'))
            methods_list = CmnPaymentMethods.objects.filter(pmnt_method_id=self.request.GET.get('paymentmethod_id'))
            context['details'] = DetailForm(instance=methods_list[0])

        if len(methods_list)>REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(methods_list, self.paginate_by)
            try:
                methods_list = paginator.page(page)
            except PageNotAnInteger:
                methods_list = paginator.page(1)
            except EmptyPage:
                methods_list = paginator.page(paginator.num_pages)

        context['methods_list'] = methods_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class PaymentMethodsCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.pmnt_method_id = get_sequenceval('cmn_payment_methods_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PaymentMethodsUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PaymentMethodsDeleteView(DeleteView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)