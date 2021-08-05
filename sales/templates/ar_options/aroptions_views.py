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
from common.models import ArOptions
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import AR_OPTIONS

MODEL = ArOptions
PK_NAME = MODEL._meta.pk.name
non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list

form_field_list = [field for field in AR_OPTIONS['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(AR_OPTIONS['fields'], AR_OPTIONS['headers'])) if
                   x[0] in form_field_list}


class ArOptionsForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        # labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(ArOptionsForm, self).__init__(*args, **kwargs)
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
URLPREFIX = '/' + APPNAME + '/aroptions{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'ar_options/aroptions-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = ArOptionsForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "sales:aroptions_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'AR Options',
             }

listview_filed_list = ['customer_id', 'price_type_id', 'offer_price_type_id',
                       'return_sub_location_id', 'return_location_id', 'invoice_report_format',
                       'invoice_screen_format', 'cpt_id', 'pmnt_method_id', 'bank_account_id', 'gl_account_id',
                       'sales_order_type', 'gl_cashingup_by']
listview_filed_dict = {x[0]: x[1] for x in list(zip(AR_OPTIONS['fields'], AR_OPTIONS['headers'])) if
                       all([x[0] in listview_filed_list, x[0] not in []])}


@method_decorator(login_required, name='dispatch')
class ArOptionsListView(ListView):
    model = MODEL
    template_name = 'ar_options/aroptions_list.html'
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(ArOptionsListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->', context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        context['form_field_dict'] = form_field_dict
        rows = ArOptions.objects.all().order_by(PK_NAME)

        if len(rows) == 1:
            context['container'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        elif self.request.GET.get('aroption_id'):
            print('aroption_id -->', self.request.GET.get('aroption_id'))
            rows = ArOptions.objects.filter(ar_option_id=self.request.GET.get('aroption_id'))
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


tab_fields_dict = {'general': ['ar_option_id', 'customer_id', 'price_type_id', 'offer_price_type_id',
                               'return_sub_location_id', 'return_location_id', 'invoice_report_format',
                               'invoice_screen_format', 'cpt_id', 'pmnt_method_id', 'bank_account_id', 'gl_account_id',
                               'sales_order_type', 'gl_cashingup_by', 'special_offer_hint', 'document_path',
                               'customer_numbering', 'barcode_qty_hint', 'inv_requisition_hint', ],
                   'decisions': ['allocate_order_qty', 'quantity_popup', 'display_invnumber_onfinalise',
                           'populate_invoice_batch', 'surcharge_account_customers', 'write_invoice_to_file',
                           'central_payment', 'pay_inout_slip', 'print_customer_note1', 'print_customer_note2',
                           'print_customer_note3', 'apply_offer_on_custprice', 'must_select_customer',
                                 'can_change_customer', 'print_bo_receipt', 'log_off_after_each_trans',
                                 'duplicate_customer_name', 'print_batch_count', 'allow_minus_stock',
                                 'allow_part_invoice', 'monitor_layaway', 'alert_less_then_cost',],
                   'printers': ['print_output_path', 'printer1_id', 'printer1_preview_mode', 'printer1_batch_mode',
                                'printer1_execution_mode', 'printer1_format', 'printer1_copies', 'printer2_id',
                                'printer2_copies', 'printer2_preview_mode', 'printer2_format', 'printer2_batch_mode',
                                'printer2_execution_mode', 'receipt_printer_id',],
                   'frontoffice': ['quickcode_id', 'fo_price_basis', 'credit_limit_control', 'unit_cost_plus_percent',
                                    'noof_layaways', 'default_item_filter', 'logoff_timeout',],
                   'www':['www_markupdown', 'www_price_type_id', 'www_customer_category', 'www_subscription_preference',
                          'www_min_order_value', 'www_min_order_freeship', 'www_price_break_display',
                          'delivery_confirmation', 'picking_confirmation', 'backorder_header_id',]}


@method_decorator(login_required, name='dispatch')
class ArOptionsCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = 'ar_options/aroptions_form.html'

    def get_context_data(self, **kwargs):
        context = super(ArOptionsCreateView, self).get_context_data(**kwargs)
        context['tab_fields'] = tab_fields_dict
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class ArOptionsUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = 'ar_options/aroptions_form.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(ArOptionsUpdateView, self).get_context_data(**kwargs)
        context['tab_fields'] = tab_fields_dict
        return context

    def get_success_url(self):
        return reverse(REVERSE)