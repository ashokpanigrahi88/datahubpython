from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# specific to this view
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.models import CmnCompanies
from common.moduleattributes.table_fields import CMN_COMPANIES

MODEL = CmnCompanies
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = CMN_COMPANIES

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                   x[0] in form_field_list}

# companies_field_list = ('comp_name',
#                         'comp_trading_name',
#                         'comp_slogan',
#                         'comp_reg_no',
#                         'comp_vat_reg_no',
#                         'comp_address_line1',
#                         'comp_city',
#                         'comp_county',
#                         'comp_post_code',
#                         'comp_phone1',
#                         'comp_phone2',
#                         'comp_fax',
#                         'comp_email',
#                         'url',
#                         'orig_system_ref_desc',
#                         'orig_system_ref_code',
#                         'gl_account_id',
#                         'attribute1',
#                         'attribute2',
#                         'cc1_currency_code',
#                         # 'cc1_cur_country',
#                         'cco_country_code')


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(CompaniesForm, self).__init__(*args, **kwargs)
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in ['attribute1', 'attribute2',]:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in ['attribute1', 'attribute2',]:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/company{0}/'
SLUG_FIELD = 'comp_id'
SLUG_URL_KWARG = 'comp_id'
TEMPLATE_PREFIX = 'companies/cmncompanies-{0}.html'
ORDERING = ('comp_id',)
FORM_CLASS = CompaniesForm
MODEL = CmnCompanies
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:companies_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Companies',
             # 'findfield': 'Company Name',
             }

search_field_list = ['comp_name', ]
listview_filed_list = ['comp_name', 'comp_trading_name', 'comp_vat_reg_no', 'comp_reg_no',
                       'comp_address_line1', 'comp_city', 'comp_county', 'comp_post_code', 'cco_country_code',
                       'comp_phone1', 'comp_email', 'url', 'orig_system_ref_code',
                       'orig_system_ref_desc', 'gl_account_id',]

listview_filed_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                       all([x[0] in listview_filed_list, x[0] not in []])}


class DetailForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = '__all__'
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in MODEL._meta.fields}

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
class CompaniesListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(CompaniesListView, self).get_context_data(**kwargs)
        context['listview_filed_dict'] = listview_filed_dict
        rows = CmnCompanies.objects.all().order_by('comp_name')
        context['search_form'] = SearchForm()

        rows = self.get_queryset()
        if 'list_filter' in self.request.GET:
            rows = formfilter_queryset(self.request.GET, rows, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(rows) == 1:
            context['company'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        elif self.request.GET.get('company_id'):
            print('company_id -->', self.request.GET.get('company_id'))
            rows = CmnCompanies.objects.filter(comp_id=self.request.GET.get('company_id'))
            context['company'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        if len(rows)>1:
            page = self.request.GET.get('page')
            paginator = Paginator(rows, self.paginate_by)
            try:
                rows = paginator.page(page)
            except PageNotAnInteger:
                rows = paginator.page(1)
            except EmptyPage:
                rows = paginator.page(paginator.num_pages)

        context['rows'] = rows
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        return context


# @method_decorator(login_required, name='dispatch')
class CompaniesCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.comp_id = get_sequenceval('cmn_companies_s.nextval')
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


class CompaniesUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


class CompaniesDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('d')

    def get_success_url(self):
        return reverse(REVERSE)
