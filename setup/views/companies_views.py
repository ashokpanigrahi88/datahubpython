from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

# specific to this view
from common.sysutil import get_sequenceval
from setup.forms.companies_forms import *
from common.models import CmnCompanies

APPNAME = 'setup'
URLPREFIX = '/' + APPNAME + '/company{0}/'
SLUG_FIELD = 'comp_id'
SLUG_URL_KWARG = 'comp_id'
TEMPLATE_PREFIX = 'setup/cmncompanies-{0}.html'
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
             'findfield': 'Company Name',
             }

# @method_decorator(login_required, name='dispatch')
class CompaniesListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(CompaniesListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        page = self.request.GET.get('page')
        if f_nm is not None:
            set1 = rows.filter(comp_trading_name__icontains=f_nm)
            set2 = rows.filter(comp_name__icontains=f_nm)
            rows = set1|set2
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
    try:
        model = MODEL
        slug_field = SLUG_FIELD
        slug_url_kwarg = SLUG_URL_KWARG
        template_name = TEMPLATE_PREFIX.format('d')

        def get_success_url(self):
            return reverse(REVERSE)
    except:
        pass