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
from common.models import InvOptions
from common.sysutil import get_sequenceval
from common.table_gen import formfilter_queryset, general_exclude_list
from common.moduleattributes.table_fields import INV_OPTIONS

MODEL = InvOptions
PK_NAME = MODEL._meta.pk.name
non_editable_list = [field.name for field in MODEL._meta.fields if not field.editable]

exclude_list = general_exclude_list + non_editable_list


form_field_list = [field for field in INV_OPTIONS['fields'] if field not in exclude_list]

form_field_dict = {x[0]: x[1] for x in list(zip(INV_OPTIONS['fields'], INV_OPTIONS['headers'])) if
                   x[0] in form_field_list}

class InventoryOptionsForm(forms.ModelForm):
    class Meta:
        model = MODEL
        fields = form_field_list
        # labels = form_field_dict

    def __init__(self, *args, **kwargs):
        super(InventoryOptionsForm, self).__init__(*args, **kwargs)
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
URLPREFIX = '/' + APPNAME + '/inventoryoptions{0}/'
SLUG_FIELD = PK_NAME
SLUG_URL_KWARG = PK_NAME
TEMPLATE_PREFIX = 'inventory_options/inventory_options-{0}.html'
ORDERING = (PK_NAME,)
FORM_CLASS = InventoryOptionsForm
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "inventory:inventoryoptions_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
             'update': URLPREFIX.format('_update'),
             'delete': URLPREFIX.format('_delete'),
             'list': URLPREFIX.format('_list'),
             'title': 'Inventory Options',
             }

listview_filed_list = ['stock_search', 'item_order_by', 'item_number',
                       'default_markup', 'noof_selling_price', 'stock_adjustment_reason', 'manf_id', 'season_code_id',
                       'category_id', 'sub_category_id', 'price_break_id', 'location_id', 'printer_id', 'markup_type', ]
listview_filed_dict = {x[0]: x[1] for x in list(zip(INV_OPTIONS['fields'], INV_OPTIONS['headers'])) if
                       all([x[0] in listview_filed_list, x[0] not in []])}


@method_decorator(login_required, name='dispatch')
class InventoryOptionsListView(ListView):
    model = MODEL
    template_name = 'inventory_options/inventoryoptions_list.html'
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(InventoryOptionsListView, self).get_context_data(**kwargs)
        print('CONTEXT  - START --->', context)
        print('self.request.GET --->', self.request.GET)
        context['listview_filed_dict'] = listview_filed_dict
        context['form_field_dict'] = form_field_dict
        rows = InvOptions.objects.all().order_by(PK_NAME)


        if len(rows) == 1:
            context['container'] = rows[0]
            context['details'] = DetailForm(instance=rows[0])

        elif self.request.GET.get('inventoryoptions_id'):
            print('inventoryoptions_id -->', self.request.GET.get('inventoryoptions_id'))
            rows = InvOptions.objects.filter(inv_options_id=self.request.GET.get('inventoryoptions_id'))
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


tab_fields_dict = {'general':['stock_search', 'item_order_by', 'item_number','default_markup', 'noof_selling_price',
                              'stock_adjustment_reason', 'manf_id','season_code_id','category_id', 'sub_category_id',
                              'price_break_id', 'location_id', 'printer_id','markup_type','price_check_hint',
                              'quantity_format', 'populate_stock_history', 'min_qty_formula','max_qty_formula',
                              'reorder_qty_formula', 'sub_location', 'printer_copies', 'batch_format',
                              'print_output_path','price_break_criteria', 'report_markup_type',
                              'primary_sub_location_hint','req_rcv_sub_location_hint',],
                   'uom':['uom_id', 'single_uom_id', 'box_uom_id', 'weight_uom_id', 'volume_uom_id', 'dimension_uom_id',
                          'volume_divider',],
                   'glcodes':['gl_account_id', 'debit_gl_account_id', 'sales_gl_account_id', 'credit_gl_account_id',
                               'costofsales_gl_account_id', 'pricevariance_gl_account_id', 'pnl_gl_account_id',
                               'balancesheet_gl_account_id',],
                   'decisions':['defualt_picture_name', 'maintain_minusstock_separately',
                                'prefix_itemnumber', 'add_item_to_location', 'snapshot_all_items',
                                'ignore_location_attributes',
                                'auto_release_to_web', 'export_all_items', 'enable_palleting',]}


@method_decorator(login_required, name='dispatch')
class InventoryOptionsCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = 'inventory_options/inventoryoptions_form.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryOptionsCreateView, self).get_context_data(**kwargs)
        context['tab_fields'] = tab_fields_dict
        return context

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class InventoryOptionsUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = 'inventory_options/inventoryoptions_form.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(InventoryOptionsUpdateView, self).get_context_data(**kwargs)
        context['tab_fields'] = tab_fields_dict
        return context

    def get_success_url(self):
        return reverse(REVERSE)