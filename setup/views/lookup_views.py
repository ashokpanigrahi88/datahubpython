from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# specific to this view

from setup.forms.lookup_form import *
from common.models import CmnLookupTypes


APPNAME='setup'
URLPREFIX = '/'+APPNAME+'/lookup{0}/'
SLUG_FIELD = 'lookup_type'
SLUG_URL_KWARG = SLUG_FIELD
TEMPLATE_PREFIX = 'setup/cmnlookuptypes-{0}.html'
ORDERING = ('lookup_type')
FORM_CLASS = LookupForm
MODEL = CmnLookupTypes
REC_IN_PAGE = settings.PUB_PAGE_LINES
REVERSE = "setup:lookup_list"
MYCONTEXT = {'create': URLPREFIX.format('_create'),
        'update': URLPREFIX.format('_update'),
        'delete': URLPREFIX.format('_delete'),
        'list': URLPREFIX.format('_list'),
        'title' : 'Lookup Types',
        'findfield' : 'Lookup Type',
             }

# @method_decorator(login_required, name='dispatch')
class CmnLookupTypesListView(ListView):

    model = MODEL
    template_name = TEMPLATE_PREFIX.format('l')
    context_object_name = 'data'
    ordering = ORDERING
    paginate_by = REC_IN_PAGE

    def get_context_data(self, **kwargs):
        context = super(CmnLookupTypesListView, self).get_context_data(**kwargs)
        rows = self.get_queryset()
        f_nm = self.request.GET.get('nm')
        page = self.request.GET.get('page')
        if f_nm is not None:
            rows = rows.filter(lookup_type__icontains=f_nm)
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


class CmnLookupTypesCreateView(CreateView):
    model = MODEL
    form_class = FORM_CLASS
    template_name = TEMPLATE_PREFIX.format('c')

    def get_success_url(self):
        return reverse(REVERSE)


class CmnLookupTypesDetailView(DetailView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = TEMPLATE_PREFIX.format('d')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


class CmnLookupTypesUpdateView(UpdateView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    #fields = CmnLookupTypes.fieldlist()
    form_class = FORM_CLASS
    template_name =  TEMPLATE_PREFIX.format('u')
    context_object_name = 'form'

    def get_success_url(self):
        return reverse(REVERSE)


class CmnLookupTypesDeleteView(DeleteView):
    model = MODEL
    slug_field = SLUG_FIELD
    slug_url_kwarg = SLUG_URL_KWARG
    template_name = '/common/confirm_delete.html'

    def get_success_url(self):
        return reverse(REVERSE)
