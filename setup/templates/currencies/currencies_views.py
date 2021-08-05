from django import forms
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# specific to this view
from common.models import CmnCurrencies
from common.sysutil import get_sequenceval
from common.moduleattributes.table_fields import CMN_CURRENCIES
from common.table_gen import filter_queryset, general_exclude_list

MODEL = CmnCurrencies
PK_NAME = MODEL._meta.pk.name

APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/currencies{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'currencies/cmncurrencies-{0}.html'
ORDERING = ('sl_no', PK_NAME,)

REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:currencies_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Currencies',
             'findfield': 'Country Name',
             }
search_field_list = ['currency_name', 'cur_country']

exclude_list = general_exclude_list + ['bu_id','sl_no',]
xml_field_list = [field for field in CMN_CURRENCIES['fields'] if field not in exclude_list]
field_dict = {x[0]: x[1] for x in list(zip(CMN_CURRENCIES['fields'], CMN_CURRENCIES['headers'])) if x[0] in xml_field_list}


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = xml_field_list
        labels = field_dict

    def __init__(self, *args, **kwargs):
        super(CurrencyForm, self).__init__(*args, **kwargs)

        for field in MODEL._meta.fields:
            if field.name in xml_field_list:
                print(self.fields[field.name].label)
                if field.get_internal_type() == 'CharField':
                    self.fields[field.name].widget.attrs.update({'style': 'text-transform:uppercase'})

    def clean(self):
        self._validate_unique = True
        for field in MODEL._meta.fields:
            if field.name in xml_field_list and field.name not in []:
                if field.get_internal_type() == 'CharField':
                    self.cleaned_data[field.name] = self.cleaned_data[field.name].upper()
        return self.cleaned_data


class DetailForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = xml_field_list
        labels = field_dict
    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for field in xml_field_list:
            self.fields[field].widget.attrs['readonly'] = True


FORM_CLASS = CurrencyForm


@method_decorator(login_required, name='dispatch')
class CurrencyListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(CurrencyListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        context['search_field_dict'] = {x: {'label': field_dict[x], 'value': ''} for x in search_field_list}
        page = self.request.GET.get('page')
        if 'list_filter' in self.request.GET:
            context, rows = filter_queryset(context, self.request.GET, rows, search_field_list)
            if len(rows) == 1:
                context['details'] = DetailForm(instance=rows[0])
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


@method_decorator(login_required, name='dispatch')
class CurrencyCreateView(CreateView):
    # model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.sl_no = get_sequenceval('cmn_currencies_s.nextval')
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(REVERSE)


class CurrencyUpdateView(UpdateView):
    model = MODEL
    fields = [f for f in xml_field_list if f!=PK_NAME]
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    # form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


class CurrencyDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('d')

    def get_success_url(self):
        return reverse(REVERSE)
