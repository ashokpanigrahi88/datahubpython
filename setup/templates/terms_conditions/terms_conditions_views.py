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
from common.models import CmnTerms
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_TERMS

MODEL = CmnTerms
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = CMN_TERMS

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
              x[0] in form_field_list}


class TNCForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(TNCForm, self).__init__(*args, **kwargs)
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


APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/tnc{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'terms_conditions/tnc-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = TNCForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:terms_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Terms and Conditions',
             }

search_field_list = ['usage', 'tc_text',]
# listview_filed_list = ['cpt_id','terms_name','terms_days','terms_type']


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
class TNCListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(TNCListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->',context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        tnc_list = CmnTerms.objects.all().order_by(PK_NAME).order_by('tc_code_id')

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            tnc_list = formfilter_queryset(self.request.GET, tnc_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(tnc_list)>REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(tnc_list, self.paginate_by)
            try:
                tnc_list = paginator.page(page)
            except PageNotAnInteger:
                tnc_list = paginator.page(1)
            except EmptyPage:
                tnc_list = paginator.page(paginator.num_pages)

        context['tnc_list'] = tnc_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class TNCCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.tc_code_id = get_sequenceval('cmn_terms_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class TNCUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class TNCDeleteView(DeleteView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)