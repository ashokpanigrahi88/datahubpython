from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
# specific to this view

from setup.forms.lookup_form import *
from common.models import CmnLookupCodes
APPNAME='setup'
URLPREFIX = '/'+APPNAME+'/lookupcode{0}/'
SLUG_FIELD = 'lookup_code'
SLUG_URL_KWARG = 'lookup_code'
TEMPLATE_PREFIX = 'setup/cmnlookupcodes-{0}.html'
ORDERING = ('clt_lookup_type','lookup_code')
FORM_CLASS = LookupCodeForm
MODEL = CmnLookupCodes
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:lookupcodes_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
        'update': URLPREFIX.format('_update'),
        'delete': URLPREFIX.format('_delete'),
        'list': URLPREFIX.format('s_list'),
        'title' : 'Lookup Codes',
        'findfield' : 'Lookup Code',
             }

@method_decorator(login_required, name='dispatch')
class LookupCodeListView(ListView):
    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(LookupCodeListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        f_type = self.request.GET.get('lookup_type')
        page = self.request.GET.get('page')
        if f_nm is not None:
            rows = rows.filter(lookup_code__icontains=f_nm)
        if f_type is not None:
            rows = rows.filter(clt_lookup_type__lookup_type__startswith=f_type)
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
class LookupCodeCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def get_success_url(self):
        return reverse(REVERSE)

@method_decorator(login_required, name='dispatch')
class LookupCodeDetailView(DetailView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name =  TEMPLATE_PREFIX.format('d')
    context_object_name = 'form'


    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class LookupCodeUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_object(self):
        lookuptype = self.kwargs['lookup_type']
        lookupcode = self.kwargs['lookup_code']
        print('get_object',lookuptype, lookupcode )
        return self.model.objects.get(clt_lookup_type__exact=lookuptype,
                                      lookup_code__exact=lookupcode)

    def form_valid(self, form):
        lookuptype = self.kwargs['lookup_type']
        lookupcode = self.kwargs['lookup_code']
        print('post',lookuptype, lookupcode )
        data = form.save(commit=False)
        #data.clt_lookup_type = lookuptype
        #data.lookup_code = lookupcode
        data.save()
        print('data',data)
        return redirect('/setup/lookupcodes_list/', {'lookup_type':lookuptype})

    def get_success_url(self):
        return reverse(REVERSE)


@method_decorator(login_required, name='dispatch')
class LookupCodeDeleteView(DeleteView):
    model = MODEL
    slug_field =  SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = settings.DELETE_TEMPLATE

    def get_success_url(self):
        return reverse(REVERSE)
