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
from common.models import CmnContainers
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import CMN_CONTAINERS

MODEL = CmnContainers
PK_NAME = MODEL._meta.pk.name
non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in CMN_CONTAINERS['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(CMN_CONTAINERS['fields'], CMN_CONTAINERS['headers'])) if
                   x[0] in form_field_list}


class ContainerForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(ContainerForm, self).__init__(*args, **kwargs)
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
URLPREFIX = '/' + APPNAME + '/containers{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'containers/cmncontainers-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = ContainerForm

REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:containers_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Containers',
             'findfield': 'Container ID/Name',
             }

search_field_list = ['pc_name',]
listview_filed_list = ['pc_id', 'pc_name', 'pc_code','container_category','container_type',
                       'container_recycle_code', ]
listview_filed_dict = {x[0]: x[1] for x in list(zip(CMN_CONTAINERS['fields'], CMN_CONTAINERS['headers'])) if
                       all([x[0] in listview_filed_list, x[0] not in []])}


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
class ContainersListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(ContainersListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->', context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        context['form_field_dict'] = form_field_dict
        rows = CmnContainers.objects.all().order_by(PK_NAME)

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            rows = formfilter_queryset(self.request.GET, rows, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(rows) == 1:
            context['container'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        elif self.request.GET.get('container_id'):
            print('container_id -->', self.request.GET.get('container_id'))
            rows = CmnContainers.objects.filter(pc_id=self.request.GET.get('container_id'))
            context['container'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        if len(rows) > REC_IN_PAGE:
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
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class ContainersCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.pc_id = get_sequenceval('cmn_containers_s.nextval')
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class ContainersUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class ContainersDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('d')

    def get_success_url(self):
        return reverse(REVERSE)