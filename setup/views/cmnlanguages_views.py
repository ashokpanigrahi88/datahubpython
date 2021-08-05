from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
# specific to this view

from setup.forms.languages_forms import *
from common.models import CmnLanguages
APPNAME='setup'
URLPREFIX = '/'+APPNAME+'/language{0}/'
SLUG_FIELD = 'language_code'
SLUG_URL_KWARG = 'language_code'
TEMPLATE_PREFIX = 'setup/cmnlanguages-{0}.html'
ORDERING = ('language_code',)
FORM_CLASS = LanguageForm
MODEL = CmnLanguages
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:languages_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
        'update': URLPREFIX.format('_update'),
        'delete': URLPREFIX.format('_delete'),
        'list': URLPREFIX.format('_list'),
        'title' : 'Languages',
        'findfield' : 'Langauge Code',
             }

@method_decorator(login_required, name='dispatch')
class LanguagesFormSetView(FormView):
    form_class = LanguagesFormSet
    template_name = 'common/model_formset.html'
    success_url = reverse_lazy('setup:languages')
#
    def post(self, request, *args, **kwargs):
        formset = LanguagesFormSet(request.POST)
        print('POST - FORMSET - ',formset)
        if formset.is_valid():
            formset.save()
            return self.form_valid(formset)

@method_decorator(login_required, name='dispatch')
class LanguagesListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(LanguagesListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        page = self.request.GET.get('page')
        if f_nm is not None:
            rows = rows.filter(langauage_code_icontains=f_nm)
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
class LanguagesCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def get_success_url(self):
        return reverse(REVERSE)

@method_decorator(login_required, name='dispatch')
class LanguagesDetailView(DetailView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name =  TEMPLATE_PREFIX.format('d')
    context_object_name = 'form'


    def get_success_url(self):
        return reverse(REVERSE)


class LanguagesUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


class LanguagesDeleteView(DeleteView):
    model = MODEL
    slug_field =  SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = settings.DELETE_TEMPLATE

    def get_success_url(self):
        return reverse(REVERSE)
