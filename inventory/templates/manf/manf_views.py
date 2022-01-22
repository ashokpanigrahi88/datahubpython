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
from common.models import InvManufacturers
from common.sysutil import get_sequenceval, get_form_context
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import INV_MANUFACTURERS

MODEL = InvManufacturers
MODEL_FIELD_LIST = INV_MANUFACTURERS
PK_NAME, non_editable_list, exclude_list ,form_field_list,form_field_dict = get_form_context(MODEL,MODEL_FIELD_LIST)


class ManfForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(ManfForm, self).__init__(*args, **kwargs)
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        super(ManfForm, self).clean()
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in form_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        print('cleaneddate',self.cleaned_data)
        return self.cleaned_data


APPNAME = 'inventory'
URLPREFIX = '/' + APPNAME + '/manf{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'manf/manf-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = ManfForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "inventory:manf_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Manufacturers',
             }

search_field_list = ['manf_name', ]
# listview_filed_list = ['cpt_id','terms_name','terms_days','terms_type']


listview_filed_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                       all([x[0] in form_field_list, x[0] not in []])}


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
class ManfListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(ManfListView, self).get_context_data(**kwargs)
        # print('CONTEXT  - START --->',context)
        # print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        manf_list = MODEL.objects.all().order_by(PK_NAME)

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            manf_list = formfilter_queryset(self.request.GET, manf_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(manf_list) > REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(manf_list, self.paginate_by)
            try:
                manf_list = paginator.page(page)
            except PageNotAnInteger:
                manf_list = paginator.page(1)
            except EmptyPage:
                manf_list = paginator.page(paginator.num_pages)

        context['manf_list'] = manf_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        # print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class ManfCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('form')

    def get_context_data(self, **kwargs):
        context = super(ManfCreateView, self).get_context_data(**kwargs)
        context['title'] = 'New Manufacturer'
        context['class'] = 'New'
        context['model'] = 'Manufacturer'
        context['cancel_href'] = '/inventory/manf/'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.manf_id = get_sequenceval('inv_manufacturers_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class ManfUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('form')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME
    #fields = form_field_list

    def get_context_data(self, **kwargs):
        context = super(ManfUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Edit Manufacturer'
        context['class'] = 'Edit'
        context['model'] = 'Manufacturer'
        context['delete_href'] = '/inventory/manf_delete/{0}'.format(context['object'])
        context['cancel_href'] = '/inventory/manf/'
        print(context)
        return context


    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class ManfDeleteView(DeleteView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_success_url(self):
        return reverse(REVERSE)