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
from common.models import InvPriceBreakHeaders, InvPriceBreakLines
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import INV_PRICE_BREAK_HEADERS, INV_PRICE_BREAK_LINES


MODEL = InvPriceBreakHeaders
PK_NAME = MODEL._meta.pk.name
MODEL_FIELD_LIST = INV_PRICE_BREAK_HEADERS

non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in MODEL_FIELD_LIST['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(MODEL_FIELD_LIST['fields'], MODEL_FIELD_LIST['headers'])) if
                   x[0] in form_field_list}


class PriceBreakHeaderForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(PriceBreakHeaderForm, self).__init__(*args, **kwargs)
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


lines_non_editable_list = [field.name for field in InvPriceBreakLines._meta.fields if not field.editable]

lines_exclude_list = general_exclude_list + lines_non_editable_list

lines_form_field_list = [field for field in INV_PRICE_BREAK_LINES['fields'] if field not in lines_exclude_list]

lines_form_field_dict = {x[0]: x[1] for x in
                         list(zip(INV_PRICE_BREAK_LINES['fields'], INV_PRICE_BREAK_LINES['headers'])) if
                         x[0] in lines_form_field_list}


class PriceBreakLinesForm(forms.ModelForm):
    class Meta:
        model = InvPriceBreakLines
        fields = lines_form_field_dict.keys()
        labels = lines_form_field_dict

    def __init__(self, *args, **kwargs):
        super(PriceBreakLinesForm, self).__init__(*args, **kwargs)
        for field in InvPriceBreakLines._meta.fields:
            if field.name in lines_form_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in InvPriceBreakLines._meta.fields:
            if field.name in lines_form_field_dict.keys() and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    try:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
                    except:
                        self.cleaned_data[field.name] = self.cleaned_data[field.name]
        return self.cleaned_data


class DetailForm(forms.ModelForm):
    class Meta:
        model = InvPriceBreakLines
        fields = '__all__'
        widgets = {x.name: forms.TextInput(attrs={'readonly': True, }) for x in InvPriceBreakLines._meta.fields}


APPNAME = 'inventory'
URLPREFIX = '/' + APPNAME + '/pricebreaks{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'price_breaks/pricebreaks-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = PriceBreakHeaderForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "pricing:pricebreaks"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Price Breaks',
             }

search_field_list = ['name',]
listview_filed_list = ['price_break_id', 'terms_name', 'terms_days', 'terms_type']

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
class PriceBreakHeadersListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    # context_object_name = 'data'
    ordering = (PK_NAME,)
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(PriceBreakHeadersListView, self).get_context_data(**kwargs)
        # print('CONTEXT  - START --->',context)
        print('self.request.GET --->', self.request.GET)
        print('self.request.POST --->', self.request.POST)
        context['listview_filed_dict'] = listview_filed_dict
        context['lines_form_field_dict'] = lines_form_field_dict
        header_list = InvPriceBreakHeaders.objects.all().order_by(PK_NAME)

        context['search_form'] = SearchForm()
        if 'list_filter' in self.request.GET:
            header_list = formfilter_queryset(self.request.GET, header_list, search_field_list)
            context['search_form'] = SearchForm(self.request.GET)

        if len(header_list) == 1:
            lines_list = InvPriceBreakLines.objects.filter(ipbh_price_break_id=header_list[0])
            context['details'] = lines_list

        elif self.request.GET.get('price_break_id'):
            print('price_break_id -->', self.request.GET.get('price_break_id'))
            header_list = InvPriceBreakHeaders.objects.filter(price_break_id=self.request.GET.get('price_break_id'))
            header = InvPriceBreakHeaders.objects.get(price_break_id=self.request.GET.get('price_break_id'))
            lines_list = InvPriceBreakLines.objects.filter(ipbh_price_break_id=header)
            context['details'] = lines_list

        if len(header_list) > REC_IN_PAGE:
            page = self.request.GET.get('page')
            paginator = Paginator(header_list, self.paginate_by)
            try:
                header_list = paginator.page(page)
            except PageNotAnInteger:
                header_list = paginator.page(1)
            except EmptyPage:
                header_list = paginator.page(paginator.num_pages)
            context['page_obj'] = header_list
            context['paginator'] = paginator
        else:
            del context['page_obj']
            del context['paginator']

        # context['header_list'] = header_list
        context['object_list'] = header_list
        self.queryset = header_list
        context['request'] = self.request
        context['MYCONTEXT'] = MYCONTEXT
        print('CONTEXT  - END --->', context)
        return context


@method_decorator(login_required, name='dispatch')
class PriceBreakHeadersCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('form')

    def get_context_data(self, **kwargs):
        context = super(PriceBreakHeadersCreateView, self).get_context_data(**kwargs)
        context['title'] = 'New Price Break Header'
        context['class'] = 'New'
        context['model'] = 'Price Break Header'
        context['cancel_href'] = '/pricing/pricebreaks/'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.price_break_id = get_sequenceval('inv_price_break_headers_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PriceBreakHeadersUpdateView(UpdateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('form')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_context_data(self, **kwargs):
        context = super(PriceBreakHeadersUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Edit Price Break Header - {}'.format(self.object)
        context['class'] = 'Edit'
        context['model'] = 'Price Break Header'
        context['delete_href'] = '/pricing/pricebreakheader_delete/{}/'.format(self.object.pk)
        context['cancel_href'] = '/pricing/pricebreaks/'
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PriceBreakHeadersDeleteView(DeleteView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = PK_NAME
    slug_url_kwarg = PK_NAME

    def get_context_data(self, **kwargs):
        context = super(PriceBreakHeadersDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Delete Price Break Header - {}'.format(self.object)
        context['class'] = 'Delete'
        context['model'] = 'Price Break Header - {}'.format(self.object)
        context['cancel_href'] = '/pricing/pricebreaks/'
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PriceBreakLinesCreateView(CreateView):
    model = InvPriceBreakLines
    form_class = PriceBreakLinesForm
    template_name = TEMPLATE_PREFIX.format('form')

    def get_context_data(self, **kwargs):
        context = super(PriceBreakLinesCreateView, self).get_context_data(**kwargs)
        context['form'] = PriceBreakLinesForm()
        context['title'] = 'New Price Break Line'
        context['class'] = 'New'
        context['model'] = 'Price Break Line'
        header_id = self.request.GET.get('price_break_id')
        context['cancel_href'] = '/pricing/pricebreaks/?price_break_id={}'.format(header_id)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.price_break_line_id = get_sequenceval('inv_price_break_lines_s.nextval')
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class PriceBreakLinesUpdateView(UpdateView):
    model = InvPriceBreakLines
    form_class = PriceBreakLinesForm
    template_name = TEMPLATE_PREFIX.format('form')
    slug_field = 'price_break_line_id'
    slug_url_kwarg = 'price_break_line_id'

    def get_context_data(self, **kwargs):
        context = super(PriceBreakLinesUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Edit Price Break Line - {}'.format(self.object)
        context['class'] = 'Edit'
        context['model'] = 'Price Break Line'
        context['price_break_id'] = self.object.ipbh_price_break_id.price_break_id
        context['delete_href'] = '/pricing/pricebreakline_delete/{}/'.format(self.object.pk)
        context['cancel_href'] = '/pricing/pricebreaks/?price_break_id={}'.format(context['price_break_id'])
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/pricing/pricebreaks/?price_break_id={0}'.format(context['price_break_id'])


@method_decorator(login_required, name='dispatch')
class PriceBreakLinesDeleteView(DeleteView):
    model = InvPriceBreakLines
    template_name = TEMPLATE_PREFIX.format('d')
    slug_field = 'price_break_line_id'
    slug_url_kwarg = 'price_break_line_id'

    def get_context_data(self, **kwargs):
        context = super(PriceBreakLinesDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Delete Price Break Line - {}'.format(self.object)
        context['class'] = 'Delete'
        context['model'] = 'Price Break Line'
        context['price_break_id'] = self.object.ipbh_price_break_id.price_break_id
        context['cancel_href'] = '/pricing/pricebreaks/?price_break_id={}'.format(context['price_break_id'])
        return context

    def get_success_url(self):
        context = self.get_context_data()
        return '/pricing/pricebreaks/?price_break_id={0}'.format(context['price_break_id'])