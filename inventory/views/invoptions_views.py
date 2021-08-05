from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# specific to this view

from setup.forms.sysoptions_forms import *
from common.models import *


def add_fields(data:{}):
    data['general_field_list'] = ['ver_no', 'financial_year_start_date', 'currency_code', 'tax_code_id',
                                  'country_code', 'application_directory', 'picture_path', 'www_image_path',
                                  'company_logo', 'picture_type', 'helpfile', 'helpexec', 'casetype',
                                  'menu_color_scheme', 'consolidate_item_in_trans', 'enable_notifications',
                                  'batch_format', 'period_header_id', 'business_type', 'licence_type',
                                  'install_type', 'enable_tparty_interface']
    data['email_field_list'] = ['enable_emailing', 'smtp_server_name', 'smtp_user_name', 'smtp_password',
                                'smtp_domain', 'smtp_port',
                                'smtp_from_address', 'to_address_disp', 'email_cc', 'email_bcc',
                                'external_mail_exe', 'pb_testemail']
    data['reports_field_list'] = ['report_server_name', 'report_execution_method', 'report_output_path',
                                  'report_server_url', 'default_browser', 'back_office_url',
                                  'alternate_report_server', 'alternate_report_url', 'remote_report_url',
                                  'mobile_url', 'mobile_url_homepage', 'db_string']
    data['cards_field_list'] = ['card_category_code', 'card_prefix_code', 'identifier', 'active', 'description',
                                'askfor_pin', 'card_options_id']
    data['dirs_field_list'] = ['dir_inbound', 'dir_outbound', 'dir_tmp', 'dir_inbound_backup',
                               'dir_outbound_backup']
    return data

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsListView(ListView):

    model = CmnSysOptions
    template_name = 'setup/cmnsysoptions-l.html'
    context_object_name = 'data'
    ordering = ('sys_options_id',)
    paginate_by = PUB_PAGE_LINES

    def get_context_data(self, **kwargs):
        context = super(CmnSysOptionsListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
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
        return context

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsCreateView(CreateView):
    model = CmnSysOptions
    form_class = SysOptionsForm
    template_name = 'setup/cmnsysoptions-c_tab.html'

    def get_context_data(self, **kwargs):
        data = super(CmnSysOptionsCreateView, self).get_context_data(**kwargs)
        data = add_fields(data)
        return data

    def get_success_url(self):
        return reverse('setup:cmnsysoptionslistview')

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsCreateViewOld(CreateView):
    model = CmnSysOptions
    form_class = SysOptionsForm
    template_name = 'setup/cmnsysoptions-c.html'

    def get_success_url(self):
        return reverse('setup:cmnsysoptionslistview')

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsDetailView(DetailView):
    model = CmnSysOptions
    slug_field = "sys_options_id"
    slug_url_kwarg = "sys_options_id"
    fields = CmnSysOptions.fieldlist()
    template_name = 'setup/cmnsysoptions-d.html'
    context_object_name = 'form'

    def get_success_url(self):
        return reverse('setup:cmnsysoptionslistview')

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsUpdateView(UpdateView):
    model = CmnSysOptions
    slug_field = 'sys_options_id'
    slug_url_kwarg = 'sys_options_id'
    #fields = CmnSysOptions.fieldlist()
    form_class = SysOptionsForm
    template_name = 'setup/cmnsysoptions-c_tab.html'
    #context_object_name = 'form'

    def get_context_data(self, **kwargs):
        data = super(CmnSysOptionsUpdateView, self).get_context_data(**kwargs)
        data = add_fields(data)
        return data

    def get_success_url(self):
        return reverse('setup:cmnsysoptionslistview')

@method_decorator(login_required, name='dispatch')
class CmnSysOptionsDeleteView(DeleteView):
    model = CmnSysOptions
    slug_field = 'sys_options_id'
    slug_url_kwarg = 'sys_options_id'
    template_name = 'setup/cmnsysoptions-d.html'

    def get_success_url(self):
        return reverse('setup:cmnsysoptionslistview')
